# Defines node class and constructor methods for state/parent/action
class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

# Defines a STACK frontier (last in,first out or depth-first)
class StackFrontier():
    # Constructor method defining the initial froniter as empty list
    def __init__(self):
        self.frontier = []

    # Defines "add" method - simply appends node to frontier list
    def add(self, node):
        self.frontier.append(node)

    # Checks if the current frontier contains nodes with the input state
    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    # Checks if the current frontier is empty (True means empty)
    def empty(self):
        return len(self.frontier) == 0

    # Depth-first node removal from frontier
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

# Breadth-first node removal from frontier
# This class definition of the Queue Frontier enables it to inherit all
# other methods from Stack Frontier, changing only the remove method
class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
