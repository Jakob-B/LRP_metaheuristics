"""
Barreto Instance:
Author: Christofides69
Customers: 50
Depots: 5
Solution LB: 549,4
Solution UB: 582,7
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance

def createInstance():

    coord = [
            [0,0], # Placeholder
            [37,52], # First Customer
            [49,49],
            [52,64],
            [20,26],
            [40,30],
            [21,47],
            [17,63],
            [31,62],
            [52,33],
            [51,21],
            [42,41],
            [31,32],
            [5,25],
            [12,42],
            [36,16],
            [52,41],
            [27,23],
            [17,33],
            [13,13],
            [57,58],
            [62,42],
            [42,57],
            [16,57],
            [8,52],
            [7,38],
            [27,68],
            [30,48],
            [43,67],
            [58,48],
            [58,27],
            [37,69],
            [38,46],
            [46,10],
            [61,33],
            [62,63],
            [63,69],
            [32,22],
            [45,35],
            [59,15],
            [5,6],
            [10,17],
            [21,10],
            [5,64],
            [30,15],
            [39,10],
            [32,39],
            [25,32],
            [25,55],
            [48,28],
            [56,37], # Last Customer
            [10,49], # First Depot
            [20,30],
            [5,25],
            [54,17],
            [43,53] # Last Depot
    ]

    demandList = [
        {7:1},
        {30:1},
        {16:1},
        {9:1},
        {21:1},
        {15:1},
        {19:1},
        {23:1},
        {11:1},
        {5:1},
        {19:1},
        {29:1},
        {23:1},
        {21:1},
        {10:1},
        {15:1},
        {3:1},
        {41:1},
        {9:1},
        {28:1},
        {8:1},
        {8:1},
        {16:1},
        {10:1},
        {28:1},
        {7:1},
        {15:1},
        {14:1},
        {6:1},
        {19:1},
        {11:1},
        {12:1},
        {23:1},
        {26:1},
        {17:1},
        {6:1},
        {9:1},
        {15:1},
        {14:1},
        {7:1},
        {27:1},
        {13:1},
        {11:1},
        {16:1},
        {10:1},
        {5:1},
        {25:1},
        {17:1},
        {18:1},
        {10:1}
    ]



    customers=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50] 
    totalVehicleCap=160
    numParticles=70 
    facilities=[51,52,53,54,55]
    fOpeningCost=[40,40,40,40,40]
    fCapacity=[1000,1000,1000,1000,1000]
    variance = 0.1

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles, variance)

    return instance