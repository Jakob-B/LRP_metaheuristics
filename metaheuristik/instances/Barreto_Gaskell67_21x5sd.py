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
        {11:0.5, 10:0.25,12:0.25},
        {7:0.5, 8:0.25,6:0.25},
        {8:0.5, 9:0.25,7:0.25},
        {14:0.5, 13:0.25,12:0.25},
        {21:0.5, 20:0.25,22:0.25},
        {4:0.5, 5:0.25,3:0.25},
        {8:0.5, 9:0.25,7:0.25},
        {1:0.5, 0:0.25,2:0.25},
        {5:0.5, 6:0.25,4:0.25},
        {6:0.5, 7:0.25,5:0.25},#10
        {12:0.5, 11:0.25,13:0.25},
        {13:0.5, 12:0.25,14:0.25},
        {13:0.5, 12:0.25,14:0.25},
        {3:0.5, 4:0.25,2:0.25},
        {9:0.5, 10:0.25,8:0.25},#15
        {21:0.5, 20:0.25,22:0.25},
        {10:0.5, 11:0.25,9:0.25},
        {9:0.5, 10:0.25,8:0.25},
        {25:0.5, 26:0.25,24:0.25},
        {18:0.5, 19:0.25,17:0.25},
        {7:0.5, 8:0.25,6:0.25}
    ]



    customers=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21] 
    totalVehicleCap=60
    numParticles=70 
    facilities=[22,23,24,25,26]
    fOpeningCost=[50,50,50,50,50]
    fCapacity=[150,150,150,150,150]
    variance = 0.1

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles, variance)

    return instance