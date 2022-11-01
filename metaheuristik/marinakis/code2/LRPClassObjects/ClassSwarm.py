import copy
from datetime import datetime
from typing import Dict, List

#from metaheuristik.marinakis.code2.LRPClassObjects.ClassParticle import Particle
import metaheuristik.marinakis.code2.LRPClassObjects.ClassParticle as ObjParticle
Particle = ObjParticle.Particle
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassTour import Tour
import metaheuristik.marinakis.code2.LRPClassObjects.ClassTour as ObjTour
Tour = ObjTour.Tour
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution import Solution
import metaheuristik.marinakis.code2.LRPClassObjects.ClassSolution as ObjSolution
Solution = ObjSolution.Solution
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance
import metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance as ObjInstance
LRPinstance = ObjInstance.LRPinstance

class Swarm:
    """
    Holds a list of all particles and a dictionary of already calculated routes.
    :param particles: Particle List of all particles in this swarm
    :param routes: Dictioray with key=routeVector of type list and value=Tour of type Tour
    """
    def __init__(self, instance: LRPinstance):
        self.instance = instance
        self.particles: List[Particle] = list()
        #self.solutions: List[Solution] = list()
        self.solutions: Dict = {}
        self.gBestSol: Solution = None 
        self.tours: Dict = {}
        self.prVersion = {"NOPR":0,"PRPB":0,"PRGB":0}
        self.iterSinceImprov = 0
        self.solroutecreationtime = 0
        self.solfindingtime = 0

    
            
#########################################

    def getSolutionByVectorsOfSolution(self, s: Solution):
        """
        Checks if solution is already known; ID for sol is routingVector+depotVector+pointerVector.
        Returns solution if known,
        otherwise returns False.

        Attention: Returned solution only contains vectors and totalCost, every other parameter (tours, etc.) is empty!
        I will call those half-empty solutions "Ghost Solution". They can be filled by calling solution.updateSolution().
        """
        if not self.isNewSolution(s):
            key = str(s.routingVector) + "" + str(s.depotVector) + "" + str(s.pointerVector)
            storableSolution: Dict = copy.deepcopy(self.solutions[key])
            s = Solution(self.instance)
            s.assignmentVector = storableSolution["aV"]
            s.depotVector = storableSolution["dV"]
            s.routingVector = storableSolution["rV"]
            s.pointerVector = storableSolution["pV"]
            s.totalCost = storableSolution["tCost"]
            return s
        else:
            return False
            
    def isNewSolution(self, s: Solution):
        """
        Checks if solution is a new Solution and not already known; ID for sol is routingVector+depotVector+pointerVector.
        Returns True if solution is new,
        otherwise returns False.
        """
        isNew = True
        startTimeFindSol = datetime.now()
        key = str(s.routingVector) + "" + str(s.depotVector) + "" + str(s.pointerVector)
        if key in self.solutions:
            #print("Found solution.")
            
            isNew = False
        else:
            #print("New Solution")
            isNew = True
        stopTimeFindSol = datetime.now()
        elapsedTime = (stopTimeFindSol-startTimeFindSol).total_seconds()
        self.solfindingtime += elapsedTime
        return isNew

        
    def storeSolution(self, s: Solution):
        key = str(s.routingVector) + "" + str(s.depotVector) + "" + str(s.pointerVector)
        storableSolution = dict()
        storableSolution = {"rV": s.routingVector, "dV":s.depotVector, "pV":s.pointerVector, "aV":s.assignmentVector,"tCost":s.totalCost}
        self.solutions.update({key:storableSolution})
        self.solroutecreationtime += s.tourcreationtime



##########################################

    def __storeTour__(self, t: Tour):
        key = str(t.fullTrip)
        #self.tours.update({key:t})
        return 0
    
    def __getTour__(self, t: Tour):
        """
        UNUSED!
        Returns True and makes inplace update if tour t already in swarm
        Otherwise false.
        """
        key = str(t.fullTrip)
        if key in self.tours:
            t = copy.deepcopy(self.tours[key])
            return True
        else:
            return False

    def updateBests(self):
        self.__updatePersonalBest__()
        return self.__updateGlobalBest__()

    def __updateGlobalBest__(self):
        globalBestUpdated = False
        for p in self.particles:
            if self.gBestSol == None:
                self.gBestSol = copy.deepcopy(p.curSol)
                globalBestUpdated = True
            elif self.gBestSol.totalCost > p.curSol.totalCost:
                self.gBestSol = copy.deepcopy(p.curSol)
                globalBestUpdated = True
        if globalBestUpdated:
            self.iterSinceImprov = 0
            print("################################\nNew Best Sol with Cost " + str(self.gBestSol.totalCost) + "\n#####################################")
        else:
            self.iterSinceImprov += 1
        return globalBestUpdated
    
    def __updatePersonalBest__(self):
        for p in self.particles:
            if p.curSol.totalCost < p.pBestSol.totalCost:
                p.pBestSol = copy.deepcopy(p.curSol)
                p.newBestFound()
            else:
                p.noNewBestFound()

    def printSwarm(self):
        """
        Prints result/current state of swarm
        """
        print("Used Path Relinking Versions: " + str(self.prVersion))
        print("Calculated Solutions: " + str(len(self.solutions)))
        print("Calculated Tours: " + str(len(self.tours)))
        print("Best Solution Found:")
        self.gBestSol.printSolution()

    def __deepcopy__(self, memodict={}):
        newSwarm = Swarm(self.instance)
        newSwarm.particles = [copy.deepcopy(p) for p in self.particles]
        newSwarm.solutions = copy.deepcopy(self.solutions)
        newSwarm.gBestSol = copy.deepcopy(self.gBestSol)
        newSwarm.tours = copy.deepcopy(self.tours)
        newSwarm.prVersion = copy.deepcopy(self.prVersion)
        newSwarm.iterSinceImprov = self.iterSinceImprov
        print("Swarm copied.")
        return newSwarm

    def __getAverageParticleVelocity__(self):
        """
        UNUSED
        For Debugging Purposes
        """
        veloPos = 0
        veloNeg = 0
        countPos =1
        countNeg = 1
        for p in self.particles:
            
            velo = p.__getAverageVelocity__()
            if velo[1]!="None":
                veloNeg+=velo[1]
                countNeg+=1
            if velo[0]!="None":
                veloPos+=velo[0]
                countPos+=1
        
        if countPos == 0 or countNeg == 0:
            return " Error calculating Avg Velocity"
        else:
            return "Neg: " + str(veloNeg/countNeg) + " @" + str(countNeg) + "; Pos: " + str(veloPos/countPos) + " @" + str(countPos)