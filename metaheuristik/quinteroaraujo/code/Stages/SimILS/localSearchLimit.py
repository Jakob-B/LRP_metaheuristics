from copy import deepcopy
import enum
from numpy import random
from typing import List, Tuple
import itertools

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Tour = LRPObj.Tour
LRPinstance = LRPObj.LRPinstance

import metaheuristik.quinteroaraujo.code.cws_custom as cws
CWSInterface = cws.cwsInterface.CWSInterface

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution

class LocalSearchLimit:
    def __init__(self, instance: LRPinstance):
        self.instance: LRPinstance = instance
        self.cwsI = CWSInterface(instance)
        self.limit = 0
    
    def doLocalSearchLimit(self,simSol: SimILSSolution, lsOperator: str, limit: int):
        self.limit = limit
        randomlsOperator = False
        #lsOperator = "IV"
        if lsOperator == "random":
            randomlsOperator = True
        elif lsOperator == "I" or lsOperator == "II" or lsOperator == "III" or lsOperator == "IV" or lsOperator == "V":
            randomlsOperator = False    
        if randomlsOperator:
            lsOperator = str(random.choice(["I", "II", "III", "IV", "V"],1)[0]) #
                        
        if lsOperator == "I":
            localSearchFunc = self.__manageLimitedCustomerSwapInterRoute__
        elif lsOperator == "II":
            localSearchFunc = self.__manageLimitedInterDepotNodeExchange__
        elif lsOperator == "III":
            localSearchFunc = self.__manage2OptInterRoute__
        elif lsOperator == "IV":
            localSearchFunc = self.__manageCrossExchange__
        elif lsOperator == "V":
            localSearchFunc = self.__manageCustomerTransferInterRoute__
            
        newSimSol = localSearchFunc(deepcopy(simSol))
        if newSimSol.totalCost<simSol.totalCost:
            print(str(lsOperator) + " improved Solution.")
        return newSimSol

    def __manageCustomerTransferInterRoute__(self, simSol: SimILSSolution):
        return self.__manageLimitedCustomerSwapInterRoute__(simSol, True)

    def __manageCrossExchange__(self, simSol: SimILSSolution):
        bestSol = deepcopy(simSol)
        inst = simSol.instance 
        possibleSwaps = []
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]   
        if len(openFacilities)>1:
            facilityCombinations = [(f1,f2) for f1 in openFacilities for f2 in openFacilities if f1<f2]
            for fComb in facilityCombinations:
                f1, f2 = fComb
                toursOfFacility1 = self.__toursOfFacility__(simSol, f1)
                toursOfFacility2 = self.__toursOfFacility__(simSol, f2) 
                customersOfTours1 = self.__customersOfTours__(toursOfFacility1)
                customersOfTours2 = self.__customersOfTours__(toursOfFacility2)
                customersOfFacility1 = [(c, tIndex) for tIndex, t in enumerate(customersOfTours1) for c in t]
                customersOfFacility2 = [(c, tIndex) for tIndex,t in enumerate(customersOfTours2) for c in t]
                triples1 = [(c1,c2,c3) 
                    for pos1,(c1,tIndex1) in enumerate(customersOfFacility1) 
                    for pos2,(c2,tIndex2) in enumerate(customersOfFacility1) 
                    for pos3,(c3,tIndex3) in enumerate(customersOfFacility1) 
                    if pos1 < pos2 and pos2 < pos3 and (pos1+1<pos2 or tIndex1 != tIndex2) and (pos2+1<pos3 or tIndex2!=tIndex3)
                ]
                triples2 = [(c1,c2,c3) 
                    for pos1,(c1,tIndex1) in enumerate(customersOfFacility2) 
                    for pos2,(c2,tIndex2) in enumerate(customersOfFacility2) 
                    for pos3,(c3,tIndex3) in enumerate(customersOfFacility2) 
                    if pos1 < pos2 and pos2 < pos3 and (pos1+1<pos2 or tIndex1 != tIndex2) and (pos2+1<pos3 or tIndex2!=tIndex3)
                ]
                possibleSwaps+=[(f1,f2,trip1, trip2) for trip1 in triples1 for trip2 in triples2]
        chosenSwapsIndices = list(random.choice(len(possibleSwaps),min(self.limit,len(possibleSwaps)),replace=False))
        chosenSwaps = [swap for index, swap in enumerate(possibleSwaps) if index in chosenSwapsIndices]
        for swap in chosenSwaps:
            newSimSol = self.__crossExchange__(deepcopy(simSol),swap)
            if newSimSol.totalCost < bestSol.totalCost:
                bestSol = deepcopy(newSimSol)
        return bestSol  

    def __manage2OptInterRoute__(self, simSol: SimILSSolution):
        bestSol = deepcopy(simSol)
        inst = simSol.instance 
        possibleSwaps = []
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        if len(openFacilities)>1:
            facilityCombinations = [(f1,f2) for f1 in openFacilities for f2 in openFacilities if f1<f2]
            for fComb in facilityCombinations:
                f1, f2 = fComb
                toursOfFacility1 = self.__toursOfFacility__(simSol, f1)
                toursOfFacility2 = self.__toursOfFacility__(simSol, f2)
                customerPairs1 = []
                for t1 in toursOfFacility1:
                    customersOfTour = self.__customersOfTours__([t1])[0]
                    if len(customersOfTour) > 1:
                        customerPairs1 += [(c1,customersOfTour[c1Index+1]) for c1Index, c1 in enumerate(customersOfTour) if c1Index < len(customersOfTour)-1]
                customerPairs2 = []
                for t2 in toursOfFacility2:
                    customersOfTour = self.__customersOfTours__([t2])[0]
                    if len(customersOfTour) > 1:
                        customerPairs2 += [(c1,customersOfTour[c1Index+1]) for c1Index, c1 in enumerate(customersOfTour) if c1Index < len(customersOfTour)-1]
                if len(customerPairs2)>0 and len(customerPairs1)>0:
                    possibleSwaps+=[(f1,f2,pair1,pair2) for pair1 in customerPairs1 for pair2 in customerPairs2]
        chosenSwapsIndices = list(random.choice(len(possibleSwaps),min(self.limit,len(possibleSwaps)),replace=False))
        chosenSwaps = [swap for index, swap in enumerate(possibleSwaps) if index in chosenSwapsIndices]
        for swap in chosenSwaps:
            newSimSol = self.__twoOptInterRoute__(deepcopy(simSol),swap)
            if newSimSol.totalCost < bestSol.totalCost:
                bestSol = deepcopy(newSimSol)
        return bestSol

    def __manageLimitedCustomerSwapInterRoute__(self,simSol: SimILSSolution, onlyTransfer = False):
        bestSol = deepcopy(simSol)
        inst = simSol.instance 
        possibleSwaps = []
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        for fIndex,f in enumerate(openFacilities):
            # list of routes of list of customers
            toursOfFacility = self.__toursOfFacility__(simSol, f)
            customersOfTours = self.__customersOfTours__(toursOfFacility)
            possibleSwaps += [(f,cXs,cYs)  for tXIndex,tX in enumerate(customersOfTours) for cXs in tX for tYIndex, tY in enumerate(customersOfTours) for cYs in tY if tXIndex < tYIndex]
            #print(possibleSwaps)
        chosenSwapsIndices = list(random.choice(len(possibleSwaps),min(self.limit,len(possibleSwaps)),replace=False))
        chosenSwaps = [swap for index, swap in enumerate(possibleSwaps) if index in chosenSwapsIndices]
        for swap in chosenSwaps:
            newSimSol = self.__customerSwapInterRoute__(deepcopy(simSol),swap)
            if newSimSol.totalCost < bestSol.totalCost:
                bestSol = deepcopy(newSimSol)
        return bestSol

    def __manageLimitedInterDepotNodeExchange__(self,simSol: SimILSSolution):
        bestSol = deepcopy(simSol)
        inst = simSol.instance
        possibleSwaps = []
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        if len(openFacilities)>1:
            facilityCombinations = [(f1,f2) for f1 in openFacilities for f2 in openFacilities if f1<f2]
            for fComb in facilityCombinations:
                f1, f2 = fComb
                customersOfFaclilty1 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f1]
                customersOfFaclilty2 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f2]
                possibleSwaps += [(f1,f2,c1,c2) for c1Index, c1 in enumerate(customersOfFaclilty1) for c2Index,c2 in enumerate(customersOfFaclilty2)]
        chosenSwapsIndices = list(random.choice(len(possibleSwaps),min(self.limit,len(possibleSwaps)),replace=False))
        chosenSwaps = [swap for index, swap in enumerate(possibleSwaps) if index in chosenSwapsIndices]
        for swap in chosenSwaps:
            newSimSol = self.__interDepotNodeExchangeNewTours__(deepcopy(simSol),swap)
            if newSimSol.totalCost < bestSol.totalCost:
                bestSol = deepcopy(newSimSol)
        return bestSol

    def __interDepotNodeExchange__(self, simSol: SimILSSolution, swap: Tuple):
        f1, f2, c1, c2 = swap
        toursF1 = self.__toursOfFacility__(simSol,f1)
        for t in toursF1:
            t: Tour
            tourCustomers = self.__customersOfTours__([t])[0]
            if c1 in tourCustomers:
                tourC1Customers = tourCustomers
                tourC1 = t
        toursF2 = self.__toursOfFacility__(simSol,f2)
        for t in toursF2:
            t: Tour
            tourCustomers = self.__customersOfTours__([t])[0]
            if c2 in tourCustomers:
                tourC2Customers = tourCustomers
                tourC2 = t
        tourC1Customers.remove(c1)
        tourC2Customers.remove(c2)
        tourC1Customers.append(c2)
        tourC2Customers.append(c1)
        simSol.tours.remove(tourC1)
        simSol.tours.remove(tourC2)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, tourC1Customers,f1)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, tourC2Customers,f2)
        simSol.simulatedRoutingCost = 0
        simSol.simulatedTotal = 0
        simSol.__getTotalCost__()
        simSol.updateAssignmentVectorByTours()
        return simSol

    def __interDepotNodeExchangeNewTours__(self, simSol: SimILSSolution, swap: Tuple):
        inst = simSol.instance
        f1, f2, c1, c2 = swap
        customersOfFaclilty1 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f1]
        customersOfFaclilty2 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f2]
        toursF1 = self.__toursOfFacility__(simSol,f1)
        toursF2 = self.__toursOfFacility__(simSol,f2)
        for t in toursF1 + toursF2:
            simSol.tours.remove(t)
        customersOfFaclilty1.remove(c1)
        customersOfFaclilty2.remove(c2)
        customersOfFaclilty1.append(c2)
        customersOfFaclilty2.append(c1)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty1,f1)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty2,f2)
        simSol.simulatedRoutingCost = 0
        simSol.simulatedTotal = 0
        simSol.__getTotalCost__()
        simSol.updateAssignmentVectorByTours()
        return simSol

    def __twoOptInterRoute__(self, simSol: SimILSSolution, swap: Tuple):
        inst = simSol.instance
        f1, f2, pair1, pair2 = swap
        p1c1, p1c2 = pair1
        p2c1, p2c2 = pair2
        customersOfFaclilty1 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f1]
        customersOfFaclilty2 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f2]
        toursF1 = self.__toursOfFacility__(simSol,f1)
        toursF2 = self.__toursOfFacility__(simSol,f2)
        for t in toursF1 + toursF2:
            simSol.tours.remove(t)
        customersOfFaclilty1.remove(p1c1)
        customersOfFaclilty1.remove(p1c2)
        customersOfFaclilty2.remove(p2c1)
        customersOfFaclilty2.remove(p2c2)
        customersOfFaclilty1.append(p2c2)
        customersOfFaclilty1.append(p2c1)
        customersOfFaclilty2.append(p1c1)
        customersOfFaclilty2.append(p1c2)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty1,f1)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty2,f2)
        simSol.simulatedRoutingCost = 0
        simSol.simulatedTotal = 0
        simSol.__getTotalCost__()
        simSol.updateAssignmentVectorByTours()
        return simSol

    def __customerSwapInterRoute__(self,simSol: SimILSSolution, swap: Tuple, onlyTransfer = False):
        f, c1, c2 = swap
        inst = simSol.instance
        tourC1 = [t for tIndex, t in enumerate(simSol.tours) if t.facility == f and c1 in t.routeVector][0]
        tourC2 = [t for tIndex, t in enumerate(simSol.tours) if t.facility == f and c2 in t.routeVector][0]
        tourC1Customers = self.__customersOfTours__([tourC1])[0]
        tourC2Customers = self.__customersOfTours__([tourC2])[0]
        tourC1Customers.remove(c1)
        tourC2Customers.append(c1)
        if not onlyTransfer:
            tourC2Customers.remove(c2)
            tourC1Customers.append(c2)
        simSol.tours.remove(tourC1)
        simSol.tours.remove(tourC2)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, tourC1Customers,f)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, tourC2Customers,f)
        simSol.simulatedRoutingCost = 0
        simSol.simulatedTotal = 0
        simSol.__getTotalCost__()
        simSol.updateAssignmentVectorByTours()
        return simSol
       
    def __crossExchange__(self,simSol: SimILSSolution, swap: Tuple):
        inst = simSol.instance
        f1, f2, triple1, triple2 = swap
        t1c1, t1c2, t1c3 = triple1
        t2c1, t2c2, t2c3 = triple2
        customersOfFaclilty1 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f1]
        customersOfFaclilty2 = [c for cIndex, c in enumerate(inst.customers) if simSol.assignmentVector[cIndex]==f2]
        toursF1 = self.__toursOfFacility__(simSol,f1)
        toursF2 = self.__toursOfFacility__(simSol,f2)
        for t in toursF1 + toursF2:
            simSol.tours.remove(t)
        customersOfFaclilty1.remove(t1c1)
        customersOfFaclilty1.remove(t1c2)
        customersOfFaclilty1.remove(t1c3)
        customersOfFaclilty2.remove(t2c1)
        customersOfFaclilty2.remove(t2c2)
        customersOfFaclilty2.remove(t2c3)
        customersOfFaclilty1.append(t2c1)
        customersOfFaclilty1.append(t2c2)
        customersOfFaclilty1.append(t2c3)
        customersOfFaclilty2.append(t1c1)
        customersOfFaclilty2.append(t1c2)
        customersOfFaclilty2.append(t1c3)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty1,f1)
        self.__cwsAndSolUpdateWithCustomerSet__(simSol, customersOfFaclilty2,f2)
        simSol.simulatedRoutingCost = 0
        simSol.simulatedTotal = 0
        simSol.__getTotalCost__()
        simSol.updateAssignmentVectorByTours()
        return simSol        
    
    def __cwsAndSolUpdateWithCustomerSet__(self, simSol: SimILSSolution, customerSet: List, facility: int):
        cI = self.cwsI
        cwsSolI, cost, savingsList = cI.CWSforCustomerSet(simSol,customerSet,facility)
        for route in cwsSolI:
            _, routeVectorI = cI.__CWStoRoutingVector__([route])
            newTourI = Tour(routeVectorI,facility,self.instance)
            newTourI.updateRoutingCost()
            newTourI.refineStrategies()
            simSol.tours.append(newTourI)
            simSol.refreshRoutingCost()
        

    def __toursOfFacility__(self, simSol: SimILSSolution, facility: int):
        toursOfFacility = [simSol.tours[tIndex] for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == facility]
        return toursOfFacility

    def __customersOfTours__(self, tourList: List[Tour]):
        customersOfTours = list()
        for t in tourList:
            customers = [c for c in t.routeVector if c != t.facility]
            customersOfTours.append(customers)
        return customersOfTours

    def __multipleListCombinations__(self, lists: List[List]):
        for l in lists:
            1
