from typing import List
class SimILSInstance:
    def __init__(self, coordinates: List[int], demand: List[dict] , customers: List[int], facilities: List[int], totalVehicleCap: int, openingCost: List[int], facCapacity: List[int]):
        self.customers = customers
        self.facilities = facilities
        self.facCapacity = facCapacity
        self.totalVehicleCap = totalVehicleCap
        self.coordinates = coordinates
        self.openingCost = openingCost
        self.demandProbMatrix = self.__createDemandMatrix__(demand)
        self.distanceMatrix = self.__euclideanDistance__(coordinates)
        self.expectedDemand = self.__expectedDemand__(demand)
    
    def __expectedDemand__(self,demand:List[dict]):
        expectedDemands: List = list()
        for c in demand:
            expectedDemandCustomer = 0
            for k,v  in c.items():
                expectedDemandCustomer += k*v
            expectedDemands.append(expectedDemandCustomer)
        print(expectedDemands)
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
        return distanceMatrix
    
    def __createDemandMatrix__(self, demand:List[dict]):
        """
        Input: Dictionary with demand:Probability (key:value) for each demand whose probability is not null
        Output: a demand matrix: from 0 to maxVehicleCap per Customer the associtated probability (including null probability)
        """
        totalVehicleCap = self.totalVehicleCap
        demandMatrix = list()
        for c in demand: # iterate over customers
            customerDemand = [0]*(totalVehicleCap+1) # including 0
            for k in c:     # iterate over special demands of customer
                a: int = c[k]
                customerDemand[k] = a
            demandMatrix.append(customerDemand)
        return demandMatrix


    def getMaxFacilityCapacity(self):
        return max(self.facCapacity)