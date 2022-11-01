import numpy, math
import sys, os

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.LRPinstance
Tour = LRPObj.Tour

import metaheuristik.quinteroaraujo.code.SimILSObjects.ClassSimILSSolution as SimILSSolution

class MCSimulation:
    """
    Does the Monte Carlo Simulation for a SimILS Solution.
    """
    def __init__(self, instance: LRPinstance):#, sol: SimILSSolution):
        self.instance = instance
        #self.sol: SimILSSolution = sol
        self.rngen = numpy.random.default_rng()

    def doIteratedSimulation(self, sol: "SimILSSolution", numIterations: int, reliabilityAnalysis = False):
        """
        Does numIterations of simulation.
        
        If reliabilityAnalysis is True, also calculates the reliablility of a sol 
        by multiplying the reliability of all tours of a sol. The reliability of a tour is defined by 
        (1-numberOfRouteFailures/numIterations)

        :params numIterations: Number of Simulation Iterations
        :params reliabilityAnalysis: True/False, defining if reliability should be calculated and returned.

        ## Returns

        - average Simulated routing cost.
        - OR: if reliabilityAnalysis is True, returns a tuple of (averageSimulatedRoutingCost, SolReliability)

        """
        if numIterations == 0:
            raise ValueError("Iterations must be bigger than zero.")
        sumSimulatedRoutingCost = 0
        sumTourFailures = [0]*len(sol.tours)
        for _ in range(numIterations):
            simulatedRoutingCost, tourFailed = self.__doSimulation__(sol)
            sumSimulatedRoutingCost += simulatedRoutingCost
            avgSimRoutingCost: float = sumSimulatedRoutingCost/numIterations
            sumTourFailures = [tourFailed[i]+sumTourFailures[i] for i in range(len(sol.tours))]
        if reliabilityAnalysis:
            tourReliability = [1-sumTourFailures[i]/numIterations for i in range(len(sol.tours))]
            solReliability = numpy.prod(tourReliability)
            #print(solReliability)
            if solReliability == 1.0 and round(avgSimRoutingCost) != round(sol.totalCost-sol.depotCost):
                print("Here something wrong.")
            if solReliability < 0.1:
                print("Surprisingly low reliability. Check config.")
            return avgSimRoutingCost, solReliability
        return avgSimRoutingCost

    def __doSimulation__(self, sol: "SimILSSolution"):
        """
        Simulates for a given sol and included routes the demand of customers,
        and calculates the route cost using the strategies of each tour resulting from this demand.
       
        Also keeps track if a tour failes. A tour failes if at least once an unplanned trip back to the depot is required.

        ## Returns 
        - simulated routingCost (float).       
        - List indicating if corresponding tour failed, i.e. [0, 0, 1] if Tour 3 failed.
        
        NOTE: momentan verwende ich Tour.strategy statt Tour.compactStrategy. Das ist wahrscheinlich
        die bessere Variante, und vielleicht muss ich die erste elif gar nicht verwenden.
        """
        totalSimulatedRoutingCost = 0
        tourFailed = [0]*len(sol.tours)
        stochasticDemands = self.__simulatedLogNormalDemandList__(self.instance.variance)
        for t in sol.tours:
            expectedRemaingDemandsList = self.__expectedRemainingDemandTour__(t)
            remainingCap = self.instance.totalVehicleCap
            simulatedRoutingCost = self.instance.distanceMatrix[t.fullTrip[0]][t.fullTrip[1]]
            distanceMatrix = self.instance.distanceMatrix
            f = t.facility
            for cIndex,c in enumerate(t.routeVector):
                if cIndex == len(t.routeVector)-1:
                    c2 = f
                else:
                    c2 = t.routeVector[cIndex+1]
                stochasticDemand = stochasticDemands[self.instance.customers.index(c)]
                
                remainingCap -= stochasticDemand
                
                actionsOfCustomer = t.strategy[c]
                if remainingCap not in actionsOfCustomer.keys() and remainingCap<=0:
                    # reactive refilling:
                    # occuring demand higher than expected, vehicle cant serve demand fully, no strategy available, full refill and roundtrip
                    # this tour "failed"
                    tourFailed[sol.tours.index(t)] = 1
                    remainingCap = self.instance.totalVehicleCap - abs(remainingCap)
                    simulatedRoutingCost += distanceMatrix[c][f]+distanceMatrix[f][c]+distanceMatrix[c][c2]
                elif remainingCap not in actionsOfCustomer.keys():
                    expectedRemaindDemandAfterC = expectedRemaingDemandsList[cIndex]
                    if remainingCap >= expectedRemaindDemandAfterC:
                        # continue to next customer
                        simulatedRoutingCost += distanceMatrix[c][c2]
                    elif remainingCap < expectedRemaindDemandAfterC:
                        # preventive unscheduled refilling after customer and before continuing to next customer, therefore also route failure
                        simulatedRoutingCost += distanceMatrix[c][f]+distanceMatrix[f][c2]
                        tourFailed[sol.tours.index(t)] = 1
                        remainingCap = self.instance.totalVehicleCap
                elif remainingCap in actionsOfCustomer.keys():
                    action = actionsOfCustomer[remainingCap][0]
                    #print(action)
                    if action == "refill":
                        remainingCap = self.instance.totalVehicleCap
                        simulatedRoutingCost += distanceMatrix[c][f] + distanceMatrix[f][c2]
                        # Also scheduled Refill is a Tour Failure
                        tourFailed[sol.tours.index(t)] = 1
                    elif action == "proceed":
                        simulatedRoutingCost += distanceMatrix[c][c2]

                else:
                    raise Exception("Something wrong in Simulation of customer demands with remaining cap " + str(remainingCap))
            #print(simulatedRoutingCost)
            totalSimulatedRoutingCost += simulatedRoutingCost
        if 1 not in tourFailed and round(totalSimulatedRoutingCost+sol.depotCost)>round(sol.totalCost):
            print("Something strange with simulation: Even though simulated tour never 'failed', the simulated costs are higher than anticipated.")
        return totalSimulatedRoutingCost, tourFailed

    def __expectedRemainingDemand__(self, customer, t: Tour):
        """
        Calcualtes the expected remaining demand of a tour t after having visited customer.
        :param customer: customer that has been visited.
        :param t: Tour on which customer is.

        ## Returns:
        - expected remaining demand on tour after visiting customer
        """
        expRemDem = 0
        c1TourIndex = t.routeVector.index(customer)
        for c2TourIndex in range(c1TourIndex+1,len(t.routeVector)):
            c2 = t.routeVector[c2TourIndex]
            c2Index = self.instance.customers.index(c2)
            c2Demand = self.instance.expectedDemand[c2Index]
            expRemDem += c2Demand
        return expRemDem

    def __expectedRemainingDemandTour__(self, t: Tour):
        """
        Calculates the expected remaining demand of a tour t after having visited a customer, for each customer. 
        
        ## Returns: 
        Returns a list of remaining demand after each customer in tour t. 
        """
        
        customers = t.routeVector
        expRemDem = [0]*len(customers)
        for cTourIndex in range(len(customers)-1,0,-1):
            """
            Start loop at last customer, end loop at second customer.
            Write value of expRemDem at current position (~the remaining demand after havings served the current Customer) plus the demand of the current customer
            to the previoues customer (~customer that is visited before the current customer.)
            """
            cCurrent = customers[cTourIndex]
            cIndex = self.instance.customers.index(cCurrent)
            cDemand = self.instance.expectedDemand[cIndex]
            expRemDem[cTourIndex-1] = expRemDem[cTourIndex] + cDemand
        return expRemDem

    def __simulatedLogNormalDemand__(self,customer, varianceFactor: int = 0.1):
        """
        DEPRECATED
        """
        rng = self.rngen
        cIndex = self.instance.customers.index(customer)
        expectedDemand = self.instance.expectedDemand[cIndex]
        simulatedDemand = rng.normal(loc = expectedDemand, scale = varianceFactor*expectedDemand)
        simulatedDemand = max(round(simulatedDemand),0)
        #print(simulatedDemand)
        return simulatedDemand
    
    def __simulatedLogNormalDemandList__(self, varianceFactor: int = 0.1):
        """
        Uses a lognormal distribution to create the simulated demands of customers.

        Note, numpy.lognormal "uses the mean and standard deviation of the underlying normal distribution it is derived from".
        That's why some additional calculations are required here. 

        See numpy.random.Generator.lognormal documentation or this [Stackoverflow Comment](https://stackoverflow.com/a/51617073/19433391).
        """
        rng = self.rngen
        numCustomers = len(self.instance.customers)
        expectedDemands = [self.instance.expectedDemand[cIndex] for cIndex in range(numCustomers)]
        if varianceFactor == 0:
            return expectedDemands
        variances = [varianceFactor*expectedDemands[cIndex] for cIndex in range(numCustomers)]
        deviations = [math.sqrt(variance) for variance in variances]
        normal_standardDeviation = [numpy.sqrt(numpy.log(1+(deviations[cIndex]/expectedDemands[cIndex])**2)) for cIndex in range(numCustomers)]
        normal_mean = [numpy.log(expectedDemands[cIndex])-normal_standardDeviation[cIndex]**2 / 2 for cIndex in range(numCustomers)]
        #simulatedDemandsN = rng.normal(loc = expectedDemands,scale=variances,size=len(expectedDemands))
        simulatedDemandsL = rng.lognormal(mean = normal_mean,sigma=normal_standardDeviation, size = len(expectedDemands))
        simulatedDemands = simulatedDemandsL
        return list(simulatedDemands)



    def __simulatedDemand__(self, customer):
        """
        Considering the demand and probability matrix, returns a random demand for a given customer.

        NOTE: NOT IN USE
        """
        
        simulatedDemand = 0
        randVal = numpy.random.rand()
        demandProbVector = self.instance.demandProbMatrix[customer-1]
        discreteDemand = dict()
        pDistr = 0
        for dIndex, p in enumerate(demandProbVector):
            if p > 0:
                pDistr += p
                discreteDemand.update({pDistr:dIndex})
        for k,discreteDemand in discreteDemand.items():
            if k > randVal:
                simulatedDemand = discreteDemand
                break
        return simulatedDemand

