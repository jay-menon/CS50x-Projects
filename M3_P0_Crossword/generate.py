import sys

from crossword import *

class Layer():

    def __init__(self, assignment, var, var_list, var_idx, num, domains):
        """
        Creates a new 'Layer' which represents the fixing of a variable to value in its domain to create
        an updated variable-value assignment.
        """
        # self.assignment stores the updated variable-value assignment
        self.assignment = assignment
        # self.var stores the variable that has been fixed
        self.var = var
        # self.var_list stores the potential values that the variable could take in list form
        self.var_list = var_list
        # self.var_idx stores the index of the value in self.var_list that the variable has been fixed to
        self.var_idx = var_idx
        # self.num stores the layer's number: i.e. the nth layer is on top of n-1 layers and so n-1 variables were fixed before this one
        self.num = num
        # self.domains stores the state of all the variables' domains BEFORE the assignment is made
        self.domains = domains

    def __str__(self):
        return f"Layer Num: {self.num}, Var_idx: {self.var_idx} || {self.assignment}"

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
        # Iterates through list of variables, checking each variable's domain satisfies unary constraints (word length)
        new_dict = {var: set(self.domains[var]) for var in dict(self.domains)}
        for var in self.domains:
            for word in self.domains[var]:
                if var.length != len(word):
                    new_dict[var].remove(word)
        
        # Updates self.domains
        self.domains = new_dict

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Check if x and y are neighbours
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

            # If there are words in remove_set, remove them from x's domain and return True
            if remove_set:
                self.domains[x] = self.domains[x] - remove_set
                return True
            else:
                # If no words need to be removed from y domain, return False
                return False
        else:
            # If x and y not neighbours, no change will be made so return False
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs input has been specified, consider the input only, but otherwise, consider all arcs
        if arcs is not None:
            arcs_list = arcs
        else:
            arcs_list = set((x, y) for x in self.crossword.variables for y in self.crossword.variables if x != y)
        
        # Loop iterates until problem becomes infeasible or no further domain change is observed
        revision_made = True
        while revision_made:
            revision_made = False

            # Evaluates each arc, noting if one of the variable's domains was constricted
            for arc in arcs_list:
                (x, y) = arc
                revision = self.revise(x, y)
                if revision:
                    revision_made = True
            
            # Automatically returns False if any domain is left empty by enforcing arc consistency
            for var in self.domains:
                if self.domains[var] == set():
                    return False
    
        # Returns True if no further domain constriction can occur and every domain is non-empty
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if assignment includes all variables
        if self.crossword.variables - set(assignment) != set():
            return False
        
        # If it does, make sure all variables have actual values assigned to them
        for var in assignment:
            if not assignment[var]:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Iterates through each variable in assignment, checking if their assigned value violates any constraints
        words_implemented = set()
        for var0 in assignment:
    
            # Ensures all diff words used and that it is an actual word that has been assigned
            if assignment[var0] in words_implemented or not assignment[var0]:
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
        # Construct set of all neighbouring variables that are unassigned in the input assignment
        all_neighbours_set = self.crossword.neighbors(var)
        assigned_neighbours_set = set(assignment)
        unassigned_neighbours_set = all_neighbours_set - assigned_neighbours_set

        # Initialise ruleout_dict to track how many values each word rules out in the unassigned neighbours' domains
        words_set = self.domains[var]
        ruleout_dict = {word: 0 for word in words_set}

        # Iterate through each word in the input variable's domain, noting how many neighbouring values it rules out
        for word in words_set:
            for neighbour in unassigned_neighbours_set:
                for neighbour_word in self.domains[neighbour]:
                    if not self.consistent({var: word, neighbour: neighbour_word}):
                        ruleout_dict[word] += 1
        
        # ruleout_dict should now contain a dict of how many ruleouts each word causes
        # Return the input variable's domain in list form, ordered from least constraining to most
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
        # Construct set of all the variables left unassigned in the input assignment
        unassigned_vars = self.crossword.variables - set(assignment)

        # Select a random initial variable from the set and note the size of its domain
        best_var = next(iter(unassigned_vars))
        curr_dom_length = len(self.domains[best_var])

        # Iterates through unassigned_vars, updating best_var if a more favourable variable found
        for var in unassigned_vars:
            
            # If the variable has a smaller domain than the incumbent, update best_variable
            if len(self.domains[var]) < curr_dom_length:
                best_var = var
                curr_dom_length = len(self.domains[var])

            # If the domains are the same size, check the degrees of each variable
            elif len(self.domains[var]) == curr_dom_length:
                # Whichever variable has more neighbours is the incumbent (if a draw, choose either)
                if len(self.crossword.neighbors(var)) >= len(self.crossword.neighbors(best_var)):
                    best_var = var

        return best_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Initialise the search
        force_bt = False
        consistent_complete = False
        layer_list = [Layer(assignment, None, None, 0, 0, domains_deepcopy(self.domains))]

        # Iterates until either a consistent and complete assignment is found OR problem is deemed infeasible
        while not consistent_complete:
            
            # Select uppermost layer in layer_list
            curr_layer = layer_list[0]

            # Enforce arc consistency on that layer's domains
            self.domains = domains_deepcopy(curr_layer.domains)
            self.ac3()
        
            # Checks if assignment has all variables assigned to actual words and words fit constraints
            if not self.consistent(curr_layer.assignment) or force_bt is True:
                force_bt = False
                # If assignment is inconsistent, layer_list is backtracked by one stage
                layer_list = layer_list_incrementor(layer_list)
                # If backtrack ever results in empty layer_list, problem is infeasible and function returns None
                if layer_list == []:
                    return None
            
            # If assignment is consistent, check if it is complete
            elif not self.assignment_complete(curr_layer.assignment):
                
                # If not complete, find next variable to fix and fix it for the next layer
                curr_var = self.select_unassigned_variable(curr_layer.assignment)
                curr_var_list = self.order_domain_values(curr_var, curr_layer.assignment)

                # If var_list is empty, force a backtrack
                if curr_var_list == []:
                    force_bt = True
                    continue
                
                # If var_list not empty, define the next layer and add to layer_list
                new_assignment = dict(curr_layer.assignment)
                new_assignment[curr_var] = curr_var_list[0]
                new_layer = Layer(new_assignment, curr_var, curr_var_list, 0, curr_layer.num + 1, domains_deepcopy(self.domains))
                layer_list.insert(0, new_layer)

            # Assignment reaches here only if it is both consistent AND complete, thus breaking the loop
            else:
                consistent_complete = True

        return curr_layer.assignment


