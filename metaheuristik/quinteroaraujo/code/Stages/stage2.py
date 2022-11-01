
from copy import deepcopy
from numpy import random
import math
from typing import List
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance

import metaheuristik.quinteroaraujo.code.Stages.SimILS as SimILS
Sr_gcws_cs = SimILS.Sr_gcws_cs
LocalSearch = SimILS.LocalSearch
LocalSearchLimit = SimILS.LocalSearchLimit

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution
MCSimulation = SimObj.MCSimulation

class Stage2():
    """
    Stage 2 is the second stage of the SimILS metaheuristic
    and deals with improving the solutions generated in the first stage.
    """
    def __init__(self, instance: LRPinstance):#, baseSols: List[SimILSSolution]):
        #self.baseSols: List[SimILSSolution] = baseSols
        self.instance: LRPinstance = instance
        self.localSearch: LocalSearch = LocalSearch(instance)
        self.sr_gcws_cs: Sr_gcws_cs = Sr_gcws_cs(instance)
        self.MCSimulation = MCSimulation(instance)
        

    def solutionImprovement(self,baseSols: List[SimILSSolution], maxIter: int):
        """
        ## Stage 2: Solution Improvement

        > In this stage, the goal is to explore in more detail each of the base solutions so that
        better customer-to-facility allocations and routing plans can be identified in them. 

        > The open facilities in each base solution however are not changed. 
        """
        promisingSolsPerBase: List[SimILSSolution] = list()
        promisingSols: List[SimILSSolution] = list()
        multiprocessing = False
        if multiprocessing:
            promisingSolsPerBase = self.__solutionImprovementMultiProcess__(baseSols, maxIter)
        else:
            for baseSol in baseSols:
                promisingSolsPerBase += self.__improveSolutionPerBaseSol__(baseSol,maxIter)
        for promisingSol in promisingSolsPerBase:
            promisingSols = self.__updatePromisingSolsList__(promisingSol)
        return promisingSols

    def __solutionImprovementMultiProcess__(self,baseSols: List[SimILSSolution], maxIter: int):
        """
        Manages multiple processes which deal with the solution improvement procedure.
        For each base sol, a separate process is executed (or multiple sols per process
        if not enough processe available.)
        """
        promisingSolsPerBase: List[SimILSSolution] = list()
        numProcesses = 4
        pool = Pool(processes=numProcesses)
        processList: List[AsyncResult] = list()
        print("MULTIPROCESSING")
        for p in range(numProcesses):
            print(p)
            
            start = p
            stop = len(baseSols)+1
            step = numProcesses
            print(baseSols[start:stop:step])
            processList.append(pool.apply_async(self.__multiprocessBaseSolsHandler__, args = (baseSols[start:stop:step],maxIter)))
        
        pool.close()
        pool.join()
        print("joined")
        for p in range(numProcesses):
            start = p
            stop = len(baseSols) + 1
            step = numProcesses
            print(processList[p].get())
            promisingSolsPerBase += processList[p].get()  
        return promisingSolsPerBase

    def __multiprocessBaseSolsHandler__(self,baseSols: List[SimILSSolution], maxIter: int):
        """
        Takes one or multiple baseSols and for each does the solution improvement.
        """
        promisingSolsPerBase: List[SimILSSolution] = list()
        for baseSol in baseSols:
            promisingSolsPerBase += self.__improveSolutionPerBaseSol__(baseSol,maxIter)
        return promisingSolsPerBase

    def __improveSolutionPerBaseSol__(self,baseSol: SimILSSolution, maxIter: int):
        """
        Given a baseSol, improves the solution using pertubation, local search and
        an improved CWS heuristic.
        """
        myCWS = self.sr_gcws_cs
        baseSol = myCWS.highQualityRoutingProcess(baseSol, nIter = 50, nIterPerSplit= 5)
        mcSimNew = self.MCSimulation
        baseSol.simulatedRoutingCost = mcSimNew.doIteratedSimulation(baseSol,500)
        promisingSols = self.__updatePromisingSolsList__(baseSol)
        tempForSA = 100
        #maxIter = 0
        for i in range(maxIter):
            availableSols = [baseSol] +promisingSols #+ 
            baseSol = random.choice(availableSols,1)[0]
            print("Iteration " + str(i) + " of " + str(maxIter) + " with Base Sol Totalcost: " + str(baseSol.totalCost))
            newMappedSol = self.__pertubateMap__(deepcopy(baseSol),maxIter, i)
            
            newSol = myCWS.highQualityRoutingProcess(newMappedSol, nIter = 50, nIterPerSplit= 5)
            mcSimNew = self.MCSimulation
            newSol.simulatedRoutingCost = mcSimNew.doIteratedSimulation(newSol,500)
            improving = True

            promisingSols = self.__updatePromisingSolsList__(newSol, promisingSols)

            #localSearchClass = self.localSearch
            localSearchLimitClass = LocalSearchLimit(self.instance)
            while improving:
                tempSol = deepcopy(newSol)
                newSolLS = localSearchLimitClass.doLocalSearchLimit(tempSol,"random",100)
                #newSolLS = localSearchClass.doLocalSearch(tempSol,"random",20)
                #newSolLS = myCWS.highQualityRoutingProcess(newSolLS,nIter = 50, nIterPerSplit=5)
                mcSimLS = self.MCSimulation
                newSolLS.simulatedRoutingCost = mcSimLS.doIteratedSimulation(newSolLS, 500)
                
                # NOTE: as the opened depots do not change in the solution Improvement phase for each individuall baseSol, 
                # it is sufficient enough to only compare the routing cost. (here: simulated routing cost)
                if newSolLS.simulatedRoutingCost < newSol.simulatedRoutingCost and newSolLS.totalCost != newSol.totalCost:
                    print("Local Search Improved")
                    newSol = deepcopy(newSolLS)
                    promisingSols = self.__updatePromisingSolsList__(newSol, promisingSols)
                else:
                    improving = False
                    #print("Local Search did not improve.")
                    accepted, tempForSA = self.__acceptanceCriterionMet__(baseSol.simulatedRoutingCost, newSol.simulatedRoutingCost, tempForSA)
                    #print("Accepted" + str(accepted))
                    if accepted:
                        baseSol = deepcopy(newSol)
        return promisingSols

    def __acceptanceCriterionMet__(self,oldSolCost: float, newSolCost: float, temp: float):
        """
        based on the estimated cost (not simulated cost) of a solution.
        """
        accepted = False
        # Demon based
        #if oldSolCost * 1.5 > newSolCost:
        #    accepted = True
        # Simualted Annealing
        accepted, temp = self.__simulatedAnnealingAccepted__(temp, costDifference=(oldSolCost-newSolCost)/(oldSolCost)*100)

        return accepted, temp

    def __simulatedAnnealingAccepted__(self,temp: float = 100, coolingFactor: float = 0.994, costDifference: float = 0):
        """
        Returns True if sol is accepted by Simulated Annealing.

        :params costDifference: Difference between oldCost - newCost. Needs to be negative.
        """
        rng = random.default_rng()
        accepted = False
        if costDifference >= 0:
            accepted = True
        elif temp > 0 and costDifference < 0:
            p = math.exp(costDifference/temp)
            if rng.uniform(0,1)<p:
                accepted = True
            else:
                accepted = False
            temp -= coolingFactor
        return accepted, temp

    def __updatePromisingSolsList__(self,sol: SimILSSolution, promisingSols: List[SimILSSolution] = list()):
        """
        based on the estimated cost (not simulated cost) of a solution.
        Keep top 10 solutions found so far. 
        """
        promisingSols.sort(key = lambda x: x.totalCost)
        if len(promisingSols)<10:
            promisingSols.append(sol)
            print("##################################### NEW SOL DUE TO BELOW 10 "+ str(sol.totalCost))
        else:
            for pSol in promisingSols:
                if pSol.totalCost > sol.totalCost:
                    print("##################################### NEW BETTER TOP 10 SOL " + str(sol.totalCost) + " at pos " + str(promisingSols.index(pSol)))
                    promisingSols.remove(pSol)
                    promisingSols.append(sol)
                    return promisingSols
        return promisingSols


    def __pertubateMap__(self,sol: SimILSSolution, maxIter: int, currentIteration: int):
        """
        Changes the allocation of the given SimILSSolution using one of two random chosen methods: 
        Either pPercent-Exchange or randomReassignment.
        :param sol: SimILSSolution that should be "pertubated"

        ## Returns

        Returns the given SimILSSolution with a new assignmentVector, an empty route list, empty pointerVector and empty routingVector.
        The cost attribute of this solution needs to be updated before being used again. 
        """
        #p = max (1,int(currentIteration/maxIter*100))
        p = max(1,math.floor(int(currentIteration/maxIter*100)/10)*5)
        pertubateFunc = random.choice([self.__pPercentExchange__,self.__randomReassignment__], 1)[0]
        #pertubateFunc = self.__randomReassignment__
        sol = pertubateFunc(sol,p)
        return sol

    def __randomSetOfCustomers__(self,sol: SimILSSolution, size: int = 0):
        """
        Returns a number of randomly choosen customers out of all customers.
        Number of customers is either given (size) or random number between
        2 and average number of customers per tour.
        """
        setOfCustomers = list()
        if size == 0:  
            minNumCustomers = 2
            if len(sol.tours)<1:
                sol.printSolution()
                raise ZeroDivisionError("Sol has no tours. \n ")
            maxNumCustomers = len(sol.instance.customers)/len(sol.tours)
            if maxNumCustomers == minNumCustomers:
                randomNumCustomers = minNumCustomers
            elif maxNumCustomers < minNumCustomers:
                raise ValueError("It appears that there are not enough customers on a route to make reassignments?")
            else:
                randomNumCustomers = random.randint(minNumCustomers,maxNumCustomers)
            setOfCustomers = list(random.choice(sol.instance.customers,size = randomNumCustomers, replace=False))
        else:
            setOfCustomers = list(random.choice(sol.instance.customers,size = size, replace=False))
        
        return setOfCustomers



    def __randomReassignment__(self,sol: SimILSSolution, p: int):
        """
        For a given solution with assignment vector, returns a random assignmentVector:
        - selects a set of customers to be reassigned
        - assigns each customer to another randomly picked facility, if it is open and has available capacity
        - doing so, refreshes the used capacity (load) of the facilities
        - returns a sol with new assignmentVector. INPLACE CHANGE!
        - "destroys" (clears) route parameter, pointerVector and routingVector of sol, to stress that those do not correspond with the new assignmentVector.

        :param p: NOT USED
        """
        inst: LRPinstance = sol.instance
        customersToReassign = self.__randomSetOfCustomers__(sol)
        print("Customers to be reassigned: " + str(customersToReassign))
        openFacilities = [f for f in inst.facilities if f in sol.assignmentVector]
        openFacilitiesCap = [inst.facCapacity[inst.facilities.index(f)] for f in openFacilities]
        loadOfOpenFacilities = [sum(inst.expectedDemand[xIndex] for xIndex in range(len(inst.expectedDemand))if sol.assignmentVector[xIndex]==f) for f in openFacilities ]
        if len(openFacilities)==1:
            # no reassignment possible, as only one facility open.
            sol.tours.clear()
            sol.pointerVector.clear()
            sol.routingVector.clear()
            return sol
        for c in customersToReassign:
            cIndex = inst.customers.index(c)
            currentFacility = sol.assignmentVector[cIndex]
            currentFacilityIndex = openFacilities.index(currentFacility)
            availableFacilities = [openFacilities[xIndex] for xIndex in range(len(openFacilities)) if openFacilities[xIndex] != currentFacility and loadOfOpenFacilities[xIndex]+inst.expectedDemand[cIndex]<= openFacilitiesCap[xIndex]]
            if len(availableFacilities)== 0:
                # no pertubation possible, as no other facility is open or no facility capacity is free
                #print("Customer " + str(c) + " can not be reassigned as no facilities available.")
                continue
            else:
                randomNewFacility = random.choice(availableFacilities,1)[0]
                randomNewFacilityIndex = openFacilities.index(randomNewFacility)
                sol.assignmentVector[cIndex] = randomNewFacility
                loadOfOpenFacilities[randomNewFacilityIndex] += inst.expectedDemand[cIndex]
                loadOfOpenFacilities[currentFacilityIndex] -= inst.expectedDemand[cIndex]
        # "Destroy" the solution.
        sol.tours.clear()
        sol.pointerVector.clear()
        sol.routingVector.clear()
        #print(sol.assignmentVector)
        return sol
        

    def __pPercentExchange__(self,sol: SimILSSolution, p: int = 5):
        """
        For a given solution with assignmentVector, return a sol with a new assignmentVector. INPLACE CHANGE!
        - exchanges p% of customers with each other
        - therefore creating new assignmentVector
        - exchanges at least two customer with each other
        - exchanges only, if facility capacity is not reached.
        :param p: percentage of customers to be reassigned/exchanged
        """
        #print(p)
        inst = sol.instance
        newAssignmentVector = list(sol.assignmentVector)
        #print("Before pPercent: " + str(newAssignmentVector))
        numCustomersLimit = max(math.ceil(len(inst.customers)*p/100),2)
        customersToExchange = self.__randomSetOfCustomers__(sol,numCustomersLimit)
        #print("Customers to be exchanged: " + str(customersToExchange))
        openFacilities = [f for f in inst.facilities if f in sol.assignmentVector]
        openFacilitiesCap = [inst.facCapacity[inst.facilities.index(f)] for f in openFacilities]
        if len(openFacilities)==1:
            # no reassignment possible, as only one facility open.
            sol.tours.clear()
            sol.pointerVector.clear()
            sol.routingVector.clear()
            return sol
        while len(customersToExchange)>1:
            c1 = customersToExchange.pop()
            c1Index = inst.customers.index(c1)
            c2 = customersToExchange.pop()
            c2Index = inst.customers.index(c2)
            fOfC1 = newAssignmentVector[c1Index]
            fOfC2 = newAssignmentVector[c2Index]
            newAssignmentVector[c1Index] = fOfC2
            newAssignmentVector[c2Index] = fOfC1
            loadOfOpenFacilities = [sum(inst.expectedDemand[xIndex] for xIndex in range(len(inst.expectedDemand))if newAssignmentVector[xIndex]==f) for f in openFacilities ]
            if True in [True if loadOfOpenFacilities[fIndex] > openFacilitiesCap[fIndex] else False for fIndex in range(len(loadOfOpenFacilities)) ]:
                #print("Capacity overload after exchange. Fallback to initial sol.")
                return sol
        sol.tours.clear()
        sol.pointerVector.clear()
        sol.routingVector.clear()
        sol.assignmentVector = newAssignmentVector
        #print("After pPercent: " + str(newAssignmentVector))
        return sol
