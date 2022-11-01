
import copy
from functools import reduce
from tqdm import tqdm
from typing import List
from datetime import datetime
from multiprocessing import Pool, Queue
from multiprocessing import Process
from numpy import random as rr
#import networkx as nx
#import matplotlib.pyplot as plt


#from GLCENTPSO.CNT import CNT
#from GLCENTPSO.VNS import VNS
#from GLCENTPSO.VNS_limit import VNS_limit
#from GLCENTPSO.ENT import ENT
import metaheuristik.marinakis.code2.GLCENTPSO.CNT as CNTModul
CNTClass = CNTModul.CNTClass
#import metaheuristik.marinakis.code2.GLCENTPSO.VNS as VNSClass
#VNS = VNSClass.VNS
import metaheuristik.marinakis.code2.GLCENTPSO.ENT as ENTModul
ENTClass = ENTModul.ENTClass

import metaheuristik.marinakis.code2.GLCENTPSO.VNS_limit as VNSModul
VNSClass = VNSModul.VNSClass
#VNS_limit = VNSlimitClass.VNS_limit
#from LRPClassObjects.ClassSwarm import Swarm
#from LRPClassObjects.ClassLRPinstance import LRPinstance
#from LRPClassObjects.ClassParticle import Particle
#from LRPClassObjects.ClassSolution import Solution
#from LRPClassObjects.ClassNetwork import SwarmNetwork
import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Particle = LRPObj.Particle
Swarm = LRPObj.Swarm
Solution = LRPObj.Solution
LRPinstance = LRPObj.LRPinstance
SwarmNetwork = LRPObj.SwarmNetwork




maxIteration: int = 1000

