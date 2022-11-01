



from datetime import datetime

import sys


import metaheuristik.instances as instances



import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
LRPinstance = LRPObj.ClassLRPinstance

import metaheuristik.marinakis.code2.GLCENTPSO as GLCENTPSOObj
GLCENTPSOmainClass = GLCENTPSOObj.GLCENTPSOmain

class ClassGLCENTPSO():
    def __init__(self, instance):
        self.instance = instance
        self.GLCENTPSOmain = GLCENTPSOmainClass(instance)
    def execute(self, iterations: int, useCNTMP, useVNS, useVNSMP, liveGraph):
        instance = self.instance
        print(instance)
        instance.useYangRoutingCost = True
        starttime = datetime.now()
        print("Starttime: " +str(starttime))
        #GLCENTPSOmain = GLCENTPSOmainClass(instance)
        self.GLCENTPSOmain.doGLCENTPSO(iterations, useCNTMP, useVNS, useVNSMP, liveGraph)
        #GLCENTPSOObj.GLCENTPSO(instance,iterations, useCNTMP, useVNS, useVNSMP, liveGraph)
        endtime = datetime.now()
        print("Endtime: " + str(endtime)) 
        timeElapsed = (endtime-starttime).total_seconds()
        print("GLCENTPSO execution time in seconds: " + str(timeElapsed))

if __name__ == '__main__':
    manual = True
    if len(sys.argv)==7:
        instanceArg = sys.argv[1]
        iterations = int(sys.argv[2])
        useCNTMP = True if sys.argv[3] == "True" else False
        useVNS = True if sys.argv[4] == "True" else False
        useVNSMP = True if sys.argv[5] == "True" else False
        liveGraph = True if sys.argv[6] == "True" else False
        print("Config: " + 
            "\nuseCNTMP:" + str(useCNTMP) +
            "\nuseVNS:" + str(useVNS) +
            "\nuseVNSMP:" + str(useVNSMP) +
            "\nliveGraph:" + str(liveGraph)
            )
    elif len(sys.argv)==3:
        instanceArg = sys.argv[1]
        iterations = int(sys.argv[2])
        useCNTMP = True
        useVNS = True
        useVNSMP = True
        liveGraph = True
        print("Auto-Config: " + 
            "\nuseCNTMP:" + str(useCNTMP) +
            "\nuseVNS:" + str(useVNS) +
            "\nuseVNSMP:" + str(useVNSMP) +
            "\nliveGraph:" + str(liveGraph)
            )
    elif manual:
        instanceArg = "Gaskell21x5"#"Perl12x2sd"#"Perl12x2"#"Christofides50x5"#"Gaskell21x5sd"#"Perl12x2"#"Perl55x15"#
        iterations = 10
        useCNTMP = False
        useVNS = True
        useVNSMP = False
        liveGraph = False
    else:
        print("Incorrect number of parameters given. Please input either <instance:string> <iterations:integer> " +
            "or <instance:string> <iterations:integer> <useCNTMP:True/False> <useVNS:True/False> <useVNSMP:True/False> <liveGraph:True/False>")
        exit()

    #arg2 = sys.argv[2]
    #arg3 = sys.argv[3]
    #arg4 = sys.argv[4]
    
    if instanceArg == "An32k5":
        print("Executing Instance An32k5")
        instance = instances.An32k5Create()
    elif instanceArg == "Perl12x2":
        print("Executing Instance Perl12x2")
        instance = instances.Perl12x2Create() #203,98
    elif instanceArg == "Perl55x15":
        print("Executing Instance Perl55x15")
        instance = instances.Perl55x15Create() #1074,8 ; my best found 1179,9
    elif instanceArg == "Perl12x2sd":
        print("Executing Instance Perl12x2sd")
        instance = instances.Perl12x2sdCreate()
    elif instanceArg == "Christofides50x5":
        print("Executing Instance Christofides50x5")
        instance = instances.Christo50x5Create() # 549,4-582,7
    elif instanceArg == "Gaskell21x5":    
        print("Executing Instance Gaskell21x5")
        instance = instances.Gaskell21x5Create() #424,9
    elif instanceArg == "Gaskell21x5sd":    
        print("Executing Instance Gaskell21x5sd")
        instance = instances.Gaskell21x5sdCreate() #424,9
    else:
        #default
        print("Executing Default Instance Perl12x2")
        instance = instances.Perl12x2Create() #203,98
        iterations = 10

    #instance = instances.Perl12x2sdPoissonCreate()
    #instance = instances.Perl12x2Create()
    #instance = instances.Gaskell21x5sdPoissonCreate()
    instance = instances.Christo50x5Create()
    g = ClassGLCENTPSO(instance)
    g.execute(iterations, useCNTMP, useVNS, useVNSMP, liveGraph)
    