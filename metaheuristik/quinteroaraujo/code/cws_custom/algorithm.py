import operator
import collections
import functools
import dataclasses
import typing
from typing import Dict, Generator, List, Tuple
from numpy import random as rr


import metaheuristik.quinteroaraujo.code.cws_custom.node as cwsNode
Node = cwsNode.Node
import metaheuristik.quinteroaraujo.code.cws_custom.route as cwsRoute
Route = cwsRoute.Route
import metaheuristik.quinteroaraujo.code.cws_custom.edge as cwsEdge
Edge = cwsEdge.Edge


def biased_randomisation (array, rngen: rr.Generator):
    """
    This method carry out a biased-randomised selection over a certain list.
    The selection is based on a quasi-geometric function:

                    f(x) = (1 - beta) ^ x

    and it therefore prioritise the first elements in list.

    :param array: The set of options already sorted from the best to the worst.
    :param beta: The parameter of the quasi-geometric distribution.
    :return: The element picked at each iteration.
    """
    L = len(array)

    
    betaL, rnL = randomStuffList(rngen, L)
    options = list(array)
    selectedList = list()
    fastBiasedRandomisation = False
    if fastBiasedRandomisation and L > 0:
        beta = betaL[0]
        probabilities = [(1-beta)**(k-1+1)*beta for k in range(0,L)]
        delta = 1-sum(probabilities)
        probabilities[0] += delta
        selectedList = list(rr.choice(options,L,replace=False,p=probabilities))
    else:
        for l in range(L):
            probLessEqK = 0
            rn = rnL[l]
            beta = betaL[l]
            oneMinusBeta = 1-beta # = 1 - beta
            oneMinusBetaExponent = 1       # = (1-beta)^k. at start k = 0, so (1-beta)^0 = 1
            for k in range(len(options)):
                probEqK = oneMinusBetaExponent*beta # P(X=k) = (1-beta)^(k-1+1) * beta ; NOTE: mathematically speaken, we should start with k = 0 and Position 1 in List (k-1). But programatically, List starts at positon 0, so no need to subtract anything From k here (add 1 again, k-1+1). Just for completeness.

                #probEqK = pow(1-beta,k+1-1)*beta
                
                probLessEqK += probEqK
                if probLessEqK > rn:
                    idx = k
                    selectedList.append(options.pop(idx))
                    
                    
                    break
                elif k == len(options)-1:
                    # sometimes some of the edges with fewest savings don't get added, because the random number rn is to high. 
                    # In that case, add the edge with the highest 'fewest' savings to the list. 
                    selectedList.append(options[0])
                    options.pop(0)
                oneMinusBetaExponent *= oneMinusBeta  # next "power" for next Iteration k+1: = (1-beta)^(k) * (1-beta) = (1-beta)^(k+1)
            
    return selectedList

def randomStuffList(rngen: rr.Generator, size):
    betaL = list(rngen.random(size=size)*0.2+0.05)
    #betaL = [0.4]*size
    rnL = list(rngen.random(size=size))
    return betaL, rnL


@dataclasses.dataclass(repr=True, frozen=True)
class CWSConfiguration:
    """
    An instance of this class represents a configuration of the parameters
    used during the execution of the algorithm.
    It can be passed to the heuristic method as well as to the __call__ method.

    :param biased: If True a biased randomisation is used, otherwise not.
                    In case of active biased randomisation the callable method
                    passed as biasedfunc is used.
    :param biasedfunc: The function to use in case of biased randomisation
                        required.
    :param reverse: If True every time a merging is tried, the possibility
                    to reverse the routes we are going to merge is considered.
                    Usually this parameter is False when the reverse of an edge
                    is different by the edge itself.
    :param metaheuristic: If True more solutions are generated doing a sort
                        of iterated local search, otherwise a single solution
                        is returned using the classic heuristic.
    :param start: The starting solution generated with a different method or
                 parameters, we want the metaheuristic to start from.
    :param maxiter: The maximum number of solutions explored in case of a
                    metaheuristic.
    :param maxnoimp: The maximum number of
    :param maxcost: The maximum cost of a route that makes it feasible.
    :param minroutes: The minimum number of routes allowed.
    :param vehicleCap: The maximum amount of demand that one vehicle can deliver. 
                    If more demand of all nodes than vehicle cap, another route is needed/created.
                    There is one vehicle per route.
    """
    biased : bool = True
    biasedfunc : typing.Callable = biased_randomisation
    reverse : bool = True
    metaheuristic : bool = False
    start : typing.Tuple[typing.List[Route], int] = None
    maxiter : int = 1000
    maxnoimp : int = 500
    maxcost : float = float('inf')
    minroutes : float = float('-inf')
    vehicleCap : float = float('inf')
    rngenerator: Generator = None



