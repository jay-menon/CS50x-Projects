import sys

from crossword import *

class Layer():
    def __init__(self, assignment, var, var_list, var_idx):
        self.assignment = assignment
        self.var = var
        self.var_list = var_list
        self.var_idx = var_idx


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # 5
        # Iterates through list of variables, checking each variable's domain satisfies unary constraints
        new_dict = {var:set(self.domains[var]) for var in dict(self.domains)}
        for var in self.domains:
            for word in self.domains[var]:
                if var.length != len(word):
                    new_dict[var].remove(word)
        self.domains = new_dict

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # 6
        # Check if they are even neighbours:
        if y in self.crossword.neighbors(x):
            # If they are, add any words that conflict with x to remove_set
            (i, j) = self.crossword.overlaps[x, y]
            remove_set = set()
            for x_word in self.domains[x]:
                remove_word = True
                for y_word in self.domains[y]:
                    if x_word[i] == y_word[j]:
                        remove_word = False
                if remove_word:
                    remove_set.add(x_word)
            # If there are words in remove_set, remove them and return True
            if remove_set:
                self.domains[x] = self.domains[x] - remove_set
                return True
            else:
                # If no words need to be removed from y domain, return False
                return False
        else:
            # If not neighbours, no change will be made so return False
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # 7
        # Iterates through list of variables, checking each variable's (x) neighbours (y)
        # Use revise on every pair to make sure x is consistent with y for each pair
        # Must KEEP iterating until either at least one domain empty (infeasible solution) OR no further domain change
        if arcs:
            arcs_list = arcs
        else:
            arcs_list = list(set((x,y) for x in self.crossword.variables for y in self.crossword.variables if x != y))
        revision_made = True
        while revision_made:
            revision_made = False
            for arc in arcs_list:
                (x, y) = arc
                revision_made = self.revise(x, y)
            for var in self.domains:
                if self.domains[var] == set():
                    return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # 1
        for var in assignment:
            if not assignment[var]:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # 2
        words_implemented = set()
        for var0 in assignment:
            # Ensures all diff words used
            if assignment[var0] in words_implemented:
                return False
            else:
                words_implemented.add(assignment[var0])
            # Ensures assignment fits length constraint
            if var0.length != len(assignment[var0]):
                return False
            # Ensures all neighbours are non-conflicting
            for var1 in self.crossword.neighbors(var0):
                (i, j) = self.crossword.overlaps[var0, var1]
                if var1 in assignment:
                    if assignment[var0][i] != assignment[var1][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # 3
        # Orders domain of variable, putting value that constricts neighbours domain MOST, as first
        # Used to implement Minimum Remaining Values (MRV) heuristic

        # self.domains is currently a dict with each var as a key and EVERY word possible as def
        words_set = self.domains[var]
        all_neighbours_set = self.crossword.neighbors(var)
        assigned_neighbours_set = set(assignment)
        unassigned_neighbours_set = all_neighbours_set - assigned_neighbours_set
        ruleout_dict = {word:0 for word in words_set}
        for word in words_set:
            for neighbour in unassigned_neighbours_set:
                for neighbour_word in self.domains[neighbour]:
                    if not self.consistent({var:word, neighbour:neighbour_word}):
                        ruleout_dict[word] += 1
        # ruleout_dict should now contain a dict of how many ruleouts each word causes
        word_ruleout_list = [(word, ruleout_dict[word]) for word in ruleout_dict]
        word_ruleout_list.sort(key=lambda x: x[1])
        return [pair[0] for pair in word_ruleout_list]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # 4
        # Implement MRV and Degrees Heuristic to select next unassigned variable for backtrack algorithm
        unassigned_vars = self.crossword.variables - set(assignment)
        curr_var = next(iter(unassigned_vars))
        curr_dom_length = len(self.domains[curr_var])
        for var in unassigned_vars:
            if len(self.domains[var]) < curr_dom_length:
                curr_var = var
                curr_dom_length = len(self.domains[var])
            elif len(self.domains[var]) == curr_dom_length:
                # Check degrees
                if len(self.crossword.neighbors(var)) >= len(self.crossword.neighbors(curr_var)):
                    curr_var = var
        return curr_var

    def layer_list_incrementor(layer_list):
        # Layer(assignment,var,var_list,var_idx)
        new_layer_list = []
        inc_layer = False
        for layer in layer_list:
            if layer.var_idx + 1 == len(layer.var_list):
                continue
            elif layer.var_idx + 1 < len(layer.var_list) and inc_layer is False:
                new_layer_list.append(Layer(layer.assignment, layer.var, layer.var_list, layer.var_idx + 1))
                inc_layer = True
                continue
            else:
                print("ERROR, SOMETHING WENT CRAZY")
            
            if inc_layer is True:
                new_layer_list.append(layer)
        return new_layer_list

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # 8
        # Implements the actual BACKTRACKING aspect to return a completed assignment from a partial one
        consistent = False
        complete = False

        curr_var = self.select_unassigned_variable(assignment)
        curr_var_list = self.order_domain_values(curr_var, assignment)
        layer_list = [Layer(assignment, curr_var, curr_var_list, 0)]
        curr_assignment = assignment

        failed_assignments = set()
        while not (consistent and complete):
            curr_layer = layer_list[-1]
            
            if not self.consistent(curr_layer.assignment):
                failed_assignments.add(curr_assignment)
                layer_list = self.layer_list_incrementor(layer_list)
                if layer_list == []:
                    return None
                raise NotImplementedError
            
            elif not self.assignment_complete(curr_layer.assignment):

                new_assignment = dict(curr_layer.assignment)
                new_assignment[curr_layer.var] = curr_layer.var_list[curr_layer.var_idx]
                next_var = self.select_unassigned_variable(new_assignment)
                next_var_list = self.order_domain_values(next_var, new_assignment)
                new_layer = Layer(new_assignment, next_var, next_var_list, 0)
                layer_list.insert(new_layer, 0)
                raise NotImplementedError
            else:
                return curr_layer.assignment


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
