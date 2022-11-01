from datetime import timedelta
from math import floor
from minizinc import Instance, Model, Solver
import math
import sys



def createSubsetDznFile(customers):
    """
    Creates a .dzn File with a list of customer subsets.
    :param customers: List of customers, i.e. [1,2,3,4,5], for which all possible subsets will be created. Needs to be in ascending order
    """
    # <PreProcessing>
    ## Generate Customer Sets (required for subtour elimination constraint)
    ### Customers (can probably be any combination of node numbers)
    ### Enter Set of Customers here (be aware of correct numeration!):
    #customers = [1,2,3,4,5]
    #customers = [2,3,4]
    

    numSubsets = int(math.pow(2, len(customers))-1) # without empty set
    customersInSubset = [0]*numSubsets
    binaryMapOfSubsets = list()
    for j in range(1, numSubsets+1): # Python range excludes last value
        temp = [0]*len(customers)
        i = 0
        n = j
        while n>0:
            temp[i] = n%2
            n = math.floor(n/2)
            i = i + 1
        binaryMapOfSubsets.append(temp)

    for j in range(0, numSubsets): # hier mit Range 0 bis vorletzte
        temp2 = set()    
        for i in range(len(customers)):
            if(binaryMapOfSubsets[j][i]==1):
                temp2.add(customers[i])
        customersInSubset[j] = temp2
                
    subsetsString = str(customersInSubset)

    ## Print Parameters to .dzn file
    textfile = open("/dzn/customerSubsets.dzn", "w")
    textfile.write("numSubsets = " + str(numSubsets) + ";\n" + "customersInSubset = " + str(customersInSubset) + ";")
    textfile.close()
    ## Read Parameters from .dzn file for Debugging/Controlling
    with open("/dzn/customerSubsets.dzn") as f:
        print(f.read())
    # </Preprocessing>
    return numSubsets

if __name__ == '__main__':
    if len(sys.argv)==4:
        dznFileName = sys.argv[1]
        customerIDStart = int(sys.argv[2])
        customerIDEnd = int(sys.argv[3])
        customers = [i for i in range(customerIDStart,customerIDEnd+1)]
    elif len(sys.argv)==2:
        dznFileName = "/CLRPSD_M+QA_5K_2V_2F_4docker.dzn"
        customers = [1,2,3,4,5]    
    elif len(sys.argv)==1:
        dznFileName = "/CLRPSD_M+QA_3K_2V_1F_4docker.dzn"
        customers = [2,3,4]    
    else:
        print("Incorrect number of parameters given. Please input " +
            "filename of .dzn-file (with file-extension, i.e. myfile.dzn) " + 
            " and " + 
            " ID of first customer and ID of last customer, i.e. 1  5")
        print(sys.argv)
        exit()

    
    print(createSubsetDznFile(customers))

    # Load M+QA Model
    ## Add relevant files
    clrpsd = Model("/mzn/CLRPSD_M+QA_4docker.mzn")
    clrpsd.add_file("/dzn/customerSubsets.dzn")
    clrpsd.add_file("/dzn/"+str(dznFileName))

    # Find the MiniZinc solver configuration for Gecode
    gecode = Solver.lookup("gecode")
    #cplex = Solver.lookup("cplex")
    cp = Solver.lookup("cp")
    float = Solver.lookup("float")

    instance = Instance(gecode, clrpsd)

    result = instance.solve(timeout=timedelta(seconds=300), processes=8)

    f = result["f"] #3D nodes, nodes, vehicles
    fProceed = result["fProceed"] #4D nodes, nodes, vehicles, transportCapacity
    fReturn = result["fReturn"] #4D nodes, nodes, vehicles, transportCapacity
    routingCost = result["routingCost"] #4D nodes, nodes, vehicles, transportCapacity
    s = result["s"] #4D nodes, nodes, vehicles, transportCapacity: Strategy - preventive refill (1) or proceed (0)
    x = result["x"] #2D customers, facilities: Customer served by facility [0,1]
    y = result["y"] #1D facilities: Facility opened [0,1]
    z = result["z"] #2D facilities, vehicles: Vehicle operates from Facility [0,1]
    ZF = result["ZF"] # Zielfunktionswert

    # Find Tour traveled by vehicles
    for nodes1 in range(len(f)):
        for nodes2 in range(len(f[nodes1])):
            for vehicles in range(len(f[nodes1][nodes2])):
                if(f[nodes1][nodes2][vehicles] == 1):
                    print("Vehicle " + str(vehicles+1) + " travels from " + str(nodes1+1) + " to " + str(nodes2+1))

    # Find Refill-Strategies
    for nodes1 in range(len(s)):
        for nodes2 in range(len(s[nodes1])):
            for vehicles in range(len(s[nodes1][nodes2])):
                for transportCapacity in range(len(s[nodes1][nodes2][vehicles])):
                    if(s[nodes1][nodes2][vehicles][transportCapacity] == 1):
                        print("Preventive Restocking with remaining Capacity of " +  str(transportCapacity)
                        + " in vehicle " + str(vehicles+1) +  " after serving Customer " +  str(nodes1+1) + " before continueing to customer " + str(nodes2+1) )


    # Print ZF-Wert

    print("Zielfunktionswert " + str(ZF))


    #print(type(f))

    print(result["s"])