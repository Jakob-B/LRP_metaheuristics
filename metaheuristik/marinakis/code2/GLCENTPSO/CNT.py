
from cmath import sqrt
from copy import copy, deepcopy
from datetime import date, datetime
from random import random
from numpy import random as rr    
#from LRPClassObjects.ClassTour import Tour
#from LRPClassObjects.ClassParticle import Particle
#from LRPClassObjects.ClassSwarm import Swarm
#from LRPClassObjects.ClassSolution import Solution
import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Tour = LRPObj.Tour
Particle = LRPObj.Particle
Swarm = LRPObj.Swarm
Solution = LRPObj.Solution
Instance = LRPObj.LRPinstance

class CNTClass:
    def __init__(self, swarm: Swarm):
        self.swarm = swarm

    def doCNT(self,average = False, p: Particle = None, iteration: int = 1, maxIteration: int = 1000):
        """
        Calculate velocity, determine Path Relinking version and do Path Relinking for a singel Particle. \n
        If a feasible Solution has been created by PR, return the Particle with curSol = new Sol,
        otherwise returned Particle is the same as the Input Particle.
        """
        swarm = self.swarm
        startCNT = datetime.now()
        if p == None or swarm == None:
            raise ValueError("None-Objects in CNT. Check if particle and swarm are not None.")
        else:
            #print("CNT start with Particle Route Vector:")
            
            
            numElements = [len(p.curSol.routingVector), len(p.curSol.pointerVector), len(p.curSol.depotVector)]
            newVelocity = velocityEquation(swarm,p) # nested List: routing, pointer, depot
            #print(newVelocity)
            version = ["","","",]
            for i in range(2):
                version[i] = [""]*numElements[i]
                if not average:
                    #for each element
                    for e in range(numElements[i]):
                        version[i][e] = prVersion(newVelocity[i][e], iteration, swarm, maxIteration)
                else:
                    #average velocities
                    averageV = sum(newVelocity[i])/numElements[i]
                    version[i] = [prVersion(averageV, iteration, swarm, maxIteration)]*numElements[i]
            #Test
            #version = ["NOPR","NOPR","PRGB","PRGB","PRGB","PRPB","PRPB","PRGB","PRGB","PRGB"]
            if average and version[0][0] == "NOPR":
                # skip Path Relinking
                pNew = deepcopy(p)
            else:
                startPR = datetime.now()
                #pNew = deepcopy(pathRelinkingShort(version,p,swarm))
                pNew = pathRelinkingShort(version,p,swarm)
                stopPR = datetime.now()
                elapsedPR = (stopPR-startPR).total_seconds()
            pNew.velocity = list(newVelocity)
            #if pNew.curSol.totalCost < swarm.gBestSol.totalCost:
            #    print(" ####################################\n " +str(pNew.curSol.totalCost) + " ####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n")
            #if tempT != p.curSol.routeVector:
            #    print("######################################")
        stopCNT = datetime.now()
        elapsedCNT = (stopCNT-startCNT).total_seconds()
        return pNew



