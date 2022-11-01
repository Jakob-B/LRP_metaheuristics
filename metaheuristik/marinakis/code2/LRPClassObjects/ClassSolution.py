from copy import deepcopy
from typing import List
from datetime import datetime
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance
import metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance as ObjInstance
LRPinstance = ObjInstance.LRPinstance
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassTour import Tour
import metaheuristik.marinakis.code2.LRPClassObjects.ClassTour as ObjTour
Tour = ObjTour.Tour
class Solution:
    """
    Represents a solution for the LRP.
    
    :param routingVector: is a list of customers, representing the order, in which they are visited/served on a route. 
    Note that this routingVector contains all routes here connected to a long route. In order to distinguish
    between different routes, the pointerVector is required. Length = Number of customers
    
    :param pointerVector: is a list of pointer, pointing at the position in the routingVector, where a route starts. 
    I.e. the second value in the pointerVector being "3" means, that the second facility starts its route at the customer
    that is at the 3rd position in the routing vector. Length = Number of facilities
    
    :param depotVector: is a boolean list, indicating if a faciltiy is open (1) or closed (0). If the pointerVector
    points at a position in the routingVector (meaning value is not null), then depotVector should be 1 - a 
    facility can only start a route at a customer, if it is openend. Length = Numer of facilities

    :param assignmentVector: list of facilities, that serve the corresponding customer at position i. I.e.
    assignmentVector value at position 1 being 12 means, that the facility 12 serves the customer at the 
    instance.customers list position 1. Length = number of customers.
    """
    def __init__(self, instance: LRPinstance) :
        self.routingVector = list()
        self.depotVector = list()
        self.pointerVector = list() # array; if value at pos i is 0, then depot is closed. Otherwise, i indicates the position in array routingVector (+1!), where routingVector of customers belonging to pos facility begins!
        self.assignmentVector: List[int] = [0]*len(instance.customers)
        self.instance = instance
        self.tours: List[Tour] = list()
        self.routes: List[int] = list() 
        self.usedFacilitiesIndex: List[int] = list()
        self.depotCost = 0
        self.routingCosts = list()
        self.totalCost = 0
        self.tourcreationtime = 0
    def __createRoutes__(self):
        """
        Based on routeVector and pointerVector, create the corresponding individual routes. \nDoes NOT create Tours or calculate routingCost Calculation.
        \nNote: PointingVector starts counting with 1 (not 0)! 0 means that the facility is closed!
        """
        # Error check if any tour starts at customer 1 (required!)
        if 1 not in self.pointerVector:
            raise ValueError("pointerVector " + str(self.pointerVector) +" is wrong. No pointer to first position in routingVector.")    


        # Create list of customers, that start a route, which means that they should not be in another route (other route should STOP before)
        stopList = list()
        for f in range(len(self.pointerVector)):
            pointerValue = self.pointerVector[f]
            if pointerValue!=0:
                AstartingCustomer = self.routingVector[pointerValue-1]
                stopList.append(AstartingCustomer)

        # Create Routes
        routes = [0]*len(self.instance.facilities)
        usedFacilitiesIndex = list()
        for f in range(len(self.pointerVector)):
            fValue = self.pointerVector[f] # tells the position in the routingVector where the route for this facility starts.
            if fValue != 0:
                usedFacilitiesIndex.append(f)
                route = list()
                startPos = fValue
                startCustomer = self.routingVector[startPos-1] # pointingVector starts counting with 1, so subtract 1 to access list correctly
                route.append(startCustomer)
                self.assignmentVector[self.instance.customers.index(startCustomer)] = self.instance.facilities[f] 
                for f2 in range(startPos-1+1,len(self.routingVector)):
                    customer = self.routingVector[f2]
                    if customer not in stopList:
                        route.append(customer)
                        self.assignmentVector[self.instance.customers.index(customer)] = self.instance.facilities[f] 
                    else:
                        break
                routes[f] = route
            else:
                routes[f] = []
        #print("Created routes are:" + str(routes))
        #print("Used Facilities (named by Index) are: "+ str(usedFacilitiesIndex))

        self.routes = routes
        self.usedFacilitiesIndex = usedFacilitiesIndex


    def pointerVectorByRoutes(self,routes:List[int]):
        """
        Given a list of routes, create the corresponding pointer Vector.
        Return new pointerVector.
        """
        #For RoutingVector, simply connect the routes to eachother. Therefore, not calculated here.
        #routingVector = [j for i in routes for j in i]
        pointerVector = [0]*(len(self.instance.facilities))
        pos = 1
        for fIndex in range(len(self.instance.facilities)):
            if len(routes[fIndex])==0:
                pointerVector[fIndex]=0
            else:
                pointerVector[fIndex]=pos
                pos += len(routes[fIndex])
        
        return pointerVector
    
    def depotVectorByRoutes(self,routes:List[int]):
        """
        Given a list of routes, create the corresponding Depot Vector.
        Return new depot Vector
        """
        depotVector = [0]*(len(self.instance.facilities))
        for fIndex in range(len(self.instance.facilities)):
            if len(routes[fIndex])==0:
                depotVector[fIndex]=0
            else:
                depotVector[fIndex]=1
        return depotVector



    def __createTours__(self, knownTours: dict = None):
        """
        Create Tour objects: make new Tour object for each route and calculate the routing cost.
        """
        self.routingCosts = list()
        self.tours = list()
        #knownTours = None #Debug
        #for f in range(len(self.usedFacilitiesIndex)):
        for f in range(len(self.instance.facilities)):
            if len(self.routes[f])>0:
                route = self.routes[f] # same index
                t = Tour(route, self.instance.facilities[f], self.instance)
                
                if knownTours != None:
                    fullTrip = [self.instance.facilities[f]] + route + [self.instance.facilities[f]]
                    if str(fullTrip) in knownTours:
                        t: Tour = knownTours[str(fullTrip)]
                    else:
                        self.tourcreationtime += t.updateRoutingCost()
                else:
                    #startTimeRC = datetime.now()
                    self.tourcreationtime += t.updateRoutingCost()
                    #stopTimeRC = datetime.now()
                    #elapsedTimeRC = (stopTimeRC-startTimeRC).total_seconds()
                    #print("Time update Routing Cost: " + str(elapsedTimeRC)) 
                self.routingCosts.append(t.routingCost)
                self.tours.append(t)

    def __getTotalCost__(self):
        totalCost = 0
        totalCost += self.depotCost
        for rc in self.routingCosts:
            totalCost += rc
        self.totalCost = totalCost

    def refreshRoutingCost(self):
        self.routingCosts = list()
        for t in self.tours:
            self.routingCosts.append(t.routingCost)

    def __getDepotCost__(self):
        depotCost = 0
        for f in range(len(self.depotVector)):
            fValue = self.depotVector[f]
            if fValue == 1:
                depotCost += self.instance.openingCost[f]
        self.depotCost = depotCost

    def __setAvectorAndDvectorByRvectorAndPvector__(self):
        """
        Using the Routing Vector and Pointer Vector,
        update the values for the assignment vector and depot Vector.
        """
        startRIndexDict = {}
        # Depot Vector
        for fIndex in range(len(self.pointerVector)):
            if self.pointerVector[fIndex] >= 1:
                self.depotVector[fIndex]=1
                startRIndexDict.update({fIndex:self.pointerVector[fIndex]})
            else:
                self.depotVector[fIndex]=0
                startRIndexDict.update({fIndex:0})
        # Assignment Vector
        for cIndex in range(len(self.routingVector)):
            for k in startRIndexDict.keys():
                if startRIndexDict[k]==cIndex+1:
                    assignedDepot = k
            c = self.routingVector[cIndex]
            cIndexA = self.instance.customers.index(c)
            self.assignmentVector[cIndexA] = self.instance.facilities[assignedDepot]
        return 0


    def updateSolution(self, knownTours: dict = None):
        """
        Updates (or creates) the routes-parameter with the given pointerVector and routingVector
        and creates the corresponding Tours, as long as the routes are feasible.

        Returns false if no feasible tours have been created, true if Tours have been created.

        **Note**: depotVector and AssignmentVector also get updated by calling this function using
        the routingVector and pointerVector.
        """
        #self.setAvectorAndDvectorByRvectorAndPvector()
        #if len(self.routingVector) != len(self.instance.customers):
         #   print("Error")
        #startTimeRF = datetime.now()
        if self.__createRoutesIfFeasible__():
            #stopTimeRF = datetime.now()
            #elapsedTimeRF = (stopTimeRF-startTimeRF).total_seconds()
            #startTimeDC = datetime.now()
            self.__getDepotCost__()
            #stopTimeDC = datetime.now()
            #elapsedTimeDC = (stopTimeDC-startTimeDC).total_seconds()
            startTimeCT = datetime.now()
            self.__createTours__(knownTours)
            stopTimeCT = datetime.now()
            elapsedTimeCT = (stopTimeCT-startTimeCT).total_seconds()
            #print("Time Create Tours: " + str(elapsedTimeCT))
            #startTimeTC = datetime.now()
            self.__getTotalCost__()
            #stopTimeTC = datetime.now()
            #elapsedTimeTC = (stopTimeTC-startTimeTC).total_seconds()
            #print("Time Route Feasible Check: " + str(elapsedTimeRF) 
            #    + ";\n Time Depot Cost Calc: " + str(elapsedTimeDC)
            #    + ";\n Time Create Tours: " + str(elapsedTimeCT)
            #
            #     + ";\n Time Tour Cost Calc: " + str(elapsedTimeTC) )
            return True
        #else:
            #print("Unfeasible solution:" + str(self.routingVector) + "" + str(self.pointerVector))
        return False


    def __createRoutesIfFeasible__(self):
        """"
        checks if this Solution is feasible regarding:
        - pointer vector (should contain a 1)

        Needs to be done before routes are created.

        Then creates routes and checks feasible regarding:
        - depot capacity

        """
        
                
        feasible = False
        if 1 not in self.pointerVector:
            feasible = False
            return feasible
        else:
            feasible = True
            for c in self.instance.customers:
                if c not in self.routingVector:
                    feasible = False
                    return feasible
            d = dict()
            for c in self.routingVector: d[c] = d[c] + 1 if c in d else 1
            for k in d.keys():
                if d[k]> 1:
                    return False 
            self.__setAvectorAndDvectorByRvectorAndPvector__()
            self.__createRoutes__()
            for f in self.instance.facilities:
                expTotalDemand = 0
                for c in range(len(self.assignmentVector)):
                    if self.assignmentVector[c] == f:
                        expTotalDemand += self.__expectedDemand__(c)
                        if expTotalDemand > self.instance.facCapacity[self.instance.facilities.index(f)]:
                            feasible = False
                            break

            
        
        return feasible

    def __expectedDemand__(self,customerIndex: int):
        #customerIndex = self.instance.customers.index(customer)
        expDemand = 0
        customerDemands = self.instance.demandProbMatrix[customerIndex]
        for d in range(len(customerDemands)):
            expDemand += d * customerDemands[d]
        return expDemand


    def randomSolution(self):
        """
        Creates a random, feasible solution (assignmentVector, RoutingVector, PointingVector) and calculates the Cost.
        """
        import numpy
        assignmentType = numpy.random.randint(1,101)
        if assignmentType <= 50:
            self.__randomAssignmentVector__()
        else:
            self.__assignNearestCustomers__()
        #self.__randomRoutingVector__()
        self.__nearestInsertion__()
        #self.__closestRoutingVector__()
        self.updateSolution()
        
        return 0

    def __randomAssignmentVector__(self):
        """
        allocats the customers to a random facility, as long as this facility has enough remaining capacity to serve
        the expected demand of the customer.
        Iterates over the customers.
        """
        import numpy
        assignmentVector = ["XX"]*len(self.instance.customers)
        depotVector = [0] * len(self.instance.facilities)
        fUsedCapacity = [0] * len(self.instance.facCapacity)
        for c in range(len(self.instance.customers)):
            # calculated expected Demand of customer
            expectedDemand = self.__expectedDemand__(c)
            
            # determine facilities which have enough remaining capacity
            availableF = list()
            fIndices = list(range(len(self.instance.facCapacity)))
            numpy.random.shuffle(fIndices)
            for fIndex in fIndices:
                if fUsedCapacity[fIndex]+expectedDemand<=self.instance.facCapacity[fIndex]:
                    availableF.append(fIndex)
            if(len(availableF)==0):
                raise ValueError("Not enough facility capacity.")    
            # assign customer to a facility of availableF (facility which has enough remaining capacity)
            allocatedFaciliyIndex = numpy.random.choice(availableF,1,False).tolist()[0]
            assignmentVector[c] = self.instance.facilities[allocatedFaciliyIndex]
            depotVector[allocatedFaciliyIndex] = 1 
            fUsedCapacity[allocatedFaciliyIndex]+=expectedDemand
        self.assignmentVector = assignmentVector
        self.depotVector = depotVector
        return 0

    def __assignNearestCustomers__(self):
        """
        assigns to a facility the nearest customers, as long as this facility has enough remaining capacity to serve
        the expected demand of the customer.
        Iterates over the facilities.
        """
        import numpy
        assignmentVector = ["XX"]*len(self.instance.customers)
        depotVector = [0] * len(self.instance.facilities)
        fUsedCapacity = [0] * len(self.instance.facCapacity)
        fIndices = list(range(len(self.instance.facCapacity)))
        cIndices = list(range(len(self.instance.customers)))
        numpy.random.shuffle(fIndices) # random order of facilities
        unassignedCustomersIndex: List = list(range(len(self.instance.customers)))
        for fIndex in fIndices:
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
                    """
                    nearestUnassignedCustomerIndex = list(unassignedCustomersDistanceDict.keys())[0]
                    for u in unassignedCustomersDistanceDict.keys():
                        if unassignedCustomersDistanceDict[u]<unassignedCustomersDistanceDict[nearestUnassignedCustomerIndex]:
                            nearestUnassignedCustomerIndex = u
                    # calculated expected Demand of nearest customer
                    expectedDemand = self.__expectedDemand__(nearestUnassignedCustomerIndex)
                    if fUsedCapacity[fIndex]+expectedDemand<=self.instance.facCapacity[fIndex]:         
                        assignmentVector[nearestUnassignedCustomerIndex] = self.instance.facilities[fIndex]
                        unassignedCustomersIndex.remove(nearestUnassignedCustomerIndex)
                        fUsedCapacity[fIndex]+=expectedDemand
                        depotVector[fIndex] = 1 
                    """
        self.assignmentVector = assignmentVector
        self.depotVector = depotVector        
        return 0
    #def __closestCustomer__(self, facilityIndex):


    def __randomRoutingVector__(self):
        """
        using the assignmentVector, puts the customers of a facility in a random order and
        creates the corresponding routing and pointerVector
        """
        import numpy
        routingVector = []
        pointerVector = [0]*len(self.instance.facilities)
        for fIndex in range(len(self.instance.facilities)):
            assignedCustomersIndex = list()
            f = self.instance.facilities[fIndex]
            for cIndex in range(len(self.instance.customers)):
                if self.assignmentVector[cIndex] == f:
                    assignedCustomersIndex.append(cIndex)
            numpy.random.shuffle(assignedCustomersIndex)
            # Routing Vector
            point = len(routingVector)
            for cIndex in assignedCustomersIndex:
                c = self.instance.customers[cIndex]
                routingVector.append(c)
            # Pointer Vector
            if len(assignedCustomersIndex)>0:
                pointerVector[fIndex] = point+1
        self.pointerVector = pointerVector
        self.routingVector = routingVector
        return 0

    def __closestRoutingVector__(self):
        routingVector = []
        pointerVector = [0]*len(self.instance.facilities)
        for fIndex in range(len(self.instance.facilities)):
            customerDistanceTupleList = list()
            f = self.instance.facilities[fIndex]
            for cIndex in range(len(self.instance.customers)):
                if self.assignmentVector[cIndex] == f:
                    c = self.instance.customers[cIndex]
                    distanceCustomerFacility = self.instance.distanceMatrix[f][c]
                    customerDistanceTupleList.append((c,distanceCustomerFacility))
                    sorted(customerDistanceTupleList,key=lambda x: x[1])
            # Routing Vector
            point = len(routingVector)
            for c,_ in customerDistanceTupleList:
                routingVector.append(c)
            # Pointer Vector
            if len(customerDistanceTupleList)>0:
                pointerVector[fIndex] = point+1
        self.pointerVector = pointerVector
        self.routingVector = routingVector
        return 0
    
    def __nearestInsertion__(self):
        routingVector = []
        pointerVector = [0]*len(self.instance.facilities)
        for fIndex in range(len(self.instance.facilities)):
            f = self.instance.facilities[fIndex]
            point = len(routingVector)
            assignedCustomers = []
            # assigned Customers 
            for cIndex in range(len(self.instance.customers)):
                c = self.instance.customers[cIndex]
                if self.assignmentVector[cIndex] == f:
                    assignedCustomers.append(c)
            # pointerVector
            if len(assignedCustomers)>0:
                pointerVector[fIndex]= point+1
                #RoutingVector
                currentNode = f
                while(len(assignedCustomers)>1): # last remaining node gets added at the end
                    shortestDistanceNode, shortestDistance = min([(otherNode, self.instance.distanceMatrix[currentNode][otherNode]) for otherNode in assignedCustomers if currentNode != otherNode],key = lambda x: x[1])
                    #shortestDistanceNode = self.instance.distanceMatrix[currentNode].index(shortestDistance)
                    #shortestDistanceNode = self.instance.customers[shortestDistanceCIndex]
                    routingVector.append(shortestDistanceNode)
                    assignedCustomers.remove(shortestDistanceNode)
                    currentNode = shortestDistanceNode
                    
                # last remaining customer gets added at the end 
                routingVector.append(assignedCustomers[0])
        self.pointerVector = pointerVector
        self.routingVector = routingVector
            

            

    def printSolution(self):
        """
        TODO: Print Solution...
        """
        print("\n###\nSolution State:")
        print("Routing Vector: " + str(self.routingVector))
        print("Pointing Vector: " + str(self.pointerVector))
        print("Depot Vector: " + str(self.depotVector))
        print("Assignment Vector: " + str(self.assignmentVector))
        print("Total Cost: " + str(self.totalCost))
        print("Routing Cost: " + str(self.routingCosts))
        print("Depot Cost: " + str(self.depotCost))
        print("Routes: " + str(self.routes))
        print("Tours:")
        for t in self.tours:
            t.printTour()
    
    def __deepcopy__(self, memodict={}):
        newS = Solution(self.instance)
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
        #print("Solution copied")
        return newS
        
