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

        # 1. mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2. mark the cell as safe
        self.mark_safe(cell)
        # 3. add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # Loop over all cells within one row and column
        if Sentence([cell], 0) not in self.knowledge:
            self.knowledge.append(Sentence([cell], 0))
        surr_cells = []
        new_count = int(count)
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # If we already know about the cell, take it out the sentence's cells
                if (i, j) in self.mines:
                    new_count -= 1
                    continue
                elif (i, j) in self.safes:
                    continue
                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    surr_cells.append((i, j))
        self.knowledge.append(Sentence(surr_cells, new_count))

        (curr_kb, new_kb) = (0,1)
        while curr_kb != new_kb:
            curr_kb = list(self.knowledge)

            # 4. Check if any sentences make anything known
            for sent in list(self.knowledge):
                if sent.known_mines():
                    for mine in list(sent.cells):
                        if mine not in self.mines:
                            self.mark_mine(mine)
                            self.knowledge.append(Sentence([mine], 1))
                elif sent.known_safes():
                    for safe in list(sent.cells):
                        if safe not in self.safes:
                            self.mark_safe(safe)
                            self.knowledge.append(Sentence([safe], 0))

            # 5. Check if any inferences can be made from sentences with overlapping cell sets
            pairs_explored = []
            for sentence_0 in list(self.knowledge):
                for sentence_1 in list(self.knowledge):
                    if sentence_0 != sentence_1 and (sentence_0,sentence_1) not in pairs_explored and (sentence_1,sentence_0) not in pairs_explored:
                        pairs_explored.append((sentence_0,sentence_1))
                        new_sentence = subset_check(sentence_0, sentence_1)
                        if new_sentence.cells != set():
                            if new_sentence not in self.knowledge:
                                self.knowledge.append(new_sentence)

            # Remove sentences with empty cells set from knowledge base
            clean_kb = [i for i in self.knowledge if i.cells != set()]
            # Remove duplicate sentences from kb
            no_dupe_kb = []
            for sent in clean_kb:
                if sent not in no_dupe_kb:
                    no_dupe_kb.append(sent)
            self.knowledge = no_dupe_kb
            new_kb = list(self.knowledge)

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
            return poss_moves[0]
        else:
            return None


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves = [(i,j) for i in range(0,self.height) for j in range(0,self.width)]
        poss_moves = [move for move in moves if move not in self.moves_made and move not in self.mines]
        if poss_moves:
            return poss_moves[random.randrange(len(poss_moves))]
        else:
            return None

# HELPER FUNCTIONS

def subset_check(sen1, sen2):
    subset_cells = set()
    if sen1.cells in sen2.cells:
        subset_cells = set(i for i in sen2.cells if i not in sen1.cells)
    elif sen2.cells in sen1.cells:
        subset_cells = set(i for i in sen1.cells if i not in sen2.cells)
    subset_count = abs(sen1.count - sen2.count)
    return Sentence(subset_cells, subset_count)