def pathRelinkingShort(version: list, p: Particle, swarm: Swarm):
    """
    Path Relinking
    :param version: Nested List containing Path Relinking Version (PRGB, PRPB, NOPR). List is [[routingVector],[pointerVector],[depotVector]]
    """
    count = 0
    # 1) doPR for RoutingVecotr
    tabuR = list()
    bestPRSol: Solution = None
    newfeasibleSolutions = 0
    newS: Solution = deepcopy(p.curSol)
    for eR in range(len(p.curSol.routingVector)):
        
        #newP = deepcopy(p)
        #newS: Solution = deepcopy(p.curSol)
        #do path relinking with version
        if version[0][eR]=="NOPR":
            p = localSearch(p,eR,tabuR)
            #print()
            newRVector = deepcopy(newS.routingVector)
            
        elif version[0][eR]=="PRPB":
            newRVector = deepcopy(doPR(newS.routingVector,p.pBestSol.routingVector,eR,tabuR))
        elif version[0][eR]=="PRGB":
            newRVector = deepcopy(doPR(newS.routingVector,swarm.gBestSol.routingVector,eR,tabuR))

        newS.routingVector = newRVector
        #if not swarm.getSolution(newS):
        if swarm.isNewSolution(newS):
            if newS.updateSolution(swarm.tours):
                swarm.storeSolution(newS)
                # check if good Solution? Store best solution created by Path Relinking
                #print("PR created feasible solution.")
                if bestPRSol != None:
                    if bestPRSol.totalCost > newS.totalCost:
                        bestPRSol = deepcopy(newS)
                else:
                    bestPRSol = deepcopy(newS)
            else:
                #print("PR created unfeasible solution.")
                a = 1
        else:
            newS = deepcopy(swarm.getSolutionByVectorsOfSolution(newS))
    # make sure that newS is the best Solution created in "PR for RoutingVector"
    if bestPRSol != None:
        newS = deepcopy(bestPRSol)
          
    # 2) doPR for PointingVector
    tabuP = list()
    bestPRSol2: Solution = None  
    for eP in range(len(p.curSol.pointerVector)):
        if version[1][eP]=="NOPR":
            #p = localSearch(p,e,tabu)
            #print()
            newPVector = deepcopy(newS.pointerVector)
        elif version[1][eP]=="PRPB":
            newPVector = deepcopy(doPRforPointingVector(newS.pointerVector, p.pBestSol.pointerVector, p.curSol.depotVector,eP,tabuP)    )
            
        elif version[1][eP]=="PRGB":
            newPVector = deepcopy(doPRforPointingVector(newS.pointerVector, swarm.gBestSol.pointerVector, p.curSol.depotVector,eP,tabuP))
            
        if newS.pointerVector != newPVector:
            prPointingVectorUsed()
        newDVector = deepcopy(updateDepotVectorWithPointingVector(newPVector))
        
        newS.depotVector = newDVector
        newS.pointerVector = newPVector
        #print(count)
        count += 1
        #if not swarm.getSolution(newS):
        if swarm.isNewSolution(newS):
            if newS.updateSolution(swarm.tours):
                swarm.storeSolution(newS)
                # check if good Solution? Store best solution created by Path Relinking
                #print("PR created feasible solution.")
                if bestPRSol2 != None:
                    if bestPRSol2.totalCost > newS.totalCost:
                        bestPRSol2 = deepcopy(newS)
                        bestPRSol = deepcopy(newS)
                else:
                    bestPRSol2 = deepcopy(newS)
                if p.curSol.routingVector != newS.routingVector or p.curSol.pointerVector != newS.pointerVector:
                    newfeasibleSolutions +=1
                if p.curSol.pointerVector != newS.pointerVector:
                    a = 1
            else:
                #print("PR created unfeasible solution.")
                unfeasibleSolCreated()
        else:
            newS = deepcopy(swarm.getSolutionByVectorsOfSolution(newS))
    pNew = deepcopy(p)
    if bestPRSol != None:
        bestPRSol.updateSolution() # just for good measure, to be sure that it is not a "Ghost solution"
        pNew.curSol = deepcopy(bestPRSol)
        #if bestPRSol.totalCost < swarm.gBestSol.totalCost:
        #    print(" ####################################\n " +str(bestPRSol.totalCost) + " ####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n")
        #print("New Solution found in PR.")
    #if newfeasibleSolutions > 0:
    #    print(str(newfeasibleSolutions) + " new feasible Solutions for Particle in PR created." + " Best Value: " + str(bestPRSol.totalCost) + " with RoutingV " + str(bestPRSol.routingVector) + " and PointerV " + str(bestPRSol.pointerVector))
    if pNew.curSol.totalCost < p.curSol.totalCost:
        #print("CNT does work.")
        0
    elif pNew.curSol.totalCost > p.curSol.totalCost:
        #print("CNT does not work.")
        0
    return pNew

def unfeasibleSolCreated():
    return 0

def prPointingVectorUsed():
    return 0

