"""
NAME : A-n32-k5
COMMENT : (Augerat et al, Min no of trucks: 5, Optimal value: 784)
TYPE : CVRP
DIMENSION : 32
EDGE_WEIGHT_TYPE : EUC_2D 
CAPACITY : 100

Depots: 5 identical depots (1-5)
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance


def createInstance():

    coord = [[99,99], # Placeholder so Matrix starts with 1 (so that node 1 is in line 1 of matrix)
            [96,44],
            [50,5],
            [49,8],
            [13,7],
            [29,89],
            [58,30],
            [84,39],
            [14,24],
            [2,39],
            [3,82],
            [5,10],
            [98,52],
            [84,25],
            [61,59],
            [1,65],
            [88,51],
            [91,2],
            [19,32],
            [93,3],
            [50,93],
            [98,14],
            [5,42],
            [42,9],
            [61,62],
            [9,97],
            [80,55],
            [57,69],
            [23,15],
            [20,70],
            [85,60],
            [98,5],
            [82,76], # Depot 1: 32
            [82,76], # Depot 2: 33
            [82,76], # Depot 3: 34
            [82,76], # Depot 4: 35
            [82,76]] # Depot 5: 36

    demandList_An32k5 = [
            {19:1},
            {21:1},
            {6:1},
            {19:1},
            {7:1},
            {12:1},
            {16:1},
            {6:1},
            {16:1},
            {8:1},
            {14:1},
            {21:1},
            {16:1},
            {3:1},
            {22:1},
            {18:1},
            {19:1},
            {1:1},
            {24:1},
            {8:1},
            {12:1},
            {4:1},
            {8:1},
            {24:1},
            {24:1},
            {2:1},
            {20:1},
            {15:1},
            {2:1},
            {14:1},
            {9:1}
    ]

    customers=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
    totalVehicleCap=100
    numParticles=70 
    facilities=[32,33,34,35,36]
    fOpeningCost=[10,10,10,10,10]
    fCapacity=[100,100,100,100,100]

    instance = LRPinstance(coord,demandList_An32k5,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles)


    return instance
