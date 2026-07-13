"""
Tic Tac Toe Player
"""

from util import Node, QueueFrontier

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
    if (XO_dict[X] + XO_dict[O])%2 == 0:
        return X
    return O


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


def sym_simplifier(board):
    """
    Returns only actions that are not mathematically equivalent to any other actions from the list of all possible actions.
    Can be used as a faster alternative to the actions(board) function.
    """
    # If the board is symmetrical along an axis, one action of a symmetric pair is added to degen_actions
    degen_actions = set()
    # horz sym line
    if [board[0][0],board[0][1],board[0][2]] == [board[-1][0],board[-1][1],board[-1][2]]:
        degen_actions.update([(0,0),(0,1),(0,2)])
    # vert sym line
    if [board[0][0],board[1][0],board[2][0]] == [board[0][-1],board[1][-1],board[2][-1]]:
        degen_actions.update([(0,0),(1,0),(2,0)])
    # y=x sym line
    if [board[0][1],board[0][0],board[1][0]] == [board[-1][1],board[-1][-1],board[1][-1]]:
        degen_actions.update([(0,1),(0,0),(1,0)])
    # y=-x sym line
    if [board[1][0],board[2][0],board[2][1]] == [board[0][1],board[0][2],board[1][2]]:
        degen_actions.update([(1,0),(2,0),(2,1)])
    # Returns the list of all possible actions without any of the degenerate actions
    new_actions = set()
    for action in actions(board):
        if action not in degen_actions:
            new_actions.add(action)
    return new_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    curr_player = player(board)
    board_copy = [list(i) for i in list(board)]
    if board_copy[i][j] != EMPTY:
        raise ValueError("Illegal move")
    elif i < 0 or i > 2 or j < 0 or i > 2:
        raise ValueError("Out of bounds move")
    board_copy[i][j] = curr_player
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Constructs lists of each row, column and diagonal on the board
    rows_list = board
    cols_list = [[],[],[]]
    diag_TLBR = []
    diag_TRBL = []
    for i in range(0,3):
        for j in range(0,3):
            cols_list[j].append(board[i][j])
        diag_TLBR.append(board[i][i])
        diag_TRBL.append(board[i][2-i])
    # Checks if any of the lists meet the winning criteria (3 in a row) and returns winner
    threes_list = rows_list + cols_list + [diag_TRBL, diag_TLBR]
    for three in threes_list:
        if three.count(X) == 3:
            return X
        elif three.count(O) ==3:
            return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    XO_dict = count_XO(board)
    if winner(board) is not None:
        return True
    elif XO_dict[X] + XO_dict[O] == 9:
        return True
    else:
        return False


def count_XO(board):
    """
    Returns dictionary specifying number of Xs and Os currently on the board.
    """
    XO_dict = {X:0, O:0}
    for row in board:
        XO_dict[X] += row.count(X)
        XO_dict[O] += row.count(O)
    return XO_dict


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Returns none if board is already in a terminal state
    if terminal(board) is True:
        return None
    # Maps out the complete game state node tree from the current board, recording all terminal nodes and each node's daughter nodes:
    terminal_nodes = set()
    initial_nodes = set()
    node_daughter_dict = {}
    for action in sym_simplifier(board):
        # Initialise the search with initial node and frontier
        initial_node = Node(result(board, action),None,action)
        initial_nodes.add(initial_node)
        frontier = QueueFrontier()
        frontier.add(initial_node)
        # Iterate through all nodes until every terminal state has been evaluated and so frontier is empty
        while frontier.empty() is False:
            curr_node = frontier.remove()
            node_daughter_dict[curr_node] = set()

            # When a terminal node is reached, add to terminal_nodes set
            if terminal(curr_node.state) is True:
                terminal_nodes.add(curr_node)
            # If node is not terminal, find its daughter nodes from the next possible actions and record this in node_daughter_dict
            else:
                poss_actions = sym_simplifier(curr_node.state)
                for poss_action in poss_actions:
                    daughter_node = Node(result(curr_node.state,poss_action), curr_node, poss_action)
                    frontier.add(daughter_node)
                    node_daughter_dict[curr_node].add(daughter_node)

    # Find the value of every node from the val_dict_writer function
    val_dict = val_dict_writer(terminal_nodes, node_daughter_dict)

    # Find the value of each immediate action possible and store in curr_action_dict
    curr_action_dict = {}
    for initial_node in initial_nodes:
        action_utility = val_dict[initial_node]
        curr_action_dict[initial_node.action] = action_utility

    # Return the utility maximising action for X or the minimising action for O
    curr_player = player(board)
    if curr_player == X:
        incumbent = -2
        best_action = None
        for action in curr_action_dict:
            if curr_action_dict[action] > incumbent:
                best_action = action
                incumbent = curr_action_dict[action]
    else:
        incumbent = 2
        best_action = None
        for action in curr_action_dict:
            if curr_action_dict[action] < incumbent:
                best_action = action
                incumbent = curr_action_dict[action]
    return best_action


def val_dict_writer(terminal_nodes, node_daughter_dict):
    """
    Returns a dictionary containing every node with their respective utility.
    """
    # node_daughter_dict = {node0:{set of node0's daughter nodes}, ...}
    # curr_terminal_nodes_dict = {term_node0: val0, term_node1: val1, ...}
    curr_terminal_nodes_dict = {terminal_node: utility(terminal_node.state) for terminal_node in terminal_nodes} 
    nodes_val_dict = dict(curr_terminal_nodes_dict)
    # Loop runs until nodes_val_dict has utility values for every node that appears in node_daughter_dict
    while len(nodes_val_dict) != len(node_daughter_dict):
        # For each node in curr_terminal_nodes_dict, replaces every instance of that node as a value in node_daughter_dict with its utility
        for terminal_node in curr_terminal_nodes_dict:
            val = curr_terminal_nodes_dict[terminal_node]
            parent = terminal_node.parent
            if type(parent) == Node:
                node_daughter_dict[parent].remove(terminal_node)
                node_daughter_dict[parent].add(val)
            else:
                pass
        # Finds all nodes in node_daughter_dict with only utilities in their definition, then
        # replaces the list of utilities with the node's final utility and adds info to nodes_val_dict
        new_terminal_nodes_dict = {}
        for node in node_daughter_dict:
            if term_node_checker(node_daughter_dict[node]) is True and node not in nodes_val_dict:
                val = val_finder(node, node_daughter_dict[node])
                nodes_val_dict[node] = val
                new_terminal_nodes_dict[node] = val
        curr_terminal_nodes_dict = new_terminal_nodes_dict
    return nodes_val_dict


def val_finder(node, val_list):
    """
    Returns a node's utility from an input of its daughter nodes' utilities.
    """
    if player(node.state) == X:
        return max(val_list)
    else:
        return min(val_list)
    

def term_node_checker(node_def):
    """
    Returns True if a node is a terminal node and False otherwise.
    """
    for val in node_def:
        if type(val) == Node:
            return False
    return True