def doPRforPointingVector(vector1: list, vector2: list, depotVector: list, e: int, tabu: list):
    """
    update Value of pointingVector with Value of vector2 at position e if not in tabu.
    Add value of vector2 to tabu list, if value is not 0.
    Return new pointingVector.
    TODO: DepotVector Parameter könnte unnötig sein, da nicht mehr verwendet wird nach Aufruf?
    """
    #return doPRforPointerVector2(vector1, vector2,e,tabu)
    if vector1 != vector2:
        newVector = deepcopy(vector1)
        valueV1 = vector1[e]
        valueV2 = vector2[e]
        if valueV2 not in tabu:
            newVector[e] = valueV2
            if valueV2 != 0:
                depotVector[e] = 1
                tabu.append(valueV2)
            else:
                depotVector[e] = 0
        return newVector
    else:
        return vector1

def doPRforPointerVector2(currentVector: list, targetVector: list,e: int, tabu: list):
    return currentVector
    # TODO: check if this is working correct!
    # # 1) check if there is a difference in opened depots
    if currentVector == targetVector:
        return currentVector
    else:
        # check if value of current is 0
        pointerValueTarget = targetVector[e]
        pointerValueCurrent = currentVector[e]
        if pointerValueCurrent != pointerValueTarget:
            if pointerValueCurrent == 0:
                print()
        newVector = list(currentVector)
        newVector[e] = pointerValueTarget
        return newVector
    # 2) open and close each one depot as in target vector
    # 3) give pointervector value of closed depot to opened depot
    """
        depotStatusTarget = targetVector[e]
        depotStatusCurrent = currentVector[e]
        newVector = list(currentVector)
        if depotStatusCurrent != depotStatusTarget:
            newVector[e]=depotStatusTarget
            if e!=len(newVector)-1:
                newVector[e+1]=depotStatusCurrent
            return newVector
        else:
            return newVector
    """

def updateDepotVectorWithPointingVector(pointerVector: list):
    """
    Update the depot Vector so that it is equal to the pointing Vector
    returns a vector
    """
    depotVector = list()
    for f in pointerVector:
        if f > 0:
            depotVector.append(1)
        else:
            depotVector.append(0)
    return depotVector

def doPR(vector1: list, vector2, e: int, tabu: list):
    newVector = deepcopy(vector1)
    valueV1 = vector1[e]
    valueV2 = vector2[e]
    if valueV1 != valueV2 and valueV2 not in tabu:
        a = vector1.index(valueV2)
        newVector[e] = valueV2
        newVector[a] = valueV1
        tabu.append(valueV2)
    return newVector


def localSearch(p: Particle, e: int, tabu: list):
    # noch unklar was genau hier gemacht wird
    # TODO: Lokal Search implementieren. Fügt derzeit nur den Wert an der Stelle e als Tabu hinzu.
    # TODO: Derzeit zufälliger Tausch mit einem anderen Element
    #a = rr.randint(1,len(p.curSol.routeVector))
    #valueInRandom = p.curSol.routeVector[a]
    valueInCS = p.curSol.routingVector[e]
    #if valueInRandom not in tabu:
    #    p.curSol.routeVector[e] = valueInRandom
    #    p.curSol.routeVector[a] = valueInCS
    tabu.append(valueInCS)
    return p


