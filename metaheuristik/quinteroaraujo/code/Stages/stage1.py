import numpy
import math
from typing import List
from copy import deepcopy

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance

#import cws_custom as cws
import metaheuristik.quinteroaraujo.code.cws_custom as cws
CWSInterface = cws.CWSInterface

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution
MCSimulation = SimObj.MCSimulation

class Stage1:
    """
    Stage 1 is the first Stage of the SimILS metaheuristic.
    It creates an initial solution that is refined in the second Stage.
    """
    def __init__(self, instance: LRPinstance):
        self.instance = instance
        #self.sol = SimILSSolution(instance)
        self.simulation = MCSimulation(instance)
        self.cwsI = CWSInterface(instance)

    def __getLowerboundNumFacilities__(self,instance: LRPinstance):
        """
        Returns the minimum amount of open depots,
        defined by the sum of expected demands and the highest facility capacity.
        """
        return  math.ceil(sum(instance.expectedDemand)/instance.getMaxFacilityCapacity())

    def __facilityCombinations__(self,nComb: int, instance: LRPinstance, lowerbound: int, upperbound: int):
        """
        For each number between lowerbound and upperbound of facilities to be opened,
        creates nComb of combinations of opened facilities.
        """
        nCombSet = []
        #for numOpenFac in range(lowerbound(instance), len(instance.facilities)+1):
        for numOpenFac in range(lowerbound, upperbound+1):
            combSetofSizeNum = []
            for _ in range(0,nComb):
                openFacilities = [0]*len(instance.facilities) #0=closed, 1=open
                # create set of exactly numOpenFac facilities
                availableFacilities = [i for i in range(len(instance.facilities))]
                for _ in range(1, numOpenFac+1):
                    facility = numpy.random.choice(availableFacilities,1,False).tolist()[0]
                    availableFacilities.remove(facility)
                    openFacilities[facility] = 1
                if openFacilities not in combSetofSizeNum:
                    combSetofSizeNum.append(openFacilities)
            nCombSet.append(combSetofSizeNum)
        return nCombSet
            

    def __fastAllocationAndRouting__(self,instance: LRPinstance, combSet: List[int]):
        """
        Create a solution for each combination of open facilities in combSet
        using fast allocation of customers and routing heuristics (here: CWS).
        :param instance: instance Object
        :param combSet: Set containing the open facilities, eg. [0,1,1,0],[0,0,1,1] if facility 2 and 3 are open, rest closed; and 3,4 open, rest closed.
        """
        solSet: List[SimILSSolution] = list()
        for facCombination in combSet:
            sol = SimILSSolution(instance)
            sol.randomSolution(facCombination) 
            cI = self.cwsI
            routingVector, pointerVector, totalCost, _ = cI.CWSforAssignmentVector(sol,sol.assignmentVector)
            sol.routingVector = routingVector
            sol.pointerVector = pointerVector
            sol.__getDepotCost__()
            sol.totalCost = sol.depotCost+totalCost
            solSet.append(sol)
        return solSet

    def __averageSolCost__(self,solSet: List[SimILSSolution]):
        """
        For a given set of solutions,
        returns the average total cost.
        """
        sumCost = 0
        numSols = 0
        for sol in solSet:
            sumCost += sol.totalCost
            numSols +=1

        if numSols > 0:
            return sumCost/numSols
        else:
            raise Exception("NumSols is zero.")

    def __reasonableNumberOfFacilities__(self,instance: LRPinstance):
        """
        Returns the number of opened facilities,
        for which the lowest average total costs are created.
        """
        reasonableL = len(instance.facilities)
        minAvgCost = None
        lowerbound = self.__getLowerboundNumFacilities__(instance)
        upperbound = len(instance.facilities)
        bound =[x for x in range(lowerbound, upperbound+1)]
        facCombs = self.__facilityCombinations__(30,instance, lowerbound, upperbound)
        for lIndex, l in enumerate(bound):
            solsWithLOpenDepots = self.__fastAllocationAndRouting__(instance,facCombs[lIndex])
            averageCostL = self.__averageSolCost__(solsWithLOpenDepots)
            if minAvgCost is None:
                reasonableL = l
                minAvgCost = averageCostL
            elif averageCostL < minAvgCost:
                reasonableL = l
                minAvgCost = averageCostL
        return reasonableL


    def __computeMinMaxRequiredDepots__(self,instance: LRPinstance):
        """
        creates the lower bound and upper bound of number of facilities, that are "reasonable".
        Returns (lb,ub)
        """
        lr = self.__reasonableNumberOfFacilities__(instance)
        lb = self.__getLowerboundNumFacilities__(instance)
        lb = max(lr-1, lb)
        ub = len(instance.facilities)
        ub = min(lr+1,ub)
        return lb, ub


    def __marginalSavings__(self,instance: LRPinstance, depotVector: List):
        """
        For each facility, sorts the customers
        based on the marignal savings if customer
        gets assigned to this facility instead of the second best facility.
        """
        facMarginalSavingsList = list()
        for fIndexA, fA in enumerate(instance.facilities):
            listSortedBySavings = list()
            for cIndex, c in enumerate(instance.customers):
                distanceA = instance.distanceMatrix[fA][c]
                minDistance = None
                for fIndexB in [x for x in range(len(instance.facilities)) if x != fIndexA and depotVector[x]==1]:
                    fB = instance.facilities[fIndexB]
                    distanceB = instance.distanceMatrix[fB][c]
                    if minDistance is None:
                        minDistance = distanceB
                    elif distanceB < minDistance:
                        minDistance = distanceB
                if minDistance is not None:
                    savings = minDistance - distanceA
                else:
                    savings = 0
                listSortedBySavings.append([c,savings])
            listSortedBySavings.sort(key=lambda x: -x[1])
            facMarginalSavingsList.append(listSortedBySavings)
        return facMarginalSavingsList


    def __diminishingProbability__(self,instance: LRPinstance, depotVector: List):
        """
        For each facility, orders the customers by savings (descending) 
        and assigns a diminishing probability to each customer per facility, 
        using a geometric function with alpha in [0.05,0.80].

        Note: The probability values are identical for the facilities at the same "order position".

        ## Returns
        - nested list of facility and customer and probability combinations, i.e. [[[5,0.78],[3,0.15],...],[[3,0.86],[4,0.09],...]]

        """
        savingsList = self.__marginalSavings__(instance, depotVector)
        diminishingProbFacsList = list()
        alpha = numpy.random.rand()*0.75+0.05
        for fIndex, f in enumerate(instance.facilities):
            diminishingProbList = list()
            for cIndex in range(len(instance.customers)):
                k = cIndex+1
                c = savingsList[fIndex][cIndex][0]
                p = self.__geometricFunction__(alpha,k)
                diminishingProbList.append([c,p])
            diminishingProbFacsList.append(diminishingProbList)
        return diminishingProbFacsList

    def __geometricFunction__(self,alpha: int, k: int):
        """
        returns the value of a geometric function with alpha and k.

        Pr(X=k) = (1-alpha)^(k-1) * alpha
        """
        val = pow(1-alpha,k-1)*alpha
        return val


    def __roundrobinAllocation__(self,instance: LRPinstance, depotVector: List[int]):
        """
        :param depotVector: List of length number of facilities, representing if facility is open (1) or closed (0); i.e. [0,0,1,1] representing depot 1 and 2 closed, depot 3 and 4 opened.
        
        1. Schleife: zum Sicherstellen, dass jeder Kunde zugeordnet wurde.
        2. Schleife: Für jeden Standort, 
            - erzeuge einen Monte Carlo Zufallswert (roundRobinVal).
        3. Schleife: Für jeden Kunden in der dimProbList,
            - erhöhe den Wert von distributionFunc um den Wert der normalisierten Zuordnungswahrscheinlichkeit dieses Kunden zu diesem Standort
            - wenn distrbutionFunc grüßer als roundRobinVal, dann ordne den aktuellen Kunden(Index) dem Standort zu
            - entferne Kunden (Index) aus Liste der zuzuordnenden Kunden (dimProblist)
            - beende die 3. Schleife, setze in 2. Schleife mit nächstem Standort fort. 

        """
        assignmentVector = ["XX"]*len(instance.customers)
        dimProbList = self.__diminishingProbability__(instance, depotVector)
        dimProbList = self.__normalizeDiminishingProbability__(dimProbList)
        for cIndex, c in enumerate(instance.customers):
            for fIndex in [x for x in range(len(instance.facilities)) if depotVector[x]==1]:
                f = instance.facilities[fIndex]
                roundRobinVal = numpy.random.rand()
                distributionFunc = 0
                for cIndexB in range(len(instance.customers)):
                    if cIndexB < len(dimProbList[fIndex]):
                        distributionFunc += dimProbList[fIndex][cIndexB][1]
                        if distributionFunc >= roundRobinVal:
                            assignedC = dimProbList[fIndex][cIndexB][0]
                            assignedCIndex = instance.customers.index(assignedC)
                            assignmentVector[assignedCIndex] = f
                            dimProbList[fIndex].pop(cIndexB)
                            # also pop in the other facilities
                            for fIndexPop in range(len(instance.facilities)):
                                for cIndexPop in range(len(instance.customers)):
                                    if cIndexPop < len(dimProbList[fIndexPop]):
                                        cPop = dimProbList[fIndexPop][cIndexPop][0]
                                        if cPop == assignedC:
                                            dimProbList[fIndexPop].pop(cIndexPop)
                            dimProbList = self.__normalizeDiminishingProbability__(dimProbList)
                            break
                    

        return assignmentVector

    def __normalizeDiminishingProbability__(self,dimProbList: List[int]):
        """
        Normalize the diminishing Probability
        so that it adds up to 1
        """
        normedDimProbList = list(dimProbList)
        for fIndex, dimProbListOfFacility in enumerate(dimProbList):
            if len(dimProbListOfFacility)>0:
                probSum = 0
                for cIndex, cProb in enumerate(dimProbListOfFacility):
                    probSum += cProb[1]
                for cIndex, cProb in enumerate(dimProbListOfFacility):
                    normedDimProbList[fIndex][cIndex][1] = cProb[1]/probSum

        return normedDimProbList


    def feasibleSolutionGenerator(self, maxSafetystock: int = 10, numSim: int = 10, numFacilitySets: int = 1000):
        """
        Generates Base Solutions with reasonable number of open facilities, creating routes using CWS and
        simulation demands to find best route and safetystock combination.
        :param instance: LRPInstance
        :param safetystock: Safetystock in %, meaning % are reserved of vehicleCap and therefore vehicleCap is reduced by % during CWS.
        :param numSim: number of simulation iterations "Fast Simulation"
        :param numFacilitySets: max number of combinations of open facilities. For each combination/set a fast allocation and routing heuristic (CWS) is executed.
        """
        instance = self.instance
        lb,ub = self.__computeMinMaxRequiredDepots__(instance)
        print("Bounds for number of facilites are " + str(lb) + " and " + str(ub))
        depotVectorsList = self.__createDepotVectors__(instance, lb, ub, numFacilitySets, unique = True)
        feasibleSols = list()
        for depotVectorIndex, depotVector in enumerate(depotVectorsList):
            print(depotVectorIndex)
            assignmentVector = self.__roundrobinAllocation__(instance,depotVector)
            bestSS = None
            bestSimRoutingCost = None
            for ss in range(0,maxSafetystock+1):
                sol = SimILSSolution(instance,ss=ss)
                sol.depotVector = depotVector
                sol.assignmentVector = assignmentVector
                cI = self.cwsI
                routingVector, pointerVector, totalCost, routes = cI.CWSforAssignmentVector(sol,sol.assignmentVector)
                sol.routingVector = routingVector
                sol.pointerVector = pointerVector
                sol.__getDepotCost__()
                if len(routes)> 0:
                    sol.createTours(routes)
                mcsim = self.simulation
                avgSimRoutingCost = mcsim.doIteratedSimulation(sol,numSim)
                if bestSS is None or avgSimRoutingCost < bestSimRoutingCost:
                    bestSS = ss
                    bestSimRoutingCost = avgSimRoutingCost
                    sol.simulatedRoutingCost = bestSimRoutingCost
                    sol.simulatedTotal = sol.depotCost + sol.simulatedRoutingCost
                    bestSSsol = deepcopy(sol)
                
            print("Best SS for depotVector " + str(depotVector) + " at " + str(bestSS) + " % with routingCost " + str(bestSimRoutingCost) + ".")        
            
            #sol.totalCost = sol.depotCost+totalCost
            feasibleSols.append(bestSSsol)
        return feasibleSols

    def __createDepotVectors__(self,instance: LRPinstance, lb: int, ub: int, numOfDepotVectors: int, unique = False):
        """
        :param unique: True = onyl distinct/"unique" depotVectors are returned; 
            False = returned list may contain dupilcates of depotVectors
        """
        depotVectorsList = list()
        numIter = 0
        numUniqueDepotVectors = 0
        if unique:
            for i in range(lb,ub+1):
                numUniqueDepotVectors += math.factorial(len(instance.facilities))/(math.factorial(i)*math.factorial(len(instance.facilities)-i))
        else:
            numUniqueDepotVectors = numOfDepotVectors
        #numUniqueDepotVectors = math.pow(2,len(instance.facilities))-1
        while(numIter<numOfDepotVectors and numIter < numUniqueDepotVectors):
            depotVector = [0]*len(instance.facilities)
            numOpenFac = numpy.random.randint(lb, ub+1)
            availableFacilities = [i for i in range(len(instance.facilities))]
            for _ in range(1, numOpenFac+1):
                fIndex = numpy.random.choice(availableFacilities,1,False).tolist()[0]
                availableFacilities.remove(fIndex)
                depotVector[fIndex] = 1
            if depotVector not in depotVectorsList or not unique:
                depotVectorsList.append(depotVector)
                numIter += 1
        return depotVectorsList