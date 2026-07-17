import itertools
import random

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.cells:
            return self.cells
        return None
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0 and self.cells:
            return self.cells
        return None    


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Input args are the cell that was just made as a move
        # And how many adjacent cells to that move are mines

        # 1. mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2. mark the cell as safe
        self.mark_safe(cell)
        # 3. add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # Loop over all cells within one row and column
        surr_cells = set()
        new_count = int(count)
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # If we already know about the cell, take it out the sentence's cells
                if (i, j) in self.mines:
                    count -= 1
                    continue
                elif (i, j) in self.safes:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    surr_cells.add((i, j))
        self.knowledge.append(Sentence(surr_cells, count))
        # 4a. mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        # 4b. Use sum of knowledge in knowledge base to check if KB entails any cells being mines
        # entailment = True
        # while entailment is True:
        #     entailment = False
        #     cells_checked = set()
        #     for sentence in self.knowledge:
        #         # If the sentence tells us explicitly which cells are safe/mines, add that knowledge first
        #         if sentence.known_mines:
        #             for mine_cell in sentence.cells:


        #         for new_cell in sentence.cells:
        #             if new_cell not in cells_checked:
        #                 mine_entailment = check_all(self.knowledge, new_cell, True, sentence.cells, {})
        #                 safe_entailment = check_all(self.knowledge, new_cell, False, sentence.cells, {})
        #                 if mine_entailment == True or safe_entailment == True:
        #                     entailment = True
        #             if mine_entailment:
        #                 self.mark_mine(new_cell)
        #             elif safe_entailment:
        #                 self.mark_safe(new_cell)

        (known, entailment, new_info) = (True, True, True)
        curr_kb = list(self.knowledge)
        while (known or entailment or new_info) and curr_kb:

            # Check if any sentences make anything known
            known = False
            for sent in curr_kb:
                if sent.known_mines():
                    known = True
                    for mine in list(sent.cells):
                        self.mark_mine(mine)
                elif sent.known_safes():
                    known = True
                    for safes in list(sent.cells):
                        self.mark_safe(safes)
            
            # new_kb = []
            # # Check if any sentences empty and removes from curr_kb
            # for new_sent in curr_kb:
            #     if new_sent.cells != set():
            #         new_kb.append(new_sent)
            # curr_kb = new_kb

            # # Checks for any entailment
            # cells_checked = set()
            # for sentence in curr_kb:

            #     for new_cell in sentence.cells:

            #         if new_cell not in cells_checked:
            #             cells_checked.add(new_cell)
            #             mine_entailment = check_all(self.knowledge, new_cell, True, sentence.cells, {})
            #             safe_entailment = check_all(self.knowledge, new_cell, False, sentence.cells, {})
            #             if mine_entailment == True or safe_entailment == True:
            #                 entailment = True
            #         if mine_entailment:
            #             self.mark_mine(new_cell)
            #         elif safe_entailment:
            #             self.mark_safe(new_cell)

            new_kb = []
            # Check if any sentences empty and removes from curr_kb
            for new_sent in curr_kb:
                if new_sent.cells != set():
                    new_kb.append(new_sent)
            curr_kb = new_kb

            # Check if any inferences can be made from sentences with overlapping cell sets
            new_info = False
            pairs_explored = set()
            new_knowledge_list = []
            for sentence_0 in curr_kb:
                for sentence_1 in curr_kb:
                    if sentence_0 != sentence_1 and (sentence_0,sentence_1) not in pairs_explored and (sentence_1,sentence_0) not in pairs_explored:
                        new_sentence = subset_check(sentence_0, sentence_1)
                        if new_sentence:
                            new_knowledge_list.append(new_sentence)
                            new_info = True
            curr_kb += new_knowledge_list



        print(self.knowledge[0])
        for sent in curr_kb:
            print(sent)
        
        print(self.safes)
        print(self.mines)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        poss_moves = [move for move in self.safes if move not in self.moves_made]
        if poss_moves:
            print("ER")
            return poss_moves[0]
            
        else:
            print("None")
            return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves = [(i,j) for i in range(0,self.height) for j in range(0,self.width)]
        print(moves)
        poss_moves = [move for move in moves if move not in self.moves_made and move not in self.mines]
        print(poss_moves)
        print(len(poss_moves))
        print(random.randrange(len(poss_moves)))
        rand_move = poss_moves[random.randrange(len(poss_moves))]
        return rand_move

# HELPER FUNCTIONS

def check_all(knowledge, query_cell, mine_check, cells, model):

    # If model has an assignment for each symbol
    # (The logic below might be a little confusing: we start with a list of symbols. The function is recursive, and every time it calls itself it pops one symbol from the symbols list and generates models from it. Thus, when the symbols list is empty, we know that we finished generating models with every possible truth assignment of symbols.)
    if not cells:

        # If knowledge base is true in model, then query must also be true
        if KB_evaluate(knowledge, model):
            return query_evaluate(query_cell, mine_check, model)
        return True
    else:

        # Choose one of the remaining unused cells
        remaining = cells.copy()
        p = remaining.pop()

        # Create a model where the symbol is true
        model_true = model.copy()
        model_true[p] = True

        # Create a model where the symbol is false
        model_false = model.copy()
        model_false[p] = False

        # Ensure entailment holds in both models
        return(check_all(knowledge, query_cell, mine_check, remaining, model_true) and check_all(knowledge, query_cell, mine_check, remaining, model_false))
    

def KB_evaluate(knowledge_base, model):
    # If knowledge base is true in the model, return True, otherwise False
    eval = True
    for sentence in knowledge_base:
        count = 0
        for cell in sentence.cells:
            if model[cell] is True:
                count += 1
        if sentence.count != count:
            return False
    return True


def query_evaluate(cell, mine_check, model):
    if model[cell] == mine_check:
        return True
    return False

def subset_check(sen1, sen2):
    subset_cells = sen1.cells & sen2.cells
    subset_count = abs(sen1.count - sen2.count)
    return Sentence(subset_cells, subset_count)


# TROUBLEHOOTING:

# test_move = (1,1)
# test_AI = MinesweeperAI()
# test_AI.add_knowledge(test_move,0)

# 1,2,3 in add_knowledge are working