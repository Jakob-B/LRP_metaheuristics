import math, numpy
import itertools
from typing import List, Tuple, Dict

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance
import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution

import metaheuristik.quinteroaraujo.code.cws_custom.edge as cwsEdge
import metaheuristik.quinteroaraujo.code.cws_custom.node as cwsNode
import metaheuristik.quinteroaraujo.code.cws_custom.route as cwsRoute
import metaheuristik.quinteroaraujo.code.cws_custom.algorithm as cwsAlgorithm
Node = cwsNode.Node
Edge = cwsEdge.Edge
Route = cwsRoute.Route
cws = cwsAlgorithm 

class Street (Edge):
    pass

class Customer (Node):
    def __init__(self, instance, id, coord, facilityId, demand = 0):
        self.coord: Tuple(int,int) = coord
        demand = demand
        super(Customer, self).__init__(id,None,None, demand)

class CWSInterface():
    def __init__(self, instance: LRPinstance):#, sol: SimILSSolution):
        self.instance = instance
        #self.sol = sol

    def CWSforAssignmentVector(self, sol: SimILSSolution, assignmentVector):
        """
        Given an AssignmentVector, creates the "best" routes using Clarke-Wright-Savings heuristic.
        ### Returns:
        - routingVector: list of all customers in the order they are visited, independent of depots. 
                        I.e. [1,2,3,4,5,6]
        - pointerVector: list of "pointers", representing each facility and where in the routingVector its Route(s) are starting.
                        I.e. [0,1,4,0]: Depots 1 and 4 are closed, depot 2 serves customers 1,2,3; depot 3 serves customers 4,5,6; in that order, but not neccessarily in the same route/tour.
        - totalCost: total Cost of this Solution, including depot cost and travel/routingCost, but so far without vehicle cost.
        - routes: actual routes that a single vehicle is serving.
        - savingsList
        """
        inst = self.instance
        allAssignedCustomers = [list() for x in range(len(self.instance.facilities))]
        for fIndex in range(len(self.instance.facilities)):
            f = self.instance.facilities[fIndex]
            for cIndex in range(len(assignmentVector)):
                c = self.instance.customers[cIndex]
                if f == assignmentVector[cIndex]:
                    allAssignedCustomers[fIndex].append(c)
        totalCost = 0
        partRoutingVector = list()
        routesPerFacility = [list()]*len(self.instance.facilities)
        pointerVector = [0]*len(self.instance.facilities)
        for fIndex in range(len(self.instance.facilities)): 
            routes = list()
            assignedCustomers = allAssignedCustomers[fIndex]
            if len(assignedCustomers)>0:
                customerDemands = [inst.expectedDemand[cIndex] for cIndex in range(len(inst.customers)) if inst.customers[cIndex] in assignedCustomers]
                facility = self.instance.facilities[fIndex]
                cwsSols, cost, savingsList = self.__executeCWS__(sol, assignedCustomers,customerDemands, facility)
                pointerVector[fIndex] = len(partRoutingVector)+1
                routes, partPartRoutingVector = self.__CWStoRoutingVector__(cwsSols)
                partRoutingVector += partPartRoutingVector
                totalCost += cost
                routesPerFacility[fIndex] = routes
            else:    
                pointerVector[fIndex] = 0
        routingVector = partRoutingVector
        pointerVector
        #print(routesPerFacility)
        return routingVector, pointerVector, totalCost, routesPerFacility

    def CWSforCustomerSet(self, sol: SimILSSolution, customers: List[int], facility: int):
        """
        Executes the CWS algorithm for a list of customers to be served by a single facility.
        :param customers: List of customers, i.e. [3,7,20]
        :param facility: Facility which serves these customers, i.e. 22

        ### Returns:
        - cwsSol: List containing routes, which themselves are made of edges
        - cost: cost of this routing
        - savingsList: List of all edges sorted by their savings
        """
        inst = self.instance
        customerDemands = [inst.expectedDemand[inst.customers.index(cus)] for cus in customers]
        cwsSol: List[Route] = list()
        cwsSol, cost, savingsList = self.__executeCWS__(sol, customers,customerDemands,facility)
        return cwsSol, cost, savingsList

    def __executeCWS__(self, sol: SimILSSolution, assignedCustomers: List[int], customerDemand: List[int], facility: int):
        """
        Execute the actual CWS process, using a biased edge(savings) ranking and metaheuristic and the safetystock of the given solution.

        ### Returns:
        - sol: List containing routes (object), which themselves are made of edges
        - cost: cost of this routing
        - savingsList: List of all edges sorted by their savings
        """

        config = cws.CWSConfiguration(
            biased = True,
            reverse = True,
            metaheuristic = False,
            start = None,
            maxiter = 1000,
            maxnoimp = 500,
            maxcost = float("inf"),
            minroutes = 1,
            vehicleCap= self.instance.totalVehicleCap*(100-sol.safetystock)/100,
            rngenerator= numpy.random.default_rng()
        )
        coord = self.instance.coordinates
        facCoord = tuple(self.instance.coordinates[facility])
        customers = [Customer(self.instance,assignedCustomers[cIndex],(coord[assignedCustomers[cIndex]][0],coord[assignedCustomers[cIndex]][1]),facility , customerDemand[cIndex]) for cIndex in range(len(assignedCustomers))]
        streets = __get_streets__(customers, self.instance, facility)
        depotStreets = __getDepotStreets__(customers, self.instance, facility)
        solver = cws.ClarkeWrightSavings(nodes=customers, edges=streets, startEdgesTuple=depotStreets, facilityId= facility)
        sol: List[Route] = list()
        sol, cost, savingsList = solver.__call__(config)
        return sol, cost, savingsList

    def __CWStoRoutingVector__(self, CWSSols: List[Route] ):
        """
        :param CWSSol: List containing routes. 
                        Each route starting with (depot->...) and ending with (...->depot)
        This function makes a single list (~routingVector) out of these routes.
        """
        routingVector = list()
        routes = list()
        for sol in CWSSols:
            route = list()
            edges = sol.edges
            for edgeIndex in range(len(edges)-1):
                edge = edges[edgeIndex]
                routingVector.append(int(edge.dest.id))
                route.append(int(edge.dest.id))
            routes.append(route)
        return routes, routingVector

    
    
