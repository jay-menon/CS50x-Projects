"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    XO_dict = count_XO(board)
    if (XO_dict["X"] + XO_dict["O"])%2 == 0:
        return "X"
    else:
        return "O"
    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    poss_actions = set()
    for i in range(0,3):
        for j in range(0,3):
            if board[i][j] == EMPTY:
                poss_actions.add((i,j))
    return poss_actions
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    curr_player = player(board)
    board[action[0]][action[1]] = curr_player
    return board
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    rows_list = board
    cols_list = [[],[],[]]
    diag_TLBR = []
    diag_TRBL = []
    for i in range(0,3):
        for j in range(0,3):
            cols_list[j].append(board[i][j])
        diag_TLBR.append(board[i][i])
        diag_TRBL.append(board[i][2-i])
    threes_list = rows_list + cols_list + [diag_TRBL, diag_TLBR]
    for three in threes_list:
        if three.count("X") == 3:
            return "X"
        elif three.count("O") ==3:
            return "O"
    return None
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    XO_dict = count_XO(board)
    if winner(board) != None:
        return True
    elif XO_dict["X"] + XO_dict["O"] == 9:
        return True
    else:
        return False
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0
    raise NotImplementedError

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    poss_actions = actions(board)
    for thing in poss_actions:
        return thing
    raise NotImplementedError

def count_XO(board):
    XO_dict = {"X":0, "O":0}
    for row in board:
        XO_dict["X"] += row.count("X")
        XO_dict["O"] += row.count("O")
    return XO_dict


# Mistakes made:
# 1. {None} Creates a None item in the dictionary, not an empty dictionary
# 2. .add() is method for SETS, not dictionaries
# 3. {} creates an empty dictionary, NOT an empty set: set created by set()
# 4. Sets and dictionaries are NOT indexable as they are UNORDERED collections (uses hashes)