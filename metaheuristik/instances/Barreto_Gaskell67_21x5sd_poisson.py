"""
Barreto Instance:
Author: Perl183
Customers: 12
Depots: 2
BKS: 424,9
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance

def createInstance():

    coord = [
            [0,0], # Placeholder
            [151,264], # First Customer
            [159,261],
            [130,254],
            [128,252],
            [163,247],
            [146,246],
            [161,242],
            [142,239],
            [163,236],
            [148,232],
            [128,231],
            [156,217],
            [129,214],
            [146,208],
            [164,208],
            [141,206],
            [147,193],
            [164,193],
            [129,189],
            [155,185],
            [139,182], # Last Customer
            [136,194], # First Depot
            [143,237],
            [136,216],
            [137,204],
            [128,197] # Last Depot
    ]

    demandList = [
        {11:1},
        {7:1},
        {8:1},
        {14:1},
        {21:1},
        {4:1},
        {8:1},
        {1:1},
        {5:1},
        {6:1}, #10
        {12:1},
        {13:1},
        {13:1},
        {3:1},
        {9:1}, #15
        {21:1},
        {10:1},
        {9:1},
        {25:1},
        {18:1},
        {7:1}
    ]



    customers=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21] 
    totalVehicleCap=60
    numParticles=70 
    facilities=[22,23,24,25,26]
    fOpeningCost=[50,50,50,50,50]
    fCapacity=[150,150,150,150,150]
    variance = 0.1

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles, variance, customName="poisson",poisson=True)

    return instance