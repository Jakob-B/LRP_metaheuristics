
from random import random
from typing import List
from copy import deepcopy
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution import Solution
import metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution as ObjSolution
Solution = ObjSolution.Solution
class Particle:
    def __init__(self, curSol: Solution, pBestSol: Solution, lBestSol: Solution ):
        self.curSol = curSol
        self.pBestSol = pBestSol
        self.lBestSol = lBestSol
        self.velocity: List[float] = self.__randomVelocity__()
        self.neighborhoodWidth = 1 # maximal 34/35?
        self.iterSinceImprov = 0


    def show(self):
        # print Particle
        print("Current Solution:\n" + "Route Vector: " +  str(self.curSol.routes) + "\n" + "Routing Cost: " + str(self.curSol.routingCosts))
        print("Personal Best Solution:\n" + "Route Vector: " +  str(self.pBestSol.routes) + "\n" + "Routing Cost: " + str(self.pBestSol.routingCosts))
        print("Local Best Solution:\n" + "Route Vector: " +  str(self.lBestSol.routes) + "\n" + "Routing Cost: " + str(self.lBestSol.routingCosts))
        print("Velocity:\n"+ str(self.velocity))
        print("Neighborhood Width:\n"+str(self.neighborhoodWidth))
    
    def newBestFound(self):
        self.iterSinceImprov = 0
    def noNewBestFound(self):
        self.iterSinceImprov += 1
        if self.iterSinceImprov > 10:
            if self.neighborhoodWidth < 34:
                self.iterSinceImprov = 0
                self.neighborhoodWidth+=1
                #print("Neighborhood increased.")
            if self.neighborhoodWidth >= 34:
                self.iterSinceImprov = 0
                self.neighborhoodWidth = 1

    def __randomVelocity__(self):
        velocity = list()
        veloD = [random()*8-4 for i in self.curSol.depotVector]
        veloR = [random()*8-4 for i in self.curSol.routingVector]
        veloP = [random()*8-4 for i in self.curSol.pointerVector]
        velocity = [veloR, veloP, veloD]
        return velocity

    def __deepcopy__(self,memodict={}):
        newP = Particle(deepcopy(self.curSol),deepcopy(self.pBestSol),deepcopy(self.lBestSol))
        newP.velocity = self.velocity[:]
        newP.neighborhoodWidth = self.neighborhoodWidth
        newP.iterSinceImprov = self.iterSinceImprov
        #print("copied a Particle")
        return newP

    def __getAverageVelocity__(self):
        """
        For Debugging Purposes.
        Calculate the average velocity of routingVector
        """
        veloPlus = 0
        veloNeg = 0
        countPlus = 0
        countNeg = 0
        #for i in self.velocity:
        for j in self.velocity[0]:
            if j > 0:
                veloPlus += j
                countPlus +=1
            else:
                veloNeg += j
                countNeg +=1
        if countPlus == 0:
            r1 = "None"
        else: 
            r1 = veloPlus/countPlus
        if countNeg == 0:
            r2 = "None"
        else:
            r2 = veloNeg/countNeg
        return [r1,r2]
            