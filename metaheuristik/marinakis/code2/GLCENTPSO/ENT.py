#from LRPClassObjects.ClassSwarm import Swarm
#from LRPClassObjects.ClassParticle import Particle
from typing import List
import copy

import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Particle = LRPObj.Particle
Swarm = LRPObj.Swarm

class ENTClass:
    def __init__(self, swarm: Swarm):
       self.swarm = swarm

    def doENT(self):
        swarm = self.swarm
        numParticles = swarm.instance.numParticles
        
        for i in range(numParticles):
            p :Particle = swarm.particles[i]
            
            nSize = p.neighborhoodWidth
            neighbors:List[Particle] = [p]
            # Left Side
            if i-nSize < 0:
                j = nSize - i
                for k in range(numParticles-j, numParticles):
                    neighbors.append(swarm.particles[k])
            for k in range(max(i-nSize,0),i-1):
                neighbors.append(swarm.particles[k])
            # Right Side
            if i+nSize > (numParticles-1):
                j = i+nSize-(numParticles-1)
                for k in range(0,j):
                    neighbors.append(swarm.particles[k])
            for k in range(i+1,min(i+nSize,numParticles-1)):
                neighbors.append(swarm.particles[k])
            # Check Solutions
            for n in neighbors:
                if n.curSol.totalCost < p.lBestSol.totalCost:
                    p.lBestSol = copy.deepcopy(n.curSol)