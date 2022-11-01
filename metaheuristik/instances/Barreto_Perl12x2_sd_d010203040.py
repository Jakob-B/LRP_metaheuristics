"""
Barreto Instance:
Author: Perl183
Customers: 12
Depots: 2
LB: 203,98
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance

def createInstance():

    coord = [
            [0,0], # Placeholder
            [34,31], #Customers
            [29,32],
            [24,33],
            [17,29],
            [8,28],
            [33,27],
            [24,25],
            [31,23],
            [30,17],
            [16,16],
            [10,14],
            [15,9],
            [25,19], # Depot 1
            [14,24] # Depot 2
    ]
    
    demandList = [
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        {20:0.4, 10:0.2,30:0.2, 0: 0.1, 40: 0.1},
        
    ]
    
    
    customers=[1,2,3,4,5,6,7,8,9,10,11,12] 
    totalVehicleCap=140
    numParticles=70 
    facilities=[13,14]
    fOpeningCost=[100,100]
    fCapacity=[280,280]
    variance = 0.1

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles, variance, customName="d010203040")

    return instance