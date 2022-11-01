import importlib
from multiprocessing import Pool
from multiprocessing.pool import AsyncResult
from typing import List
import sys, os

import metaheuristik.quinteroaraujo.code.simils as simils
import metaheuristik.marinakis.code2.GLCENTPSO_Control as GLCENTPSO

class metaheuristicSolverClass:
    def __init__(self, instance):
        self.SimILS = simils.SimILS(instance)
        self.GLCENTPSO = GLCENTPSO.ClassGLCENTPSO(instance)

def metaheuristicInterface():

    # Choose Instance
    cwd = os.getcwd()
    try:
        allInstances = os.listdir(cwd+"/instances")
    except:
        allInstances = os.listdir(cwd+"/metaheuristik/instances")
    allInstancesTuple = [(i,iIndex) for iIndex,i in enumerate(allInstances)]
    allInstancesTupleString = ""
    for i in allInstancesTuple:
        allInstancesTupleString += str(i) + "\n"
    val = input("Choose from " + allInstancesTupleString + ": Enter Number...") 
    if val.isnumeric():
        index = int(val)
        if index in range(len(allInstances)):
            i = allInstances[index]
            importI = i[:-3]
            instanceModul = importlib.import_module("metaheuristik.instances."+str(importI))
            iX = instanceModul.createInstance()
            metaheuristicSolver = metaheuristicSolverClass(iX)
            #metaheuristic.execute(instanceModul.createInstance())
        else:
            print("Exit")
            exit()
    else:
        print("Exit")
        exit()

    # Number of metaheuristic executions
    val = input("Enter number of times metaheurisitc is executed (default is 1): ...")
    if val.isnumeric():
        execTimes = int(val)
    else:
        print("Exit")
        exit()

    # Number of iterations per Metaheuristic execution
    val = input("Enter number of iterations per metaheuristic-execution: ...")
    if val.isnumeric():
        iterations = int(val)
    else:
        print("Exit")
        exit()
    # Choose Metaheuristic
    val = input("Choose metaheuristic: GLCENTPSO by Marinakis (1) or SimILS by Quintero-Araujo et al. (2): 1/2...")
    if val == '1':
        print("GLCENTPSO")
        #iX = instanceModul.createInstance()
        #metaheuristic = GLCENTPSO.ClassGLCENTPSO(iX)
        metaheuristic = metaheuristicSolver.GLCENTPSO
        multiProcessHandler(metaheuristic.execute,(iterations, False, True, False, False),execTimes)
        #for i in range(execTimes):
        #    metaheuristic.execute(instanceModul.createInstance(),iterations,False,True,False,False)
    elif val =='2':
        print("SimILS")
        val = input("Enter maximum Safety Stock: ...")
        if val.isnumeric():
            maxSafetyStock = int(val)
            #iX = instanceModul.createInstance()
            # metaheuristicSolver = metaheuristicSolverClass(iX)
            #metaheuristic = simils.SimILS(iX)
            metaheuristic = metaheuristicSolver.SimILS
            multiProcessHandler(metaheuristic.execute,(maxSafetyStock,1000,100,5000, iterations),execTimes)
            #for i in range(execTimes):
            #    metaheuristic.execute(instanceModul.createInstance(),maxSafetyStock=5, maxIterStage2=iterations)
        else:
            print("Exit")
            exit()
        
    else:
        print("Exit")
        exit()


def multiProcessHandler(fun, args, iterations):
    numProcesses = 6
    pool = Pool(processes=numProcesses)
    processList: List[AsyncResult] = list()
    x = list(range(iterations))
    l = [x[i::numProcesses] for i in range(numProcesses)]
    for p in range(numProcesses):
        numIterations = len(l[p])
        processList.append(pool.apply_async(executeFunctionXtimes, args = (fun,args,numIterations)))
    pool.close()
    pool.join()
def executeFunctionXtimes(fun, args, iterations):
    for _ in range(iterations):
        fun(*args)

if __name__ == '__main__':
    metaheuristicInterface()