def __distance__ (city1, city2):
    delta0 = city1[0]-city2[0]
    delta1 = city1[1]-city2[1]
    return round(math.sqrt((delta0*delta0 + delta1*delta1)),2)

def __distanceByLookup__(instance: LRPinstance, id1, id2):
    return instance.distanceMatrix[id1][id2]

def __getDepotStreets__(customers: List[Customer], instance: LRPinstance, facilityId: int):
    depotStreets = []
    for c in customers:
        sDtoC = Street(facilityId,c,0,__distanceByLookup__(instance,c.id,facilityId))
        sCtoD = Street(c, facilityId,0,__distanceByLookup__(instance,facilityId, c.id))
        sDtoC.inverse = sCtoD
        sCtoD.inverse = sDtoC
        depotStreets.append((sDtoC,sCtoD))
    return depotStreets

def __get_streets__ (customers: List[Customer], instance: LRPinstance, facilityId: int):
    streets = []
    i: Customer
    j: Customer
    for i, j in itertools.combinations(customers,2):
        key = __streetKey__(i,j,facilityId)
        streetParamDict = __getStreetParamFromDict__(instance,key)
        if streetParamDict == None:
            cost = __distanceByLookup__(instance, i.id, j.id)
            costFromIToDepot = __distanceByLookup__(instance, i.id, facilityId)
            costFromDepotToJ = __distanceByLookup__(instance, facilityId, j.id)
            saving = costFromIToDepot + costFromDepotToJ - cost
            s = Street(i, j, saving, cost)
            s_inverse = Street(j, i, saving, cost)
            s.inverse, s_inverse.inverse = s_inverse, s
            __storeStreetParam__(instance,s,s_inverse,key)
        else:
            id1, id2, saving, cost = streetParamDict
            s = Street(i, j, saving, cost)
            s_inverse = Street(j, i, saving, cost)
            s.inverse, s_inverse.inverse = s_inverse, s
        streets.append(s)
    return tuple(streets)

def __streetKey__(nodeFrom: Customer, nodeTo: Customer, facility):
    key = str(nodeFrom.id)+"-"+str(nodeTo.id)#+":"+str(facility)
    return key

def __storeStreetParam__(instance: LRPinstance, street: Street, streetInverse: Street, key):
    streetParam = street.origin.id, street.dest.id, street.saving, street.cost
    #streetInverseParam = streetInverse.origin.id, streetInverse.dest.id, streetInverse.saving, streetInverse.cost
    streetTuple = (streetParam)#,streetInverseParam)
    instance.cwsStreetDict.update({key: streetTuple})

def __getStreetParamFromDict__(instance: LRPinstance, key):
    if key in instance.cwsStreetDict:
        return instance.cwsStreetDict[key]
    else:
        return None