def velocityEquation(s: Swarm, p: Particle):
    """
    Calculates the Velocity of a Particle, returns a nested List. \n
    Velocity is a nested List: 
    - List of Velocity for routingVector
    - List of Velocity for pointerVector
    - List of Velocity for depotVector
    """
    # Parameters
    c1 = 1.35
    c2 = 1.35
    c3 = 1.40
    c = c1 + c2 + c3
    constrictionFactor = (2)/(abs(2-c-sqrt(c**2-4*c))) # ~ 0,73
    
    rand1 = random()
    rand2 = random()
    rand3 = random()
    ubound = 4
    lbound = -4
    #######
    veloR = list()
    veloP = list()
    veloD = list()
    #textfile = open("metaheuristik/marinakis/figures/velocities.txt", "a")
    # routing Vector
    numElements = len(p.curSol.routingVector)
    newVelocity = [0]*numElements
    for e in range(numElements):
        newVelocity[e] += p.velocity[0][e]
        newVelocity[e] += c1*rand1*distance(p.pBestSol.routingVector,p.curSol.routingVector,e, True)
        newVelocity[e] += c2*rand2*distance(s.gBestSol.routingVector,p.curSol.routingVector,e, True)
        newVelocity[e] += c3*rand3*distance(p.lBestSol.routingVector,p.curSol.routingVector,e, True)
        newVelocity[e] *= constrictionFactor
        #if newVelocity[e]<0 and p.velocity[0][e]>0:
        #print(newVelocity[e])
        
        # Check if Velocity is out of bounds
        if newVelocity[e] > ubound or newVelocity[e] < lbound:
            newVelocity[e] = random()*8-4
        #a = textfile.write(str(newVelocity[e])+"\n")
    veloR = newVelocity
    #textfile.close
    # pointerVector
    numElements = len(p.curSol.pointerVector)
    newVelocity = [0]*numElements
    for e in range(numElements):
        newVelocity[e] += p.velocity[1][e]
        newVelocity[e] += c1*rand1*distance(p.pBestSol.pointerVector,p.curSol.pointerVector,e, True)
        newVelocity[e] += c2*rand2*distance(s.gBestSol.pointerVector,p.curSol.pointerVector,e, True)
        newVelocity[e] += c3*rand3*distance(p.lBestSol.pointerVector,p.curSol.pointerVector,e, True)
        newVelocity[e] *= constrictionFactor
        # Check if Velocity is out of bounds
        if newVelocity[e] > ubound or newVelocity[e] < lbound:
            newVelocity[e] = random()*8-4
    veloP = newVelocity

    # depot Vector
    numElements = len(p.curSol.depotVector)
    newVelocity = [0]*numElements
    for e in range(numElements):
        newVelocity[e] += p.velocity[2][e]
        newVelocity[e] += c1*rand1*distance(p.pBestSol.depotVector,p.curSol.depotVector,e)
        newVelocity[e] += c2*rand2*distance(s.gBestSol.depotVector,p.curSol.depotVector,e)
        newVelocity[e] += c3*rand3*distance(p.lBestSol.depotVector,p.curSol.depotVector,e)
        newVelocity[e] *= constrictionFactor
        # Check if Velocity is out of bounds
        if newVelocity[e] > ubound or newVelocity[e] < lbound:
            newVelocity[e] = random()*8-4
    veloD = newVelocity

    return [veloR, veloP, veloD]

def prVersion(velocity: float, iteration: int = 1000, swarm: Swarm = None, itermax: int = 1000):
    """
    Calculates L1 and L2 values
    """
    #return "PRGB" # DEBUG
    ubound = 4
    lbound = -4
    w1 = 0.8#0.8
    w2 = 0.9#0.9
    
    version = ""

    #textfile = open("metaheuristik/marinakis/figures/prVersion.txt", "a")

    L1 = (ubound - lbound) * (w1 - (w1/itermax)*iteration)+lbound
    L2 = (ubound - lbound) * (w2 - (w2/(2*itermax))*iteration)+lbound
    if velocity < L1:
        swarm.prVersion["NOPR"]+=1
        version = "NOPR"
    elif velocity >= L1 and velocity < L2:
        swarm.prVersion["PRPB"]+=1
        version =  "PRPB"
    else:
        #velocity > L2:
        swarm.prVersion["PRGB"]+=1
        version = "PRGB" 

    #a = textfile.write(str(prVersion)+"\n")
    #textfile.close
    return version

def distance(v1: list(), v2: list(), e: int, exactMatch = True):
    """
    Calculates the exact match distance of two vectors if True.
    Else calculates "actual distance"
    """
    exactMatch = True
    e1 = v1[e]
    e2 = v2[e]
    distance = 0
    if exactMatch:
        if e1 == e2:
            distance = 0
        elif e1 < e2:
            distance = 1
        elif e1 > e2:
            distance = -1
        else:
            distance = 1
        return distance
    else:
        return e1-e2