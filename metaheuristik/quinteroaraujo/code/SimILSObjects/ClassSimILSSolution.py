
from typing import List
from copy import deepcopy

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance
Tour = LRPObj.Tour
Solution = LRPObj.Solution

class SimILSSolution(Solution):
    def __init__(self, instance: LRPinstance, ss: int = 0):
        """
        :param ss: Safetystock in %, i.e. 10
        """
        self.safetystock = ss
        self.simulatedRoutingCost = 0
        self.simulatedTotal = 0
        self.reliability: float = 66.0
        super().__init__(instance)
        
    
    def randomSolution(self, combSet: List[int]):
        """
        Calls __assignNearestCustomers__ to assign the nearest customers to the opened facilities.
        :param combSet: Set of Facilities, 0 if closed, 1 if open
        """
        self.__assignNearestCustomers__(combSet)
        self.depotVector = combSet
        return 0

    def __assignNearestCustomers__(self, combSet: List[int]):
        """
        using the combSet of open facilities, assigns to a facility the nearest customers,
        as long as this facility has enough remaining capacity to serve the expected demand of the customer.
        Iterates over the open facilities.
        :param combSet: Set of Facilities, 0 if closed, 1 if open
        """
        import numpy
        assignmentVector = ["XX"]*len(self.instance.customers)
        depotVector = [0] * len(self.instance.facilities)
        fUsedCapacity = [0] * len(self.instance.facCapacity)
        fIndices = list(range(len(self.instance.facCapacity)))
        cIndices = list(range(len(self.instance.customers)))
        #numpy.random.shuffle(fIndices) # random order of facilities
        unassignedCustomersIndex: List = list(range(len(self.instance.customers)))
        availableFacilitiesIndexList = [fIndices[combSetIndex] for combSetIndex in range(len(combSet)) if combSet[combSetIndex] == 1]
        numpy.random.shuffle(availableFacilitiesIndexList)
        for fIndex in availableFacilitiesIndexList:
            facility = self.instance.facilities[fIndex]
            
            for cIndex in cIndices:
                if len(unassignedCustomersIndex) > 0: 
                    unassignedCustomersDistanceDict = {i:self.instance.distanceMatrix[facility][self.instance.customers[i]] for i in unassignedCustomersIndex}
                    sortedUnassignedCustomersDistanceDict = {k: v for k, v in sorted(unassignedCustomersDistanceDict.items(), key = lambda item: item[1])}
                    
                    for u in sortedUnassignedCustomersDistanceDict.keys():
                        expectedDemand = self.__expectedDemand__(u)
                        if fUsedCapacity[fIndex]+expectedDemand<=self.instance.facCapacity[fIndex]:         
                            assignmentVector[u] = self.instance.facilities[fIndex]
                            unassignedCustomersIndex.remove(u)
                            fUsedCapacity[fIndex]+=expectedDemand
                            depotVector[fIndex] = 1 
                            break
        self.assignmentVector = assignmentVector
        self.depotVector = depotVector
        return 0
    


    def createTours(self, routesPerFacility: List[int]):
        """
        Create a Tour object and assign it to the Tour-List attribut using a routesPerFacility Parameter.

        Previous Tours get removed! 

        :param routesPerFacility: Nested List, containing  for each depot the routes starting there.
            i.e.: [[[1,2],[3,4]],[[5,6]],[]]: Depot 1 has two routes, serving customer 1 and 2 as well as serving customer 3 and 4. 
            Depot 2 only has one route, serving customer 5 and 6. Depot 3 has no route and serves no customer.
        """
        #print(routesPerFacility)
        self.tours = list()
        self.routingCosts = list()
        self.simulatedRoutingCost = 0
        self.simulatedTotal = 0
        for fIndex in range(len(self.instance.facilities)):
            f = self.instance.facilities[fIndex]
            routesFromFacility = routesPerFacility[fIndex]
            for route in routesFromFacility:
                t = Tour(route,f,self.instance)
                t.updateRoutingCost()
                t.refineStrategies()
                self.tours.append(t)
                self.routingCosts.append(t.routingCost)
        self.__getTotalCost__()
        return 0

    def __deepcopy__(self, memodict=...):
        #newInstance = deepcopy(self.instance)
        newInstance = self.instance
        newS = SimILSSolution(newInstance)
        newS.routingVector = self.routingVector[:]
        newS.depotVector = self.depotVector[:]
        newS.pointerVector = self.pointerVector[:]
        newS.assignmentVector = self.assignmentVector[:]
        newS.tours = [deepcopy(t) for t in self.tours]
        newS.routes = self.routes[:]
        newS.usedFacilitiesIndex = self.usedFacilitiesIndex[:]
        newS.depotCost = self.depotCost
        newS.routingCosts = self.routingCosts[:]
        newS.totalCost = self.totalCost
        newS.safetystock = self.safetystock
        newS.simulatedRoutingCost = self.simulatedRoutingCost
        newS.simulatedTotal = self.simulatedTotal
        newS.reliability = self.reliability
        #print("Solution copied")
        return newS

    def updateAssignmentVectorByTours(self):
        for t in self.tours:
            facility = t.facility
            for c in t.routeVector:
                cIndex = self.instance.customers.index(c)
                self.assignmentVector[cIndex] = facility
        return 0

    def printSolution(self):
        super().printSolution()
        print("Simulated Routing Cost: " + str(self.simulatedRoutingCost))
        print("Simulated Total Cost: "+ str(self.simulatedTotal))
        print("Safety Stock Percentage: " + str(self.safetystock))
        print("Reliability Index: " + str(self.reliability))
        return 0
        