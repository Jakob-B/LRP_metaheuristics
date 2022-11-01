"""
Main function for executing the SimILS metaheuristic. 
"""
from typing import List
from math import floor
from copy import deepcopy
from datetime import datetime
import sys


import metaheuristik.instances as instances
import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.ClassLRPinstance
import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
import metaheuristik.quinteroaraujo.code.Stages as stage

try:
    import code.Stages as stage
except:
    print("Relative import does not work.")





SimILSSolution = SimObj.SimILSSolution
SimNetwork = SimObj.SimNetwork
MCSimulation = SimObj.MCSimulation

class SimILS():
    def __init__(self, instance: LRPinstance.LRPinstance):
        self.instance = instance
        self.stage1 = stage.Stage1(self.instance)
        self.stage2 = stage.Stage2(self.instance)
    def execute(self, maxSafetyStock:int=10, numFacilitySets:int = 1000, numFastSim:int=100, numLongSim:int=5000, maxIterStage2 = 100):
        instance = self.instance
        print(str(maxSafetyStock) + " " + str(numFacilitySets) + " " + str(numFastSim) + " " + str(numLongSim) + " " + str(maxIterStage2))
        startTime = datetime.now()
        iX = instance
        print(iX)
        iX.useYangRoutingCost = False # Yang ist viel zu teuer hier, nicht nutzen!


        """
        # First Step
        # Generation of Feasible Solutions
        """
        #s1 = stage.Stage1(iX)
        s1 = self.stage1

        sols: List[SimILSSolution] = s1.feasibleSolutionGenerator(numSim=numFastSim, numFacilitySets=numFacilitySets, maxSafetystock=maxSafetyStock)
        minCost = 1000000
        maxCost = 0
        bestSol = None
        worstSol = None
        for sol in sols:
            if minCost > sol.totalCost:
                minCost = sol.totalCost
                bestSol = sol
            if maxCost < sol.totalCost:
                maxCost = sol.totalCost
                worstSol = sol
        
        numBaseSols = max(2 + floor(len(iX.customers)/100),1)
        sortedSols = sorted(sols, key = lambda x: x.simulatedTotal)
        baseSols: List[SimILSSolution] = list()
        for i in range(min(numBaseSols,len(sortedSols))):
            baseSols.append(sortedSols[i])
            
        """
        # Second Step
        # Solution Improvement
        """
        #s2 = stage.Stage2(iX,baseSols)
        s2 = self.stage2
        promisingSols = s2.solutionImprovement(baseSols, maxIter=maxIterStage2)

        # Long Sim 
        for pSol in promisingSols:
            mcsim = MCSimulation(iX)
            simulatedRoutingCost, reliability = mcsim.doIteratedSimulation(pSol,numLongSim, True)
            print("SimRC: " + str(simulatedRoutingCost) + " @Reliability: " + str(reliability) +
            " and totalCost: " +str(pSol.totalCost) + "; number of Tours: " + str(len(pSol.tours)))
            pSol.simulatedRoutingCost = simulatedRoutingCost
            pSol.reliability = reliability
            pSol.simulatedTotal = pSol.simulatedRoutingCost + pSol.depotCost

        """
        # Final
        # Evaluation/Output
        """

        bestSol = promisingSols[0]
        for pSol in promisingSols:
            if pSol.simulatedTotal < bestSol.simulatedTotal:
                bestSol = deepcopy(pSol)
        
        bestSol.printSolution()
        print("\nTotal Cost: "+str(bestSol.totalCost))
        net = SimNetwork(bestSol)

        stopTime = datetime.now()
        elapsedTime = (stopTime-startTime).total_seconds()

        # ACHTUNG: Wenn simils.py nicht in Docker ausgeführt wird, sondern "per Hand", dann muss der erste / entfernt werden:
        # Pfad ist dann metaheuristik/figures/simils_...
        filename = str("/metaheuristik/figures/simils_"+iX.__str__()
            + "_TC-"+str(round(bestSol.totalCost,2))
            +"_RC-"+str(round(sum(bestSol.routingCosts),2))
            +"_SimTC-"+str(round(bestSol.simulatedTotal,2))
            +"_SimRC-"+str(round(bestSol.simulatedRoutingCost,2))
            +"_SimSS-"+str(bestSol.safetystock)
            +"_SimRe-"+str(round(bestSol.reliability,2))
            +"_TSec-"+str(round(elapsedTime,2))
            +".svg")
        # hier ebenso
        filenameStrategy = str("/metaheuristik/figures/simils_"+iX.__str__()
            + "_TC-"+str(round(bestSol.totalCost,2))
            +"_RC-"+str(round(sum(bestSol.routingCosts),2))
            +"_SimTC-"+str(round(bestSol.simulatedTotal,2))
            +"_SimRC-"+str(round(bestSol.simulatedRoutingCost,2))
            +"_SimSS-"+str(bestSol.safetystock)
            +"_SimRe-"+str(round(bestSol.reliability,2))
            +"_TSec-"+str(round(elapsedTime,2))
            +"_Strategy"
            +".svg")
        net.drawSolution(show=False, save=True,fileName=filename)
        net.drawBestStrategy(show=False, save=True, fileName=filenameStrategy)

if __name__ == '__main__':
    i1 = instances.Perl12x2Create()
    i2 = instances.Perl12x2sdCreate()
    i3 = instances.Christo50x5Create()
    i4 = instances.An32k5Create()
    i5 = instances.An32k1Create()
    i6 = instances.Gaskell21x5Create()
    i7 = instances.Gaskell21x5sdCreate()
    i8 = instances.Christo100x10Create()
    i9 = instances.Gaskell21x5sdPoissonCreate()
    i10 = instances.Gaskell32x5sd()
    iX = i10
    s = SimILS(iX)
    s.execute(maxSafetyStock=0, maxIterStage2=100)