# HELPER FUNCTIONS:

def layer_list_incrementor(layer_list):
    '''
    Returns a layer list that has been backtracked by one stage relative to the input layer list.
    If impossible to backtrack any further, returns [].
    '''
    # Initialise new_layer_list
    new_layer_list = []
    backtrack_layer = False
    for layer in layer_list:

        # If the current layer's variable domain is empty, consider the next layer instead
        if not layer.var_list:
            continue

        # If the current layer's variable domain has been fully explored, consider the next layer instead
        if layer.var_idx + 1 == len(layer.var_list):
            continue

        # If the current layer is the first layer who's variable domain hasn't been fully explored, that is the backtrack layer
        elif layer.var_idx + 1 < len(layer.var_list) and backtrack_layer is False:
            # Update the layer's assignment to include the new domain value and add the new layer to new_layer_list
            backtrack_layer = True
            new_assignment = layer.assignment
            new_assignment[layer.var] = layer.var_list[layer.var_idx + 1]
            new_layer_list.append(Layer(new_assignment, layer.var, layer.var_list, layer.var_idx + 1, layer.num, layer.domains))
            continue     

        # Add all layers after the backtrack layer to new_layer_list, unaltered
        if backtrack_layer is True:
            new_layer_list.append(layer)

    return new_layer_list

def domains_deepcopy(domains):
    '''
    Returns a deep copy of the input domains dictionary.
    '''
    domains_copy = dict(domains)
    return {val: set(domains_copy[val]) for val in domains_copy}

def domain_constrictor(domains, assignment):
    '''
    Updates domains dictionary, constricting the domain of variables from assignment
    to their respective value in the assignment dictionary.
    '''
    for var in assignment:
        domains[var] = set(assignment[var])


# MAIN FUNCTION

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
