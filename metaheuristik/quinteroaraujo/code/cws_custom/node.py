import abc


class Node (abc.ABC):
    """
    The class that inherits from this one
    inherits all the attributes and methods
    needed to work as an Node of the graph
    on which the Clarke Wright Savings heuristic
    is going to be computed.
    """
    def __init__(self, id, dn_edge, nd_edge, demand = 0):
        """
        Initialise.

        :param id: The unique id of the node. (NOTE: There is no control
                  on the unicity of this id)
        :param demand: The demand of the node. Default is 0.
        """
        self.id = id
        self.demand = demand

    def __repr__(self):
        return str(self.id)
