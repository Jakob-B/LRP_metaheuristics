from typing import List
from copy import deepcopy
import math
class LRPinstance:
    def __init__(self, coordinates: List[int], demand: List[dict] , customers: List[int], facilities: List[int], totalVehicleCap: int, openingCost: List[int], facCapacity: List[int], numParticles: int, variance: float = 0, customName = "", poisson = False):
        """
        Create a new Instance for a LRP.
        Contains all static informations/parameters for the LRP. \n
        Creates the demand Matrix and distance/cost Matrix based on demand-Dictionary and coordinates list.
        """
        self.customers = customers
        self.facilities = facilities
        self.facCapacity = facCapacity
        self.totalVehicleCap = totalVehicleCap
        self.coordinates = coordinates
        self.openingCost = openingCost
        self.demand = demand
        self.poisson = poisson
        self.expectedDemand = self.__expectedDemand__(demand)
        self.demandProbMatrix = self.__createDemandMatrix__(demand, poisson)
        self.distanceMatrix = self.__euclideanDistance__(coordinates)
        self.numParticles = numParticles
        
        self.highestDemand = self.__highestDemand__(demand)
        self.variance = variance
        self.useYangRoutingCost = False
        self.costDict = dict()
        self.cwsStreetDict = dict()
        self.__customName__ = customName
    def __repr__(self):
        pass
    def __str__(self):
        return f'{len(self.customers)}x{len(self.facilities)}_var{self.variance}_{self.__customName__}'

    def __highestDemand__(self,demand:List[dict]):
        highestDemands: List = list()
        for c in demand:
            highestDemandCustomer = 0
            for k,v in c.items():
                if k>highestDemandCustomer:
                    highestDemandCustomer = k
            highestDemands.append(highestDemandCustomer)
        #print(highestDemands)
        return highestDemands

    def __expectedDemand__(self,demand:List[dict]):
        expectedDemands: List = list()
        for c in demand:
            expectedDemandCustomer = 0
            for k,v  in c.items():
                expectedDemandCustomer += k*v
            expectedDemands.append(expectedDemandCustomer)
        #print(expectedDemands)
        return expectedDemands

    def __euclideanDistance__(self,coordinates:List[int]):
        """
        Given a list of coordinates, returns a matrix containing the distances between all nodes using the euclidean distance
        """
        from math import dist

        distanceMatrix = list()
        size = len(coordinates)
        for node in range(size):
            distance = list()
            for node2 in range(size):
                point1 = coordinates[node]
                point2 = coordinates[node2]
                onedist = round(dist(point1,point2) ,2)
                distance.append(onedist)
            distanceMatrix.append(distance)
        #print(distanceMatrix)
        return distanceMatrix
    
    def __createDemandMatrix__(self, demand:List[dict], poisson = False):
        """
        Input: Dictionary with demand:Probability (key:value) for each demand whose probability is not null
        Output: a demand matrix: from 0 to maxVehicleCap per Customer the associtated probability (including null probability)
        """
        totalVehicleCap = self.totalVehicleCap
        demandMatrix = list()
        discretedemandDictList = list()
        if not poisson:
            
            for c in demand: # iterate over customers
                customerDemand = [0]*(totalVehicleCap+1) # including 0
                for k in c:     # iterate over special demands of customer
                    a: int = c[k]
                    customerDemand[k] = a
                demandMatrix.append(customerDemand)
        else:
            for cIndex, c in enumerate(self.customers):
                expectedDemandC = self.expectedDemand[cIndex]
                customerDemand = [0]*(totalVehicleCap+1) # including 0
                for k in range(0,totalVehicleCap+1):
                    PxequalK = expectedDemandC**k/ math.factorial(k) * math.e**(-expectedDemandC)
                    if PxequalK >= 0.01:
                        customerDemand[k]= round(PxequalK,2)
                    else:
                        customerDemand[k]=0
                sumDemandProbs = sum(customerDemand)
                normedCustomerDemand = [round(p/sumDemandProbs,4) for p in customerDemand]        
                demandMatrix.append(normedCustomerDemand)
                discreteDemandDictC = dict([(demandK, probK) for demandK, probK in enumerate(normedCustomerDemand) if probK > 0])
                discretedemandDictList.append(discreteDemandDictC)
            self.demand = discretedemandDictList
        #print(demandMatrix)
        #textfile = open("metaheuristik/marinakis/figures/demandMatrix.txt", "w")
        #a = textfile.write(str(demandMatrix)+"\n")
        #textfile.close
        
        return demandMatrix

    def getMaxFacilityCapacity(self):
        return max(self.facCapacity)

    def __deepcopy__(self, memodict=...):
        newCoord = deepcopy(self.coordinates)
        newDemand: List[dict] = deepcopy(self.demand)
        newCustomers: List[int] = deepcopy(self.customers)
        newFacilities: List[int]= deepcopy(self.facilities)
        newTotalVehicleCap: int = self.totalVehicleCap
        newOpeningCost: List[int] = deepcopy(self.openingCost)
        newFacCapacity: List[int] = deepcopy(self.facCapacity)
        newNumParticles: int = self.numParticles
        newVariance: float = self.variance

        newI = LRPinstance(coordinates=newCoord, demand= newDemand, customers= newCustomers, facilities= newFacilities, totalVehicleCap= newTotalVehicleCap, openingCost=newOpeningCost,facCapacity=newFacCapacity,numParticles=newNumParticles,variance=newVariance)
        return newI

    