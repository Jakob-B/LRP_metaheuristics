import abc

import metaheuristik.quinteroaraujo.code.cws_custom.node as Node

class Edge (abc.ABC):
    """
    The class that inherits from this one
    inherits all the attributes and methods
    needed to work as an Edge of the graph
    on which the Clarke Wright Savings heuristic
    is going to be computed.

    """
    def __init__(self, origin, dest, saving, cost = 0):
        """
        Initialise.

        :param origin: The node of origin.
        :param dest: The node of destination.
        :param saving: The saving value associated to this edge.
        :param cost: The cost associated to this edge.

        :attr inverse: The inverse edge.
        """
        self.origin: Node = origin    # node/customer or facility
        self.dest: Node = dest        # node/customer or facility
        self.saving = saving
        self.cost = cost
        self.inverse = None

    def __repr__(self):
        return f"({self.origin} -> {self.dest})"
