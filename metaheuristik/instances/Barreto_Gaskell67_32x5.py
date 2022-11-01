"""
Barreto Instance:
Author: Gaskelll67
Customers: 32
Depots: 5
BKS: 562,22
"""

from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance

def createInstance():

    coord = [
            [0,0], # Placeholder
            [298,427], # First Customer
            [309,445],
            [307,464],
            [336,475],
            [320,439],
            [321,437],
            [322,437],
            [323,433],
            [324,433],
            [323,429],
            [314,435],
            [311,442],
            [304,427],
            [293,421],
            [296,418],
            [261,384],
            [297,410],
            [315,407],
            [314,406],
            [321,391],
            [321,398],
            [314,394],
            [313,378],
            [304,382],
            [295,402],
            [283,406],
            [279,399],
            [271,401],
            [264,414],
            [277,439],
            [290,434],
            [319,433], # Last Customer
            [364,435], # First Depot
            [323,413],
            [285,427],
            [278,424],
            [266,422] # Last Depot
    ]

    demandList = [
        {700:1},
        {400:1},
        {400:1},
        {1200:1},
        {40:1},
        {80:1},
        {2000:1},
        {900:1},
        {600:1},
        {750:1},
        {1500:1},
        {150:1},
        {250:1},
        {1600:1},
        {450:1},
        {700:1},
        {550:1},
        {650:1},
        {200:1},
        {400:1},
        {300:1},
        {1300:1},
        {700:1},
        {750:1},
        {1400:1},
        {4000:1},
        {600:1},
        {1000:1},
        {500:1},
        {2500:1},
        {1700:1},
        {1100:1}
    ]



    customers=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32] 
    totalVehicleCap=8000
    numParticles=70 
    facilities=[33,34,35,36,37]
    fOpeningCost=[50,50,50,50,50]
    fCapacity=[35000,35000,35000,35000,35000]
    variance = 0.0

    instance = LRPinstance(coord,demandList,customers,facilities, totalVehicleCap, fOpeningCost, fCapacity, numParticles, variance)

    return instance