class ClarkeWrightSavings (object):
    """
    An instance of this class represents the
    Clarke & Wright Savings heuristic implementation.
    """
    def __init__(self, nodes: List[Node], edges: List[Edge], startEdgesTuple: List[Tuple[Edge]], facilityId: int):
        """
        Initialise.

        :param nodes: The nodes to visit.
        :param edges: The edges connecting the nodes.
        :param startEdges: The 2-tuple of edges connecting the nodes to the depot and from depot to node
        """
        self.nodes: List[Node] = nodes
        self.edges: List[Edge] = edges
        self.startEdgesTuple: List[Tuple[Edge]] = startEdgesTuple
        self.facilityId: int = facilityId

    @staticmethod
    def savings_list (edges):
        """
        Given the set of edges, this method generates the savings list
        by simply sorting them for decreasing saving value.

        :param edges: The edges list.
        """
        return sorted(edges, key=operator.attrgetter("saving"), reverse=True)

    @staticmethod
    def _reversed (route: Route):
        """
        This method is used to reverse a route.
        It instantiate and return a new Route.

        :param route: The route to reverse.
        """
        return Route(collections.deque(reversed([e.inverse for e in route.edges])),route.facilityId)

    def heuristic (self, config: CWSConfiguration):
        """
        This method is the core of the algorithm. Here is where the well-known
        Clarke & Wright Savings algorithm is implemented.

        It is indirectly used by the main method __call__, or it can be used
        alone for generating a single solution using different berameters or
        behaviour.

        :param config: The configuration used during the execution of the heuristic
                        (see CWSConfiguration class).
        """
        edges, nodes, startEdgesTuple = self.edges, self.nodes, self.startEdgesTuple
        biased, biasedfunc, reverse = config.biased, config.biasedfunc, config.reverse
        maxcost, minroutes = config.maxcost, config.minroutes
        rngenerator = config.rngenerator
        routes: List[Route] = list()

        nodes: List[Node]
        # Generates the dummy solution

        for e1, e2 in startEdgesTuple:
            e1: Edge
            e2: Edge
            r = Route(collections.deque([e1, e2]),self.facilityId)
            routes.append(r)
        
        # routes dictionary: for a given node, has the associated route which ends (Dest) or starts (Origin) at this node.
        routeOfNode = dict([(route.first_node, route) for route in routes])
        
        # Generates the savings list with eventual biased randomisation
        savings_list: List[Edge] = self.savings_list(edges)
        savings_iterator = savings_list if not biased else biasedfunc(savings_list, rngenerator)

        # Starts the iterative merging process...
        for edge in savings_iterator:

            # Check if the minimum number of routes has been reached
            # number of routes DECREASES during algorithm, because they get merged.
            if len(routes) <= minroutes:
                #print("Print current routes:")
                #for r in routes:
                #    print(str(r.edges))
                #    print(str(r.cost))
                return routes, sum(r.cost for r in routes), savings_list

            # Get the routes connected by the currently considered edge
            origin, dest = edge.origin, edge.dest
            iroute: Route = routeOfNode[edge.origin] #routeOrigin[edge.origin]
            jroute: Route = routeOfNode[edge.dest] #routeDest[edge.dest]

            # If the routes are the same, next edge is considered
            if iroute == jroute:
                continue

            # If adding the two routes exceed vehicleCap, next edge is considered
            if iroute.routeDemand + jroute.routeDemand > config.vehicleCap:
                continue

            # Check if extremes of edge are internal. In this case,
            # next edge is considered.
            # Prüfe ob die derzeit betrachtete Kante zwei Knoten verbinden würde, welche nicht am Anfang
            # oder Ende einer Route sind. Es dürfen nur Knoten von zwei verschiedenen Routen verbunden werden, 
            # wenn sie sich am jeweiligen Ende oder Anfang ihrer derzeitigen Route befinden.
            if (origin != iroute.first_node and origin != iroute.last_node) or \
                (dest != jroute.first_node and dest != jroute.last_node):
                continue

            # If the merging is possible with no reversions...
            if origin == iroute.last_node and dest == jroute.first_node:
                # If the maxcost of a route is not exceeded...
                if iroute.cost + jroute.cost - edge.saving <= maxcost:
                    # Remove the edges to the origin in the merged routes
                    iroute.popright()
                    jroute.popleft()
                    # Build the new route
                    iroute.append(edge)
                    iroute.extend(jroute.edges)
                    # Update the list of routes
                    routes.remove(jroute)
                    # update the dictionary of routes: jroute node also referencing to iroute
                    for node in iroute.nodes:
                        routeOfNode[node] = iroute
                # Next edge is considered
                continue

            # If it is not possible to reverse the route and the edge
            if not reverse and (origin != iroute.last_node or dest != jroute.first_node):
                continue

            # If the reversion of routes is possible
            if reverse:
                # Initialise the reversed edge and routes before eventual
                # reversing process.
                redge, riroute, rjroute = edge, iroute, jroute
                # If both routes should be reversed, reverse the edge: Fall I
                if origin == iroute.first_node and dest == jroute.last_node:
                    #redge = edge.inverse
                    routes.remove(iroute)
                    riroute = self._reversed(iroute)
                    routes.append(riroute)
                    routes.remove(jroute)
                    rjroute = self._reversed(jroute)
                    routes.append(rjroute)
                # Reverse the first route: Fall II
                elif origin != iroute.last_node and dest == jroute.first_node:
                    routes.remove(iroute)
                    riroute = self._reversed(iroute)
                    routes.append(riroute)
                # Reverse the second route: Fall III
                elif origin == iroute.last_node and dest != jroute.first_node:
                    routes.remove(jroute)
                    rjroute = self._reversed(jroute)
                    routes.append(rjroute)
                else:
                    raise ValueError("Somethings wrong in CWS route merging.")
                # Once routes and edge are ready for merging, check the cost
                # If the cost of the new route does not exceed the maximum allowed...
                if riroute.cost + rjroute.cost - redge.saving <= maxcost:
                    # Remove the edges to the origin in the merged routes
                    riroute.popright(); rjroute.popleft();
                    # Build the new route
                    riroute.append(redge)
                    riroute.extend(rjroute.edges)
                    # Update the list of routes
                    routes.remove(rjroute)
                    # update the dictionary of routes: jroute node also referencing to iroute
                    for node in riroute.nodes:
                        routeOfNode[node] = riroute
                        

        # Returns the solution found
        #print("Print current routes:")
        #for r in routes:
        #    print(str(r.edges))
        #    print(str(r.cost))

        return routes, sum(r.cost for r in routes), savings_list


    def _metaheuristic (self, starting_sol, config):
        """
        This method represents an Iterated Local Search in which
        the Clarke Wright Savings heuristic is incorporated.
        In order to generate a ifferent solution at each iteration,
        the biased randomisation in the configuration should be activated
        and a biasedfunc should be provided.

        :param starting_sol: The starting solution.
        :param config: The configurations of parameters defined.
        """
        # Initialise the behaviour we want to use to generate new solutions
        heuristic = functools.partial(self.heuristic, config)
        # Initialise the current best solution
        best, cost, savingsList = starting_sol
        maxiter, maxnoimp = config.maxiter, config.maxnoimp
        missed_improvements = 0
        # Starts the iterated local search
        for _ in range(maxiter):
            # Generates a new solution
            newsol, newcost, savingsList = heuristic()
            missed_improvements += 1
            # Eventually updates the best
            if newcost < cost:
                best, cost = newsol, newcost
                missed_improvements = 0
            # If the maximum number of iterations with no improvement is exceeded
            # returns the current best
            if missed_improvements > maxnoimp:
                return best, cost, savingsList
        # Return the best solution found at the end of the process
        return best, cost, savingsList



    def __call__(self, config):
        """
        This method representes the main function of the algorithm.

        :param config: The configuration of parameters used for the
                        execution of the algorithm (see CWSConfiguration class).
        """
        best, cost, savingsList = self.heuristic(config)
        if config.metaheuristic:
            starting_sol = config.start or self.heuristic(config)
            best, cost, savingsList = self._metaheuristic(starting_sol, config)
        return best, cost, savingsList
