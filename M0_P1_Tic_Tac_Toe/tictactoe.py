"""
Tic Tac Toe Player
"""

import math
from util import Node, StackFrontier, QueueFrontier

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
    board_copy = [list(i) for i in list(board)]
    board_copy[action[0]][action[1]] = curr_player
    return board_copy
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
    curr_player = player(board)
    action_util_dict = {key:[] for key in actions(board)}
    #print(actions(board))
    board_copy = list(board)
    action_num = 0
    for action in actions(board):
        action_num += 1
        #print(action_num)
        # Initialise the search with initial node and frontier
        initial_node = Node(result(board, action),board,action)
        frontier = QueueFrontier()
        frontier.add(initial_node)
        # Iterate through all nodes until terminal condition met, store terminal nodes in set
        # Also stores the utility of each node in node_dict
        num = 0
        while frontier.empty() is False:
            curr_node = frontier.remove()
            num += 1
            if terminal(curr_node.state) is True:
                action_util_dict[action].append(utility(curr_node.state))
            else:
                poss_actions = actions(curr_node.state)
                poss_added = 0
                for poss_action in poss_actions:
                    frontier.add(Node(result(curr_node.state,poss_action), curr_node, poss_action))
                    poss_added += 1
                    #print(poss_added)
        #print(num)
    print(action_util_dict)
    return (0,0)
# Minimax node tree troubleshoot
# - actions(board) does indded give all available actions
# - on the first action iteration, the initial board is correct
# - (NOW FIXED) it appears the frontier has not been clearing after each iteration on the for loop
# - Terminal states outputted appear to be accurate
# - Node tree part appears to have been fixed

    if curr_player == "X":
        action_min_util_dict = {action:min(action_util_dict[action]) for action in action_util_dict}
        incumbent = -2
        best_action = None
        for action in action_min_util_dict:
            if action_min_util_dict[action] > incumbent:
                best_action = action
                incumbent = action_min_util_dict[action]
    else:
        action_max_util_dict = {action:max(action_util_dict[action]) for action in action_util_dict}
        incumbent = 2
        best_action = None
        for action in action_max_util_dict:
            if action_max_util_dict[action] < incumbent:
                best_action = action
                incumbent = action_max_util_dict[action]       
    return best_action




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
# When writing node tree
# 1. When importing classes from diff file, need to use:
#   from util import Node, StackFrontier, QueueFrontier

# Learnt:
# 1. The multiline comment below the function def gets attached to the function as its explanation
# 2. list() only makes a copy of the OUTER list meaning for nested lists, the lists inside your shallow copy
#       are still linked to the original copy and changing those also changes the original!!

# Extras to include:
# - Use symmetry to reduce early computatiom
# - Alpha beta pruning