class GLCENTPSOmain:
    def __init__(self, instance: LRPinstance):
        self.instance = instance
        self.swarm = Swarm(self.instance)
        self.ENT = ENTClass(self.swarm)
        self.VNS = VNSClass(self.swarm)
        self.CNT = CNTClass(self.swarm)

    def doGLCENTPSO(self, iterations: int, useCNTMP = True, useVNS = True, useVNSMP = True, liveGraph = True):
        instance = self.instance
        startTime = datetime.now()
        #swarm = Swarm(instance)
        swarm = self.swarm
        #global maxIteration
        #maxIteration = iterations
        self.initialize(swarm)
        print("Swarm is initialized with " + str(len(swarm.solutions)) + " unique solutions.")
        #print(getsizeof(swarm))
        #makeRidiculousDict(swarm)
        self.doIteration(swarm, iterations, useCNTMP, useVNS, useVNSMP, liveGraph)
        #showGraph(swarm, iterations)
        for p in swarm.particles:
            print(p.curSol.routes)
        #net = SwarmNetwork(swarm,0)
        # net.drawBestSolution()
        # swarm initialize
        # do iteration
        stopTime = datetime.now()
        elapsedTime = (stopTime-startTime).total_seconds()
        self.saveStrategyFigureDocker(swarm,elapsedTime)
        return 0

    def saveStrategyFigureDocker(self,swarm: Swarm, elapsedTime: float):
        """
        Create graph of solution, store in folder with Docker-like path representation.
        """
        net = SwarmNetwork(swarm,0)
        # Docker Variant
        filenameStrategy = str("/metaheuristik/figures/glcentpso_"+swarm.instance.__str__()
            + "_TC-"+str(round(swarm.gBestSol.totalCost,2))
            + "_RC-"+str(round(sum(swarm.gBestSol.routingCosts),2))
            + "_TSec-"+str(round(elapsedTime,2))
            + "_Strategy"
            + ".svg"
        )
        filename = str("/metaheuristik/figures/glcentpso_"+swarm.instance.__str__()
            + "_TC-"+str(round(swarm.gBestSol.totalCost,2))
            + "_RC-"+str(round(sum(swarm.gBestSol.routingCosts),2))
            + "_TSec-"+str(round(elapsedTime,2))
            + ".svg"
        )
        net.drawBestStrategy(save=True, fileName=filenameStrategy, show=False)
        net.drawBestSolution(save=True, fileName=filename, show=False)



    def initialize(self,swarm: Swarm):
        ##########################
        # Best Found Solution TEST for 12x2
        #solCplex = Solution(swarm.instance)
        #solCplex.assignmentVector = [13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13]
        #solCplex.depotVector= [1,0]
        #solCplex.routingVector = [3,4,6,5,7,1,2,8,9,10,11,12]
        #solCplex.routingVector = [10, 12, 11, 5, 4, 7, 3, 2, 1, 6, 9, 8]
        #solCplex.pointerVector = [1,0]
        #solCplex.updateSolution()
        #p = Particle(solCplex,solCplex,solCplex)
        #p1 = copy.deepcopy(p)
        #swarm.particles.append(p)
        #swarm.storeSolution(solCplex)
        ############################
        
        for i in range(swarm.instance.numParticles):
            sol = Solution(swarm.instance)
            sol.randomSolution()
            p = Particle(sol,sol,sol)
            swarm.particles.append(p) 
            swarm.storeSolution(sol)
            
        swarm.updateBests()   
        #net = SwarmNetwork(swarm,0)
        #net.drawBestSolution().plot()
        return 0

    def showGraph(self,swarm: Swarm, maxIteration: int, iteration = "Final"):
        import os
        path = os.getcwd()
        print(path)
        if not os.path.exists(path+"/figures"):
            os.mkdir(path+"/figures")
        net = SwarmNetwork(swarm,0)
        net.drawBestSolution(show=True)
        #net.drawAllParticles()
        #net.drawBestStrategy(save=True, fileName="metaheuristik/marinakis/figures/strategy_iter_"+ str(iteration) + "_of_" + str(maxIteration) + "_ZF_"+str(round(swarm.gBestSol.totalCost,2)).replace(".",","), show=False)
        #net.drawBestStrategy(save=True, fileName="/figures/strategy_iter_"+ str(iteration) + "_of_" + str(maxIteration) + "_ZF_"+str(round(swarm.gBestSol.totalCost,2)).replace(".",","), show=False)
        net.drawBestStrategy(save=True, fileName="figures/strategy_iter_"+ str(iteration) + "_of_" + str(maxIteration) + "_ZF_"+str(round(swarm.gBestSol.totalCost,2)).replace(".",","), show=False)
        return 0

    def doIteration(self,swarm: Swarm,iterations: int, useCNTMP = True, useVNS = True, useVNSMP = True, liveGraph = True):
        import math
        

        startTime = datetime.now()
        
        #useCNTMP = True
        #useVNS = True
        #useVNSMP = True
        #liveGraph = True	 

        # Graph Debugging Test
        #showGraph(swarm=swarm)

        # VNS Performance Timing
        C_vns_list = [1,2,3,4,5,6,7,8,9,10,11]*7
        C_vns_time = [0]*11

        p1: Process = None
        p2: Process = None

        for i in tqdm(range(iterations), desc = "GLCENTPSO Iteration..."):
        #for i in range(1000):
            #print("Velo: "+str(swarm.getAverageParticleVelocity()))
            timeNow = datetime.now()
            timeElapsed = (timeNow - startTime).total_seconds()
            print("\nAt beginning of iteration " + str(i) + " known solutions: " + str(len(swarm.solutions))
                + "\nCalculation of associated routes took time: " + str(swarm.solroutecreationtime)
                + "\nSolution Finding Time: " + str(swarm.solfindingtime)
            )
            
            if swarm.iterSinceImprov > 250 or timeElapsed > 100000: # or len(swarm.solutions) >= math.factorial(len(swarm.particles[0].curSol.routingVector)):
                break
            
    #CNT    

            versionInt = rr.randint(1,3)
            if versionInt == 1:
                average = True
            elif versionInt == 2:
                average = False
            #average = True
            startTimeCNT = datetime.now()
            if useCNTMP:
                """
                startParam = datetime.now()
                currentParticles = copy.deepcopy(swarm.particles)
                param = zip(repeat(average,swarm.instance.numParticles),currentParticles,repeat(swarm,swarm.instance.numParticles),repeat(i, swarm.instance.numParticles), repeat(iterations, swarm.instance.numParticles))
                stopParam = datetime.now()
                elapsedTimeParam = (stopParam-startParam).total_seconds()
                print("#            CNT: Time to create param zip: " + str(elapsedTimeParam))
                """
                currentSolFindingTime = swarm.solfindingtime
                currentRouteCreationTime = swarm.solroutecreationtime
                """
                startTimeMPsol = datetime.now()
                q = Queue()
                processes: List[Process] = []
                rets = []
                
                for i in range(0,5):
                    pStart = i*14
                    pStop = i*14+14 # note: acutally +13, but list excludes last one
                    #proc = Process(target = __CNTdummy__,args=(q, average, swarm.particles[pStart:pStop], swarm, i, iterations, ))
                    #processes.append(proc)    
                for procs in processes:
                    procs.start()
                for procs in processes:
                    ret = q.get()
                    rets.append(ret)
                for procs in processes:
                    procs.join()
                #print(rets)
                stopTimeMPsol = datetime.now()
                elapsedTimeMPsol = (stopTimeMPsol-startTimeMPsol).total_seconds()
                print("#CNT: New Variant took time: " + str(elapsedTimeMPsol))
                #p5 = Process(target = __CNTdummy__,args=(q, average, swarm.particles[0:20], swarm, i, iterations, ))
                #p5.start()
                #print("start")
                #r = q.get()
                #p5.join()
                #print("Hm")
                #print(r)
                """
                ################################
                #swarm2 = copy.deepcopy(swarm)
                #swarm2 = swarm
                startTimeMPsol = datetime.now()
            
                pool = Pool(processes=5)
                proc1 = pool.apply_async(self.__CNTdummy2__,args=( average, swarm.particles[0:14], swarm, i, iterations,))
                proc2 = pool.apply_async(self.__CNTdummy2__,args=( average, swarm.particles[14:28], swarm, i, iterations,))
                proc3 = pool.apply_async(self.__CNTdummy2__,args=( average, swarm.particles[28:42], swarm, i, iterations,))
                proc4 = pool.apply_async(self.__CNTdummy2__,args=( average, swarm.particles[42:56], swarm, i, iterations,))
                proc5 = pool.apply_async(self.__CNTdummy2__,args=( average, swarm.particles[56:70], swarm, i, iterations,))

                pool.close()
                pool.join()
                resList = list()
                resList.append(proc1.get())
                resList.append(proc2.get())
                resList.append(proc3.get())
                resList.append(proc4.get())
                resList.append(proc5.get())
                stopTimeMPsol = datetime.now()
                elapsedTimeMPsol = (stopTimeMPsol-startTimeMPsol).total_seconds()
                #print(resList)

                # Store current Particles
                resList = resList[0]+resList[1]+resList[2]+resList[3]+resList[4]
                newParticles: List[Particle] = [r[0] for r in resList]
                swarm.particles = newParticles

                # Store Solutions
                solutions = [r[1] for r in resList if len(r[1])>0]
                [swarm.solutions.update(k) for k in solutions]

                # Store number of pr versions
                prVersions = [r[2] for r in resList]
                prVersionsDict = {"NOPR":0,"PRPB":0,"PRGB":0}
                for prVersion in prVersions:
                    prVersion: dict
                    for k,v in prVersion.items():
                        swarm.prVersion[k] =swarm.prVersion[k]+ v 

                # store SolFindingTime
                findingTimes = [r[3] for r in resList]
                additionalSolFindingTime = reduce(lambda a,b: a+b, findingTimes)
                swarm.solfindingtime = currentSolFindingTime+additionalSolFindingTime
                            
                # store SolRouteCreationTime
                creationTimes = [r[4] for r in resList]
                additionalSolRouteCreationTime = reduce(lambda a,b: a+b, creationTimes)
                swarm.solroutecreationtime = currentRouteCreationTime + additionalSolRouteCreationTime


                print("#CNT: Another New Variant took time: " + str(elapsedTimeMPsol))
                ################################
                """
                startTimeMPsol = datetime.now()
                pool = Pool(4)
                
                results = pool.starmap(__CNTmp__,param)
                
                pool.close()
                pool.join()

                
                newParticles: List[Particle] = [r[0] for r in results]
                
                #swarm.particles = copy.deepcopy(newParticles)   
                swarm.particles = newParticles
                

                # Store Solutions
                solutions = [r[1] for r in results if len(r[1])>0]
                [swarm.solutions.update(k) for k in solutions]

                # Store number of pr versions
                prVersions = [r[2] for r in results]
                prVersionsDict = {"NOPR":0,"PRPB":0,"PRGB":0}
                
                #prVersionsDict = {k: v  for i in prVersions for k,v in i.items()}
                for p in prVersions:
                    p: dict
                    for k,v in p.items():
                        #prVersionsDict[k] = prVersionsDict[k]+v 
                        swarm.prVersion[k] =swarm.prVersion[k]+ v 
                #swarm.prVersion = dict(prVersionsDict)
                
                # store SolFindingTime
                findingTimes = [r[3] for r in results]
                additionalSolFindingTime = reduce(lambda a,b: a+b, findingTimes)
                swarm.solfindingtime = currentSolFindingTime+additionalSolFindingTime
                            
                # store SolRouteCreationTime
                creationTimes = [r[4] for r in results]
                additionalSolRouteCreationTime = reduce(lambda a,b: a+b, creationTimes)
                swarm.solroutecreationtime = currentRouteCreationTime + additionalSolRouteCreationTime 

                stopTimeMPsol = datetime.now()
                elapsedTimeMPsol = (stopTimeMPsol-startTimeMPsol).total_seconds()
                print("#CNT: Time to read and merge sols: " + str(elapsedTimeMPsol)) 
                """
            else: 
                
                
                #for p in tqdm(swarm.particles,desc="CNT..."):
                #for p in swarm.particles:
                #for pIndex in tqdm(range(len(swarm.particles)), desc = "CNT..."):
                #CNT = CNTClass(swarm)
                for pIndex in range(len(swarm.particles)):
                    p = swarm.particles[pIndex]
                    #pNew = copy.deepcopy(CNT(average, p, i, swarm, iterations))
                    pNew = self.CNT.doCNT(average, p, i, iterations)
                    #if pNew.curSol.totalCost < swarm.gBestSol.totalCost:
                    #    print(" ####################################\n " +str(pNew.curSol.totalCost) + " ####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n####################################\n")
                    #p = pNew
                    #swarm.particles[pIndex] = copy.deepcopy(pNew)
                    swarm.particles[pIndex] = pNew

            print("After CNT (average = " +  str(average)+ ") at iteration " + str(i) + " known solutions: " + str(len(swarm.solutions)))
            print("Done PR types:" + str(swarm.prVersion))    
            stopTimeCNT = datetime.now()
            elapsedTimeCNT = (stopTimeCNT-startTimeCNT).total_seconds()
            print("CNT Iteration Time: " + str(elapsedTimeCNT) + "\n") 
            
            #particleChunks = [list(c) for c in mit.divide(6,swarm.particles)]
            #swarm.updateBests()
    # VNS   
            if useVNS:
                print("VNS Start at: " + str(datetime.now())) 
                startTimeVNS = datetime.now()
                if useVNSMP:
                    """
                    startParam = datetime.now()
                    currentParticles = copy.deepcopy(swarm.particles)
                    params = zip(currentParticles,repeat(swarm, swarm.instance.numParticles))
                    stopParam = datetime.now()
                    elapsedTimeParam = (stopParam-startParam).total_seconds()
                    print("#            VNS: Time to create param zip: " + str(elapsedTimeParam)) 
                    """
                    currentSolFindingTime = swarm.solfindingtime
                    currentRouteCreationTime = swarm.solroutecreationtime


                    ##################################
                    startTimeMPsol = datetime.now()
                    swarm2 = swarm

                    pool = Pool(processes=5)
                    proc1 = pool.apply_async(self.__VNSdummy2__,args=( swarm2.particles[0:14], swarm,))
                    proc2 = pool.apply_async(self.__VNSdummy2__,args=( swarm2.particles[14:28], swarm, ))
                    proc3 = pool.apply_async(self.__VNSdummy2__,args=(  swarm2.particles[28:42], swarm,))
                    proc4 = pool.apply_async(self.__VNSdummy2__,args=(  swarm2.particles[42:56], swarm,))
                    proc5 = pool.apply_async(self.__VNSdummy2__,args=(  swarm2.particles[56:70], swarm,))
                    pool.close()
                    pool.join()
                    resList = list()
                    resList.append(proc1.get())
                    resList.append(proc2.get())
                    resList.append(proc3.get())
                    resList.append(proc4.get())
                    resList.append(proc5.get())
                    stopTimeMPsol = datetime.now()
                    elapsedTimeMPsol = (stopTimeMPsol-startTimeMPsol).total_seconds()

                    # Store current Particles
                    resList = resList[0]+resList[1]+resList[2]+resList[3]+resList[4]
                    newParticles: List[Particle] = [r[0] for r in resList]
                    swarm2.particles = newParticles

                    # Store Solutions
                    solutions = [r[1] for r in resList if len(r[1])>0]
                    [swarm2.solutions.update(k) for k in solutions]


                    # store SolFindingTime
                    findingTimes = [r[2] for r in resList]
                    additionalSolFindingTime = reduce(lambda a,b: a+b, findingTimes)
                    swarm2.solfindingtime = currentSolFindingTime+additionalSolFindingTime
                                
                    # store SolRouteCreationTime
                    creationTimes = [r[3] for r in resList]
                    additionalSolRouteCreationTime = reduce(lambda a,b: a+b, creationTimes)
                    swarm2.solroutecreationtime = currentRouteCreationTime + additionalSolRouteCreationTime

                    print("#VNS: Another New Variant took time: " + str(elapsedTimeMPsol))

                    ##################################
                    """
                    startTimeMPsol = datetime.now()
                    pool = Pool(4)
                    results = pool.starmap(__VNSmp__,params)
                    pool.close()
                    pool.join()

                    
                    # Store new Particles
                    newParticles: List[Particle] = [r[0] for r in results]
                    #swarm.particles = copy.deepcopy(newParticles)
                    swarm.particles = newParticles

                    # store solutions
                    solutions = [r[1] for r in results]
                    [swarm.solutions.update(k) for k in solutions]
                    
                    # store SolFindingTime
                    findingTimes = [r[2] for r in results]
                    additionalSolFindingTime = reduce(lambda a,b: a+b, findingTimes)
                    swarm.solfindingtime = currentSolFindingTime+additionalSolFindingTime

                    # store SolRouteCreationTime
                    creationTimes = [r[3] for r in results]
                    additionalSolRouteCreationTime = reduce(lambda a,b: a+b, creationTimes)
                    swarm.solroutecreationtime = currentRouteCreationTime + additionalSolRouteCreationTime

                    stopTimeMPsol = datetime.now()
                    elapsedTimeMPsol = (stopTimeMPsol-startTimeMPsol).total_seconds()
                    print("#VNS: Time to read and merge sols: " + str(elapsedTimeMPsol)) 
                    """
                else:
                    
                    #for p in tqdm(swarm.particles, desc = "VNS..."):
                    #for p in swarm.particles:
                    #VNS = VNSClass(swarm)
                    for pIndex in range(len(swarm.particles)):
                    #for pIndex in tqdm(range(len(swarm.particles)), desc = "VNS..."):
                        p: Particle = swarm.particles[pIndex]
                        C_vns = C_vns_list[swarm.particles.index(p)]
                        C_vnsIndex = C_vns-1
                        
                        s = p.curSol    
                        #sNew: Solution = VNS(swarm,s)
                        sNew: Solution = self.VNS.VNS_limit(s)
                        #p.curSol = copy.deepcopy(sNew)
                        p.curSol = sNew
                        #swarm.particles[pIndex] = copy.deepcopy(p)
                        swarm.particles[pIndex] = p
                        #C_vns_time[C_vnsIndex] += elapsedTimeVNS
                    

                print("After VNS at iteration " + str(i) + " known solutions: " + str(len(swarm.solutions)))
                stopTimeVNS = datetime.now()
                elapsedTimeVNS = (stopTimeVNS-startTimeVNS).total_seconds()
                print("VNS Iteration Time: " + str(elapsedTimeVNS) + "\n") 
            
            
            if swarm.updateBests():
                if p1 != None and liveGraph == True:
                    #if p2 == None:
                    p2 = Process(target=self.showGraph, args=[swarm, iterations,i])    
                    p2.start()
                    p1.terminate()
                    p1.join()
                    p1: Process = None
                elif p2 != None and liveGraph == True:
                    #if p1 == None:
                    p1 = Process(target=self.showGraph, args=[swarm, iterations,i])    
                    p1.start()
                    p2.terminate()
                    p2.join()
                    p2: Process = None
                elif liveGraph == True:
                    p1 = Process(target=self.showGraph, args=[swarm, iterations,i])    
                    p1.start()
            
            
            # ENT
            #ENT = ENTClass(swarm)
            self.ENT.doENT()

            #proc.terminate()
            #proc.join()

            #swarm.solutions = {}
            print("Lösungsanzahl: "+str(len(swarm.solutions)))
        
        
        swarm.printSwarm()    

        #print("C_VNS Time: " +str(C_vns_time))
        return 0

    def __VNSdummy2__(self,pList: List[Particle], swarm: Swarm):
        resultList = list()
        for p in pList:
            #print("p")
            result = self.__VNSmp__(p, swarm)
            resultList.append(result)
        return resultList


    def __VNSmp__(self,p: Particle,swarm: Swarm):
        currentdict = dict(swarm.solutions)
        currentSolFindingTime = swarm.solfindingtime
        currentRouteCreationTime = swarm.solroutecreationtime
        s = p.curSol
        #VNS = VNSClass(swarm)
        sNew: Solution = self.VNS.VNS_limit(s)
        p.curSol = copy.deepcopy(sNew)
        returndict = {k:v for k,v in swarm.solutions.items() if k not in currentdict.keys()}
        #returndict = {}
        newSolFindingTime = swarm.solfindingtime
        differenceSolFindingTime = newSolFindingTime-currentSolFindingTime

        newRouteCreationTime = swarm.solroutecreationtime
        differenceRouteCreationTime = newRouteCreationTime - currentRouteCreationTime

        return [p,returndict, differenceSolFindingTime, differenceRouteCreationTime]

    """
    def __CNTdummy__(queue: Queue, average: bool, pList: List[Particle], swarm: Swarm, i: int, maxIteration: int):
        resultList = list()
        for p in pList:
            #print("p")
            result = __CNTmp__(average, p, swarm, i, maxIteration)
            resultList.append(result)
        #return resultList
        queue.put(resultList)
        #print("finished")
        return 0
    """
    def __CNTdummy2__(self,average: bool, pList: List[Particle], swarm: Swarm, i: int, maxIteration: int):
        resultList = list()
        for p in pList:
            #print("p")
            result = self.__CNTmp__(average, p, swarm, i, maxIteration)
            resultList.append(result)
        return resultList
        
        

    def __CNTmp__(self,average: bool, p: Particle, swarm: Swarm, i: int, maxIteration: int):
        starttime = datetime.now()
        currentdict = dict(swarm.solutions)
        currentPRVersion = dict(swarm.prVersion)
        currentSolFindingTime = swarm.solfindingtime
        currentRouteCreationTime = swarm.solroutecreationtime
        #CNT = CNTClass(swarm)
        p = self.CNT.doCNT(average, p, i, maxIteration)
        newSolutionsDict = {k:v for k,v in swarm.solutions.items() if k not in currentdict.keys()}
        #newSolutionsDict = {}
        #returnPRVersion = {}
        returnPRVersion = {k:v-currentPRVersion[k] for k,v in swarm.prVersion.items()}

        newSolFindingTime = swarm.solfindingtime
        differenceSolFindingTime = newSolFindingTime-currentSolFindingTime

        newRouteCreationTime = swarm.solroutecreationtime
        differenceRouteCreationTime = newRouteCreationTime - currentRouteCreationTime
        stoptime = datetime.now()
        elapsedtime = (stoptime-starttime).total_seconds()
        #print(elapsedtime)
        return [p,newSolutionsDict, returnPRVersion, differenceSolFindingTime, differenceRouteCreationTime]