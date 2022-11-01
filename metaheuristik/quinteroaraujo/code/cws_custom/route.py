import collections
from typing import List

import metaheuristik.quinteroaraujo.code.cws_custom.edge as cwsEdge
import metaheuristik.quinteroaraujo.code.cws_custom.node as cwsNode
Node = cwsNode.Node
Edge = cwsEdge.Edge 

class Route (object):
    """
    An instance of this class represents a route made by a sequence
    of edges.
    """
    def __init__ (self, edges: List[Edge] = None, facilityId: int = None):
        """
        Initialise.

        :param edges: The edges that currently constitute the route.
        :attr cost: The overall cost of the route.
        """
        self.edges: List[Edge] = edges or collections.deque()
        self.cost = sum(edge.cost for edge in self.edges)
        self.facilityId = facilityId
        self.nodes: List[Node] = self.getNodes(edges)
        self.routeDemand = self.getTotalDemand()

    def getNodes(self, edges: List[Edge]):
        """
        Returns a list of all nodes (in the order they are visited (probably?)) except the "depot" node.
        """
        nodes: List[Node] = list()
        nodes = [edge.dest for edge in edges if edge.dest!=self.facilityId]
        """
        for edge in edges:
            if edge.dest != "depot" and edge.dest != self.facilityId:
                #nodes.add(edge.dest)
                if edge.dest not in nodes:
                    nodes.append(edge.dest)
            if edge.origin != "depot" and edge.origin != self.facilityId:
                #nodes.add(edge.origin)
                if edge.origin not in nodes:
                    nodes.append(edge.origin)
        """
        return nodes

    def getTotalDemand(self):
        totalDemand = 0
        for n in self.nodes:
            totalDemand+= n.demand
        return totalDemand

    @property
    def first_node (self):
        """
        The first node of the route visited after the origin.
        """
        return self.edges[0].dest

    @property
    def last_node (self):
        """
        The last node of the route visited before returning to the
        origin.
        """
        return  self.edges[-1].origin

    def popleft (self):
        """
        This method removes the first edge from the route and takes care
        of updating the overall cost too.
        """
        removed = self.edges.popleft()
        self.cost -= removed.cost
        self.nodes = self.getNodes(self.edges)
        self.routeDemand = self.getTotalDemand()

    def popright (self):
        """
        This method removes the last edge from the route and takes care
        of updating the overall cost too.
        """
        removed = self.edges.pop()
        self.cost -= removed.cost
        self.nodes = self.getNodes(self.edges)
        self.routeDemand = self.getTotalDemand()

    def extend (self, edges: List[Edge]):
        """
        This method is preferable for extending the route with new
        edges because it automatically updates the cost too.

        :param edges: The new edges to add to the route.
        """
        self.edges.extend(edges)
        self.cost += sum(edge.cost for edge in edges)
        self.nodes = self.getNodes(self.edges)
        self.routeDemand = self.getTotalDemand()

    def append (self, edge: Edge):
        """
        This method is preferable for adding a new edge to the route
        because it automatically updates the cost too.

        :param edge: The new edge to add to the route.
        """
        self.edges.append(edge)
        self.cost += edge.cost
        self.nodes = self.getNodes(self.edges)
        self.routeDemand = self.getTotalDemand()

    def __repr__(self):
        return str(list(self.edges))