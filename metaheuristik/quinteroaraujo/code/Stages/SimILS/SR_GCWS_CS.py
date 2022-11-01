"""
Juan, A., Faulin, J., Jorba, J. et al. 
On the use of Monte Carlo simulation, cache and splitting techniques to improve the Clarke and Wright savings heuristics. 
J Oper Res Soc 62, 1085–1097 (2011). 
https://doi.org/10.1057/jors.2010.29 
"""

from copy import deepcopy
from typing import Dict, List, Tuple
from multiprocessing.pool import AsyncResult
from multiprocessing import Pool
from numpy import random

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution

import metaheuristik.quinteroaraujo.code.cws_custom as cws
CWSInterface = cws.cwsInterface.CWSInterface
Route = cws.Route
Edge = cws.Edge

import metaheuristik.quinteroaraujo.code.Stages.SimILS as SimILSFunctions
splittingPolicy = SimILSFunctions.splittingPolicy
createSplittingPolicies = SimILSFunctions.createSplittingPolicies

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance

class Sr_gcws_cs():
    """
    Based on the SR-GCWS-CS heuristic for vehicle routing. An improved heuristic
    for vehicle routing, using splitting, caching and biased randomisation techniques.
    """
    def __init__(self, instance: LRPinstance):
        self.cwsI = CWSInterface(instance)

    def highQualityRoutingProcess(self, sol: SimILSSolution, nIter: int = 10, nIterPerSplit: int = 2):
        """
        For a given SimILSSolution - specifically using the assignmentVector - create routes and calculate associated costs.
        The facilities are already known and do not change throughout this process,
        therefore the problem to be solved is similar to a VRP.   

        :param sol: SimILSSolution with assignmentVector but not necessarily with a "working" tour/route attribute or routingVector.

        ## Returns

        - newSol: new SimILSSolution with routingVector and Tour attribute.
        """
        newSol = deepcopy(sol)
        multiprocessing = False 
        inst = newSol.instance
        customerSets = self.__customerSetsFromAssignmentVector__(newSol)
        improvedRoutesPerFacility = [list()]*len(inst.facilities)
        #print("##################\nStartSol\n###################")
        #sol.printSolution()
        if multiprocessing:
            improvedRoutesPerFacility = self.__multiProcessingForCustomerSets__(newSol,customerSets,inst.facilities,nIter,nIterPerSplit)
        else:
            improvedRoutesPerFacility = self.__multipleCustomerSetsHandler__(newSol,customerSets,inst.facilities,nIter,nIterPerSplit)
        simpleListOfRouting = [[[n.id for n in r.nodes] for r in improvedRoutesPerFacility[fIndex]] for fIndex in range(len(inst.facilities)) ]
        newSol.createTours(simpleListOfRouting)
        if newSol.totalCost < sol.totalCost:
            return newSol
            #return startSol    
        else:
            return newSol

    def __multiProcessingForCustomerSets__(self,simSol: SimILSSolution, customerSetPerFacility: List[int], facilities: List[int], nIter: int, nIterPerSplit: int):
        """
        ACTUALLY NOT USED/TESTED
        """
        improvedRoutesPerFacility = [list()]*len(facilities)
        numProcesses = 4
        pool = Pool(processes=numProcesses)
        processList: List[AsyncResult] = list()
        print("MULTIPROCESSING")
        for p in range(numProcesses):
            print(p)
            
            start = p
            stop = len(facilities)+1
            step = numProcesses
            print(customerSetPerFacility[start:stop:step])
            processList.append(pool.apply_async(self.__multipleCustomerSetsHandler__, args = (simSol,customerSetPerFacility[start:stop:step],facilities[start:stop:step],nIter,nIterPerSplit)))
        
        pool.close()
        pool.join()

        for p in range(numProcesses):
            start = p
            stop = len(facilities)
            step = numProcesses
            improvedRoutesPerFacility[start:stop:step] = processList[p].get()  
        return improvedRoutesPerFacility


    def __multipleCustomerSetsHandler__(self,simSol: SimILSSolution, customerSetPerFacility: List[int], facilities: List[int], nIter: int, nIterPerSplit: int):
        """
        Deals with multiple customerSets, each allocated to a different facility.
        """
        improvedRoutesPerFacility = [list()]*len(facilities)
        for fIndex, f in enumerate(facilities):
            customerSet = customerSetPerFacility[fIndex]
            if len(customerSet)> 0:
                improvedRoutes = self.__singleCustomerSetHandler__(simSol,customerSet,f,nIter,nIterPerSplit)
                improvedRoutesPerFacility[fIndex] = improvedRoutes
        #print("Finished " + str(customerSetPerFacility))
        return improvedRoutesPerFacility

    def __singleCustomerSetHandler__(self,simSol: SimILSSolution, customerSet: List[int], facility: int, nIter: int, nIterPerSplit: int):
        """
        Deal with a single Customer set and creates the improved routes for that specific set of customers.
        """
        improvedRoutes: List[Route] = list()
        if len(customerSet)>0:
            improvedRoutes = self.__sr_gcws_cs__(simSol,customerSet, facility, nIter, nIterPerSplit, useSplitting = True)
            #print("Improved Routes: " + str(improvedRoutes))
        return improvedRoutes


    def __sr_gcws_cs__(self,simSol: SimILSSolution, customers: List[int], facility: int, nIter: int, nIterPerSplit: int, useSplitting = False, rCache: Dict[str,Route] = None):
        """
        Solve the given VRP with the SimORouting's Generalized Clarke Wright Savings with Cache and Splitting algorithm (sr_gcws_cs).
        The facility remains unchanged.
        """
        if useSplitting:
            splittingPolicies: List[splittingPolicy] = createSplittingPolicies()
        startCwsSol, startCost, savingsList = self.__constructCWSSol__(simSol, customers, facility)
        if rCache == None:
            rCache: Dict[str,Route] = {}
        bestVrpSol: List[Route] = startCwsSol
        bestCost = startCost
        for i in range(nIter):
            vrpSol: List[Route] = list()
            vrpSol, newCost = self.__constructRandomSol__(simSol, customers, facility, savingsList)
            vrpSol, rCache = self.__improveSolUsingRoutesCache__(vrpSol, rCache)
            totalCost = sum(r.cost for r in vrpSol)
            if totalCost < bestCost and useSplitting:
                #print("Better sol found.")
                vrpSol = self.__improveSolUsingSplitting__(vrpSol,rCache, simSol,splittingPolicies, facility, nIterPerSplit, savingsList)
                bestVrpSol = vrpSol
                bestCost = totalCost
            elif totalCost < bestCost:
                bestVrpSol = vrpSol
                bestCost = totalCost
        return bestVrpSol

    def __improveSolUsingSplitting__(self,cwsSol: List[Route], rCache: Dict[str,Route], simSol: SimILSSolution, splittingPolicies: List[splittingPolicy], facility: int, nIterPerSplit: int, savingsList: List[Edge]):
        """
        Splitting approach to reduce the problem dimension and, therefore, the computational effort necessary to obtain quasi-optimal solutions.
        """
        #return cwsSol
        #print("Splitting started")
        inst = simSol.instance
        sol = cwsSol
        solTotalCost = sum(r.cost for r in sol)
        vrpCenter = self.__calcGeometricCenter__(cwsSol, simSol)
        rngen = random.default_rng()
        randomSplittingPolicies = rngen.choice(splittingPolicies,10,replace=False)
        for policy in randomSplittingPolicies:
            frontRoutes: List[Route] = list()
            backRoutes: List[Route] = list()
            frontRoutes = self.__selectFrontRoutes__(simSol,sol,vrpCenter,policy) 
            backRoutes = [r for r in sol if r not in frontRoutes]
            nodesInFrontRoutes = [node.id for r in frontRoutes for node in r.nodes ]
            bestSubSol = frontRoutes
            bestSubCost =  sum(r.cost for r in bestSubSol)
            #subVrpSol = sr_gcws_cs(simSol, nodesInFrontRoutes, facility, nIter=nIterPerSplit,useSplitting=False, rCache=rCache, nIterPerSplit=0)
            for _ in range(nIterPerSplit):
                newSubSol: List[Route] = list()
                newSubSol, newCost = self.__constructRandomSol__(simSol, nodesInFrontRoutes, facility, savingsList)
                newSubSol, rCache = self.__improveSolUsingRoutesCache__(newSubSol, rCache)
                newTotalCost = sum(r.cost for r in newSubSol)    
                if newTotalCost < bestSubCost:
                    bestSubSol = newSubSol
                    bestSubCost = newTotalCost
            newSol = backRoutes + bestSubSol
            totalCostNew = sum(r.cost for r in newSol)
            if totalCostNew < solTotalCost:
                sol = newSol
                solTotalCost = totalCostNew
        #print("Splitting Finished.")
        return sol

    def __selectFrontRoutes__(self,simSol: SimILSSolution, allRoutes: List[Route], routesCenter: Tuple[int,int], policy: splittingPolicy):
        """
        Apply splittingPolicy on List of routes and return list of routes (~frontRoutes) that fulfill policy.
        As soon as one node of a route is in the Policy Area, the whole route gets added to the frontRoutes
        """
        frontRoutes: List[Route] = list()
        inst = simSol.instance
        for r in allRoutes:
            for node in r.nodes:
                id = node.id
                xCoord, yCoord = inst.coordinates[id]
                if policy.checkIfNodeFulfillsPolicy(xCoord,yCoord, *routesCenter):
                        frontRoutes.append(r)
                        break 
        return frontRoutes    

    def __calcGeometricCenter__(self,cwsSol: List[Route], simSol: SimILSSolution):
        """
        Calculates the geometric center of all nodes in the routes.
        Note: a route object contains node objects. However, those node objects do not carry information about their coordinates.
        Therefore we need to "merge" the node IDs with the instance customers to find the coordinates of the nodes.
        """
        inst = simSol.instance
        xCenter = 0
        yCenter = 0
        count = 0
        for r in cwsSol:
            for node in r.nodes:
                id = node.id
                xCoord, yCoord = inst.coordinates[id]
                xCenter += xCoord
                yCenter += yCoord
                count += 1
        if count == 0:
            raise ValueError("Can't calculate geometric center of nothing that exists. (no nodes are given)")
        return xCenter/count, yCenter/count

    def __improveSolUsingRoutesCache__(self,cwsSol: List[Route], rCache: Dict[str,Route]):
        """
        A given solution is improved by using cache procedure which uses cache best results from previous iterations
        to improve (if possible) the current solution.

        For each route in cwsSol the cache is checked if there is already a known route for this hashcode. 
        The hashcode consists of the nodes/customers visited on this route in ascending order. 
        If there is already a hashcode in the rCache, it is checked if the current route outperforms the route found in the cache.
        Then update the cache or the current route, depending on the check. 
        """
        for rIndex, r in enumerate(cwsSol):
            hashCode = self.__getRouteHashCode__(r)
            if hashCode in rCache.keys():
                routeInCache: Route = rCache[hashCode]
                if routeInCache.cost < r.cost: # note: this allows new routes with same cost as cached route to be accepted
                    r = routeInCache
                    cwsSol[rIndex] = r
                    #print("Cache improved.")
                else:
                    self.__improveNodesOrder__()
                    rCache.update({hashCode: r})
            else:
                self.__improveNodesOrder__()
                rCache[hashCode] = r
        return cwsSol, rCache

    def __improveNodesOrder__(self):
        """
        TODO: implement. I dont know yet what this function is supposed to do.
        """
        return 0

    def __getRouteHashCode__(self,r: Route):
        """
        ~~Hashcode of a route is just the nodes in visited order.~~
        Hashcode of a route is the nodes sorted in ascending order.
        """
        nodes: List = list(r.nodes)
        nodes.sort(key= lambda x: x.id)
        #hashValue = str(r.getNodes())
        hashValue = str(nodes)
        return hashValue

    def __constructRandomSol__(self,sol: SimILSSolution, customers: List[int], facility: int, savingsList: List[int]):
        """
        create a random VRP sol using a CWS procedure, however dont pick edge with greatest savings, instead use a
        random edge, defined by geometric probability.
        """
        cwsSol, cost, savingsListNew = self.__constructCWSSol__(sol, customers, facility) 
        return cwsSol, cost

    def __constructCWSSol__(self,sol: SimILSSolution, customers: List[int], facility: int):
        """
        creates a routing solution for a given set of customers belonging to the same faciltiy,
        using the "simple" CWS algorithm.

        ### Returns:
        - cwsSol: List containing routes, which themselves are made of edges
        - cost: cost of this routing
        - savingsList: List of all edges sorted by their savings
        """
        cI = self.cwsI
        cwsSol, cost, savingsList = cI.CWSforCustomerSet(sol,customers,facility)
        return cwsSol, cost, savingsList

    def __customerSetsFromAssignmentVector__(self,sol: SimILSSolution):
        """
        given an assignmentVector, create a nested list containing the customers allocated to each facility
        
        ### Returns:
        nestedList of customers assigned to each facility
        """
        inst = sol.instance
        customerSets = [list() for _ in inst.facilities]
        for fIndex, f in enumerate(inst.facilities):
            f = inst.facilities[fIndex]
            for cIndex, assignedFac in enumerate(sol.assignmentVector):
                c = inst.customers[cIndex]
                if f == assignedFac:
                    customerSets[fIndex].append(c)
        return customerSets



