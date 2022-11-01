"""
Barreto Instance:
Author: Perl83
Customers: 55
Depots: 15
BKS: 1112,06

NOTE: This instance in the literature uses "variable costs" for depots. 
However, the metaheuristics are not made to deal with variable costs for depots.
Therefore, the above mentioned Best Known Solution (BKS) is higher than the solution generetated by SimILS.
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance

def createInstance():

    coord = [
        [0,0], # Placeholder
        [32,31], # Customers
        [29,32],
        [27,36],
        [29,29],
        [32,29],
        [26,25],
        [24,33],
        [30,35],
        [29,27],
        [29,21],
        [33,28],
        [17,53],
        [34,30],
        [25,60],
        [21,28],
        [30,51],
        [19,47],
        [17,33],
        [22,40],
        [25,14],
        [29,12],
        [24,48],
        [17,42],
        [6,26],
        [19,21],
        [10,32],
        [34,56],
        [12,47],
        [19,38],
        [27,41],
        [21,35],
        [32,45],
        [27,45],
        [32,38],
        [8,22],
        [15,25],
        [35,10],
        [36,47],
        [46,51],
        [50,40],
        [23,22],
        [27,30],
        [38,39],
        [36,32],
        [32,41],
        [42,36],
        [36,20],
        [15,19],
        [19,14],
        [45,19],
        [27,5],
        [52,24],
        [40,22],
        [40,52],
        [42,42], # Customers
        [30,61], # Facilities
        [22,54],
        [45,54],
        [39,47],
        [28,39],
        [36,36],
        [32,35],
        [33,32],
        [27,28],
        [32,28],
        [11,27],
        [18,25],
        [39,19],
        [15,12],
        [40,12]  # Facilities
        
    ]

    demandList = [
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1},
        {20:1}
    ]

    customers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55]
    totalVehicleCap = 120
    numParticles = 70
    facilities = [56,57,58,59,60,61,62,63,64,65,66,67,68,69,70]
    fOpeningCost = [240]*15
    fCapacity = [550]*15

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles)

    return instance