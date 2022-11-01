
from typing import List, Dict
import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
SwarmNetwork = LRPObj.SwarmNetwork

import metaheuristik.quinteroaraujo.code.SimILSObjects as SimObj
SimILSSolution = SimObj.SimILSSolution

class SimNetwork(SwarmNetwork):
    def __init__(self, simSol: SimILSSolution):
        self.simSol = simSol
        self.instance = simSol.instance
        self.pos = self.__posDict__()
        self.edges = None
        self.edgesProceed = None
        self.edgeLabelsProceed: Dict = None
        self.edgesReturn = None
        self.edgeLabelsReturn: Dict = None
        self.edgeLabels: Dict = None
        self.edgeStyles: List = None
        self.edgeConnectionStyles: List = None

    def __posDict__(self):
        coord = self.simSol.instance.coordinates
        nodes = self.simSol.instance.customers+self.simSol.instance.facilities
        pos = {}
        for n in nodes:
            pos.update({n: coord[nodes.index(n)+1]}) # Offset of 1, as coordinate List in instances uses a placeholder for the first entry of [0,0]. We want to skip this one.
        return pos

    def __getSolutionEdges__(self):
        """
        returns a Dict containing the used edges and occurences: {[node1,node2]: occurences}
        only for the best solution of the swarm
        """
        edgeOccur = {}
        s = self.simSol
        for t in s.tours:
            edges = self.__getEdges__(t.fullTrip)
            for e in edges:
                if e in edgeOccur.keys():
                    occur = edgeOccur[e] + 1
                    edgeOccur[e] = occur
                else:
                    edgeOccur.update({e:1}) 
        return edgeOccur 

            
    def drawSolution(self, show = False, save=False, fileName="fig"):
        """
        Draws the routing network of the current solution.
        Note: Dont use show = True and save = True at the same time, as this doesnt work.
        """
        self.edges = self.__getSolutionEdges__()
        return self.__drawGraph__(show=show, save=save,fileName=fileName)    

    def drawBestStrategy(self, save=False, fileName="Fig", show=False):
        """
        Draws the routing network of the current solution, including the strategy (proceed/refill decisions).
        Note: Dont use show = True and save = True at the same time, as this doesnt work.
        """
        self.__getStrategyEdges__(self.simSol)
        return self.__drawGraph__(variant="strategy", save=save, fileName=fileName, show=show)
        