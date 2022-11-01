
from copy import deepcopy
from numpy import random
from typing import List

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Tour = LRPObj.Tour
LRPinstance = LRPObj.LRPinstance

import metaheuristik.quinteroaraujo.code.cws_custom as cws
CWSInterface = cws.cwsInterface.CWSInterface

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution

class LocalSearch:
    def __init__(self, instance: LRPinstance):
        self.instance: LRPinstance = instance
        self.cwsI = CWSInterface(instance)

    def doLocalSearch(self,simSol: SimILSSolution, lsOperator: str, iterations: int):
        """
        For a given Simulation LRP Solution, does a local search and returns the best found solution; 
        however, this solution might be worse then the input solution.
        :param simSol: SimILSSolution that is to be improved
        :param lsOperator: defines which LocalSearch should be executed:
        :param iterations: Number of local searches (exchanges/interchanges... depending on LocalSearch Method) should be executed.
        - I: customer Swap Inter Route
        - II: inter Depot Node Exchange
        - III: twoOpt Inter Route
        - IV: cross Exchange
        - random: any of those four, changing during iterations
        """
        bestSimSol = deepcopy(simSol)
        newSimSol = deepcopy(simSol)
        firstLocalSearchSolution = False
        randomlsOperator = False
        #lsOperator = "IV"
        if lsOperator == "random":
            randomlsOperator = True
        elif lsOperator == "I" or lsOperator == "II" or lsOperator == "III" or lsOperator == "IV" or lsOperator == "V":
            randomlsOperator = False
        else:
            raise ValueError("Wrong Operator.")
        for _ in range(10):
            if randomlsOperator:
                lsOperator = str(random.choice(["I", "II", "III", "IV", "V"],1)[0])
                        
            if lsOperator == "I":
                localSearchFunc = self.__customerSwapInterRoute__
                #newSimSol = self.__customerSwapInterRoute__(deepcopy(newSimSol))
            elif lsOperator == "II":
                localSearchFunc = self.__interDepotNodeExchange__
                #newSimSol = self.__interDepotNodeExchange__(deepcopy(newSimSol))
            elif lsOperator == "III":
                localSearchFunc = self.__twoOptInterRoute__
                #newSimSol = self.__twoOptInterRoute__(deepcopy(newSimSol))
            elif lsOperator == "IV":
                localSearchFunc = self.__crossExchange__
                #newSimSol = self.__crossExchange__(deepcopy(newSimSol))
            elif lsOperator == "V":
                localSearchFunc = self.__customerTransferInterRoute__
                #newSimSol = self.__customerTransferInterRoute__(deepcopy(newSimSol))

            for i in range(iterations):
                newSimSol = localSearchFunc(deepcopy(bestSimSol))
            
                if newSimSol.totalCost<bestSimSol.totalCost or firstLocalSearchSolution:
                    print(str(lsOperator) + " improved Solution.")
                    bestSimSol = newSimSol
                    firstLocalSearchSolution = False    
                    i = 0
            
            # Debugging
            if len(newSimSol.tours)<1:
                newSimSol.printSolution()
                raise ValueError("newSimSol has no tours after local search operator " + lsOperator)   
        return bestSimSol

    def __customerTransferInterRoute__(self, simSol: SimILSSolution):
        """
        Transfer one customer of a route to another route of that same facility.
        """
        return self.__customerSwapInterRoute__(simSol,True)

    def __customerSwapInterRoute__(self,simSol: SimILSSolution, onlyTransfer = False):
        """
        Pick a random open facility and two random tours from this facility (if available) 
        and exchange two random customers from those tours. 
        Calculate new routes with CWS and create new tour objects, update the SimSol with those tours. 
        Return updated simSol.
        """
        inst = simSol.instance
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        randomFacility = random.choice(openFacilities,1)[0]
        toursOfRandomFacility = [simSol.tours[tIndex] for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == randomFacility]
        indexOfTours = [tIndex for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == randomFacility]
        if len(toursOfRandomFacility)>1:
            random2Tours: List[Tour] = random.choice(toursOfRandomFacility,size=2, replace=False)
            tourI = random2Tours[0]
            tourIIndex = indexOfTours[toursOfRandomFacility.index(tourI)]
            tourJ = random2Tours[1]
            tourJIndex = indexOfTours[toursOfRandomFacility.index(tourJ)]
            tourICustomers = [c for c in tourI.fullTrip if c != randomFacility]
            tourJCustomers = [c for c in tourJ.fullTrip if c != randomFacility]
            customerI = random.choice(tourICustomers,size=1, replace=False)[0]
            customerJ = random.choice(tourJCustomers,size=1, replace=False)[0]
            if onlyTransfer == False:
                # exchange two customers from different routes.
                tourICustomers[tourICustomers.index(customerI)] = customerJ
                tourJCustomers[tourJCustomers.index(customerJ)] = customerI
            else:
                # transfer one Customer to another route.
                tourICustomers.remove(customerI)
                tourJCustomers.append(customerI)
            # remove old toures from simSol Tour List
            simSol.tours.pop(tourIIndex)
            simSol.routingCosts.pop(tourIIndex)
            # Note: when tourI is popped, the index of tours changes, therefore here checking for index.
            simSol.tours.pop(tourJIndex if tourJIndex < tourIIndex else tourJIndex-1)
            simSol.routingCosts.pop(tourJIndex if tourJIndex < tourIIndex else tourJIndex-1)
            
            # Note: Exchanging the customers might lead to overloading of a single route, resulting in two new routes per overloaded route.
            cI = self.cwsI
            cwsSolI, cost, savingsList = cI.CWSforCustomerSet(simSol,tourICustomers,randomFacility)
            for route in cwsSolI:
                _, routeVectorI = cI.__CWStoRoutingVector__([route])
                newTourI = Tour(routeVectorI,randomFacility,inst)
                newTourI.updateRoutingCost()
                newTourI.refineStrategies()
                simSol.tours.append(newTourI)
                simSol.routingCosts.append(newTourI.routingCost)
            cwsSolJ, cost, savingsList = cI.CWSforCustomerSet(simSol,tourJCustomers,randomFacility)
            for route in cwsSolJ:
                _, routeVectorJ = cI.__CWStoRoutingVector__([route])
                newTourJ = Tour(routeVectorJ,randomFacility,inst)
                newTourJ.updateRoutingCost()
                newTourJ.refineStrategies()
                simSol.tours.append(newTourJ)
                simSol.routingCosts.append(newTourJ.routingCost)
            
            simSol.simulatedRoutingCost = 0
            simSol.simulatedTotal = 0
            simSol.__getTotalCost__()
            simSol.updateAssignmentVectorByTours()
        return simSol


    def __interDepotNodeExchange__(self,simSol: SimILSSolution):
        """
        Pick two random open facilities and random tour from each. From those exchange 2 customers with each other.
        Calculate new routes with CWS and create new tour objects, update the SimSol with those tours. 
        Return updated simSol.
        """
        inst = simSol.instance
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        if len(openFacilities)>1:
            random2Facilities = random.choice(openFacilities,2, replace=False)
            selectedTours: List[Tour] = list()
            selectedCustomers: List[int] = list()
            for randomFacilityIndex, randomFacility in enumerate(random2Facilities):
                toursOfRandomFacility = [simSol.tours[tIndex] for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == randomFacility]
                if len(toursOfRandomFacility)<1:
                    # Facility has no tours, no exchange possible
                    return simSol
                randomTour: Tour = random.choice(toursOfRandomFacility,size=1, replace=False)[0]
                randomTourCustomers = [c for c in randomTour.fullTrip if c != randomFacility]
                randomCustomer = random.choice(randomTourCustomers,size=1, replace=False)[0]
                selectedTours.append(randomTour)
                selectedCustomers.append(randomCustomer)
            # remove selected Tours from simSOl
            simSol.tours.remove(selectedTours[0])
            simSol.tours.remove(selectedTours[1])
            simSol.routingCosts = list()
            # Exchange customers
            tourCustomers = [[c for c in selectedTours[tourIndex].fullTrip if c != random2Facilities[tourIndex]] for tourIndex in range(len(selectedTours))]
            tourCustomers[0][tourCustomers[0].index(selectedCustomers[0])] = selectedCustomers[1]
            tourCustomers[1][tourCustomers[1].index(selectedCustomers[1])] = selectedCustomers[0] 
            # Calculate CWS
            # Note: Exchanging the customers might lead to overloading of a single route, resulting in two new routes per overloaded route.
            cI = self.cwsI
            for tourIndex, customers in enumerate(tourCustomers):
                facility = random2Facilities[tourIndex]
                cwsSol, cost, savingsList = cI.CWSforCustomerSet(simSol,customers,facility)
                for route in cwsSol:
                    _, routeVectorI = cI.__CWStoRoutingVector__([route])
                    newTour = Tour(routeVectorI,randomFacility,inst)
                    newTour.updateRoutingCost()
                    newTour.refineStrategies()
                    simSol.tours.append(newTour)
            # update the simSol routing Costs and total Cost
            simSol.routingCosts = [t.routingCost for t in simSol.tours]
            simSol.simulatedRoutingCost = 0
            simSol.simulatedTotal = 0
            simSol.__getTotalCost__()
            simSol.updateAssignmentVectorByTours()
            
        return simSol

    def __twoOptInterRoute__(self,simSol: SimILSSolution):
        """
        Pick two random open facilities and random tour from each.
        From each of those tours, select a chain of two customers and exchange those chains with each other.
        Requires at least two customers in each tour.
        Calculate new routes with CWS and create new tour objects, update the SimSol with those tours. 
        Return updated simSol.
        """
        inst = simSol.instance
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        if len(openFacilities)>1:
            random2Facilities = random.choice(openFacilities,2, replace=False)
            selectedTours: List[Tour] = list()
            selectedCustomers: List[int] = list()
            for randomFacilityIndex, randomFacility in enumerate(random2Facilities):
                toursOfRandomFacility = [simSol.tours[tIndex] for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == randomFacility]
                if len(toursOfRandomFacility)<1:
                    # Facility has no tours, no exchange possible
                    return simSol
                randomTour: Tour = random.choice(toursOfRandomFacility,size=1, replace=False)[0]
                selectedTours.append(randomTour)
                if len(randomTour.routeVector)<2:
                    # If Tour has only one customer then no chain of length two is possible
                    return simSol
                chainStartIndex = random.randint(0,len(randomTour.routeVector)-1) # dont pick last Customer in route as start for chain
                customerChain: List[int] = randomTour.routeVector[chainStartIndex:chainStartIndex+1+1]
                selectedCustomers.append(customerChain)
            # remove selected Tours from simSOl
            simSol.tours.remove(selectedTours[0])
            simSol.tours.remove(selectedTours[1])
            simSol.routingCosts = list()
            # Exchange customers
            tourCustomers = [[c for c in selectedTours[tourIndex].fullTrip if c != random2Facilities[tourIndex]] for tourIndex in range(len(selectedTours))]
            tourCustomers[0].remove(selectedCustomers[0][0])
            tourCustomers[0].remove(selectedCustomers[0][1])
            tourCustomers[1].remove(selectedCustomers[1][0])
            tourCustomers[1].remove(selectedCustomers[1][1])
            tourCustomers[0].append(selectedCustomers[1][0])
            tourCustomers[0].append(selectedCustomers[1][1])
            tourCustomers[1].append(selectedCustomers[0][0])
            tourCustomers[1].append(selectedCustomers[0][1])
            # Calculate CWS
            # Note: Exchanging the customers might lead to overloading of a single route, resulting in two new routes per overloaded route.
            cI = self.cwsI
            for tourIndex, customers in enumerate(tourCustomers):
                facility = random2Facilities[tourIndex]
                cwsSol, cost, savingsList = cI.CWSforCustomerSet(simSol,customers,facility)
                for route in cwsSol:
                    _, routeVectorI = cI.__CWStoRoutingVector__([route])
                    newTour = Tour(routeVectorI,randomFacility,inst)
                    newTour.updateRoutingCost()
                    newTour.refineStrategies()
                    simSol.tours.append(newTour)
            # update the simSol routing Costs and total Cost
            simSol.routingCosts = [t.routingCost for t in simSol.tours]
            simSol.simulatedRoutingCost = 0
            simSol.simulatedTotal = 0
            simSol.__getTotalCost__()
            simSol.updateAssignmentVectorByTours()
            
        return simSol

    def __crossExchange__(self,simSol: SimILSSolution):
        """
        Pick two random open facilities and 3 random customers from each facility, which are not consecutive.
        Assign each 3 customers to the other facility.
        Calculate new routes with CWS and create new tour objects, update the SimSol with those tours. 
        Return updated simSol.
        """
        inst = simSol.instance
        openFacilities = [inst.facilities[fIndex] for fIndex in range(len(inst.facilities)) if simSol.depotVector[fIndex]==1]
        if len(openFacilities)>1:
            random2Facilities = random.choice(openFacilities,2, replace=False)
            selectedTours: List[Tour] = list()
            selectedCustomers: List[List[int]] = [list(), list()]
            facilitiesCustomers: List[List[int]] = [[inst.customers[cIndex] for cIndex in range(len(simSol.assignmentVector)) if simSol.assignmentVector[cIndex]==f] for f in random2Facilities]
            for randomFacilityIndex, randomFacility in enumerate(random2Facilities):
                toursOfRandomFacility = [simSol.tours[tIndex] for tIndex in range(len(simSol.tours)) if simSol.tours[tIndex].facility == randomFacility]
                availableCustomersPerTour = [t.routeVector for t in toursOfRandomFacility]
                availableCustomers = [j for i in availableCustomersPerTour for j in i]
                for _ in range(3):
                    if len(availableCustomers)<1:
                        continue
                    customer = random.choice(availableCustomers,size=1, replace=False)[0]
                    customersOfTourOfChosenCustomer = [availableCustomersPerTour[iIndex] for iIndex in range(len(availableCustomersPerTour)) if customer in availableCustomersPerTour[iIndex]][0]
                    tourIndex = availableCustomersPerTour.index(customersOfTourOfChosenCustomer)
                    customerIndex = customersOfTourOfChosenCustomer.index(customer)
                    if customerIndex == len(customersOfTourOfChosenCustomer)-1:
                        if customerIndex == 0:
                            customersOfTourOfChosenCustomer.remove(customer)
                        else:
                            leftCustomer = customersOfTourOfChosenCustomer[customerIndex-1]
                            customersOfTourOfChosenCustomer.remove(customer)
                            customersOfTourOfChosenCustomer.remove(leftCustomer)
                    elif customerIndex == 0:
                        rightCustomer = customersOfTourOfChosenCustomer[customerIndex+1]
                        customersOfTourOfChosenCustomer.remove(customer)
                        customersOfTourOfChosenCustomer.remove(rightCustomer)
                    else:
                        leftCustomer = customersOfTourOfChosenCustomer[customerIndex-1]
                        rightCustomer = customersOfTourOfChosenCustomer[customerIndex+1]
                        customersOfTourOfChosenCustomer.remove(leftCustomer)
                        customersOfTourOfChosenCustomer.remove(customer)
                        customersOfTourOfChosenCustomer.remove(rightCustomer)
                    availableCustomersPerTour[tourIndex] = customersOfTourOfChosenCustomer
                    availableCustomers = [j for i in availableCustomersPerTour for j in i]
                    selectedCustomers[randomFacilityIndex].append(customer)
            if len(selectedCustomers[0])==3 and len(selectedCustomers[1])==3:
                newfacilitiesCustomers = deepcopy(facilitiesCustomers)
                [[newfacilitiesCustomers[fIndex].remove(c) for c in selectedCustomers[fIndex]] for fIndex in range(2)]
                [[newfacilitiesCustomers[fIndexOther].append(c) for c in selectedCustomers[fIndex] for fIndexOther in range(2) if fIndexOther != fIndex] for fIndex in range(2)]
                cI = self.cwsI
                simSol.tours: List[Tour] = list()
                simSol.routingCosts = list()
                for fIndex, facility in enumerate(random2Facilities):
                    facilityCustomers = newfacilitiesCustomers[fIndex]
                    cwsSol, cost, savingsList = cI.CWSforCustomerSet(simSol,facilityCustomers,facility)
                    for route in cwsSol:
                        _, routeVector = cI.__CWStoRoutingVector__([route])
                        newTour = Tour(routeVector,facility,inst)
                        newTour.updateRoutingCost()
                        newTour.refineStrategies()
                        simSol.tours.append(newTour)
                # update the simSol routing Costs and total Cost
                simSol.routingCosts = [t.routingCost for t in simSol.tours]
                simSol.simulatedRoutingCost = 0
                simSol.simulatedTotal = 0
                simSol.__getTotalCost__()
                simSol.updateAssignmentVectorByTours()
                
        return simSol