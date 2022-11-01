from copy import deepcopy
from typing import Dict, List, Literal
#from metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance import LRPinstance
import metaheuristik.marinakis.code2.LRPClassObjects.ClassLRPinstance as ObjInstance
LRPinstance = ObjInstance.LRPinstance
class Tour:
    def __init__(self, routeVector: list, facility, instance: LRPinstance):
        if len(routeVector)>len(instance.customers):
            raise ValueError("RouteVector too long: " + str(routeVector))    
        self.routeVector = routeVector
        self.facility = facility
        self.instance = instance
        self.travelCostMatrix = self.instance.distanceMatrix
        self.demandProbMatrix = self.instance.demandProbMatrix
        self.totalVehicleCap = self.instance.totalVehicleCap
        self.routingCost = 0
        self.fullTrip = [facility]+self.routeVector+[facility]
        self.strategy = {e: {} for e in self.fullTrip}
        self.compactStrategy = dict()
        self.states = dict()
        self.thresholdReverse = list()
    def __updateFullTrip__(self):
        self.fullTrip = [self.facility]+self.routeVector+[self.facility]
    def __resetStrategy_(self):
        self.strategy = {e: {} for e in self.fullTrip}
    def updateRoutingCost(self):
        """
        Calculates the cost of a Tour and creates the ideal strategies.
        """
        
        self.__updateFullTrip__()
        
        self.__resetStrategy_()
        # dict initialisieren
        self.states = dict()
        
        
        
        if self.instance.useYangRoutingCost == False:
            # A) Recursion wise
            self.routingCost = __routingCostByRecursion__(self)
        elif self.instance.useYangRoutingCost == True:
            # B) Reverse wise      
            self.routingCost = __routingCostByYang__(self)
        
        
        return 0     
    def __copyTour__(self):
        """
        UNUSED
        Returns a new Tour Object with same values as input Tour object
        """
        newT = Tour(self.routeVector,self.facility,self.travelCostMatrix,self.demandProbMatrix,self.totalVehicleCap)
        newT.fullTrip = self.fullTrip
        newT.strategy = self.strategy
        newT.routingCost = self.routingCost
        newT.thresholdReverse = list(self.thresholdReverse)
        return newT
    def printTour(self):
        """
        Prints (some of) the parameters of a Tour
        """
        self.refineStrategies()
        print("Fulltrip:" + str(self.fullTrip))
        print("\nStrategy:") #+ str(self.strategy))
        #for key in self.strategy.keys():
        #    print("At node "+str(key) + ": " + str(self.strategy[key]))
        print("\nStrategy compact:")
        for key in self.compactStrategy.keys():
            print("At node "+str(key) + ": " + str(self.compactStrategy[key]))
        print("\nRouting Cost: " + str(self.routingCost))
        if len(self.thresholdReverse)!=0:
            print("\nThresholds: ")
            for cIndex in range(len(self.routeVector)):
                c = self.routeVector[cIndex]
                cIndexReverse = len(self.routeVector)-1-cIndex
                print("Threshold at node " + str(c) + ": "+ str(self.thresholdReverse[cIndexReverse]))

    def refineStrategies2(self):
        compactStrategy = dict()
        expectedDemandSoFar = 0
        for c, strategyC in self.strategy.items():
            compactCStrategy = dict()
            refillAt = None
            proceedUntil = None
            if c != self.facility:
                cIndex = self.instance.customers.index(c)
                expectedDemand = self.instance.expectedDemand[cIndex]
                expectedDemandSoFar+=expectedDemand
            for k,v in strategyC.items():
                if "proceed" in v:
                    proceedUntil = k
                    proceedCost = v[1]
                    #if k != 0:
                    #    refillAt = k-1
                    #    refillCost = strategyC[k-1][1]
                    break
                elif "refill" in v:
                    refillAt = k
                    refillCost = v[1]
            if refillAt != None and proceedUntil is None: #or self.totalVehicleCap-expectedDemandSoFar<proceedUntil)#expectedDemandSoFar>=self.totalVehicleCap):
                compactCStrategy.update({refillAt:["refill",refillCost]})
                expectedDemandSoFar = 0
            elif refillAt != None and self.totalVehicleCap-expectedDemandSoFar<proceedUntil:
                compactCStrategy.update({refillAt:["refill",refillCost]})
                expectedDemandSoFar = 0
            if proceedUntil != None: 
                compactCStrategy.update({proceedUntil:["proceed",proceedCost]})
            
            compactStrategy.update({c:compactCStrategy})
        return compactStrategy
    def refineStrategies(self):
        """
        The strategy parameter (dictionary) after finishing a calculation of a route might contain strategies for states
        that are not actually reachable. Remove these here:
        """
        s2 = self.refineStrategies2()
        compactStrategy = deepcopy(s2)
        self.compactStrategy = s2
        return 0
        # remove unreachable "full states". (a vehicle can only )
        #compactStrategy = deepcopy(self.strategy)
        for strategyAtElement in range(2,len(self.strategy)):
            previousCustomer = self.fullTrip[strategyAtElement-1]
            currentCustomer = self.fullTrip[strategyAtElement]
            strategyAtPrevious = compactStrategy[previousCustomer] #thats a dictionary
            strategyAtCurrent = compactStrategy[currentCustomer]
            refinedStAtCur = dict()
            for previousState in strategyAtPrevious.keys():
                decision = strategyAtPrevious[previousState][0] # "proceed" or "refill"
            
                currentDemands = self.__possibleDemandsOfCustomer__(currentCustomer-1)
                
                for demand in currentDemands:
                    if decision == "proceed":
                        currentState = previousState - demand
                    elif decision == "refill":
                        currentState = self.totalVehicleCap - demand
                    if currentState in strategyAtCurrent.keys():
                        refinedStAtCur.update({currentState:strategyAtCurrent[currentState]})
                    else:
                        # Sometimes the Strategy willingly accepts the risk of not being able to serve a customer at arrival
                        # and needing to do a unscheduled refill (roundtrip to depot and back again), as this might be cheaper
                        # than preventive refilling.
                        # In that case, the possible states ("currentstate") regarding the remaining load created in the loop above
                        # might not all be depicted in the strategy of the next customer. This is intentional and fully correct.
                        a = 1
            compactStrategy.update({currentCustomer:refinedStAtCur})    
            
        self.compactStrategy = compactStrategy

                
                   
    def __possibleDemandsOfCustomer__(self,element):
        """
        element: customer, as index position in customers List
        """
        demandProb = self.demandProbMatrix[element]
        possibleDemands = list()
        for k in range(len(demandProb)):
            if demandProb[k]>0:
                possibleDemands.append(k)
        return possibleDemands
    
    def __deepcopy__(self, memodict={}):
        newT = Tour(self.routeVector[:],self.facility, self.instance)
        newT.routingCost = self.routingCost
        newT.fullTrip = self.fullTrip[:]
        newT.strategy = self.__deepcopyDict__(self.strategy) # dict(self.strategy)
        newT.compactStrategy = self.__deepcopyDict__(self.compactStrategy) # dict(self.compactStrategy) # deepcopy(self.compactStrategy)
        newT.states = self.__deepcopyDict__(self.states) #dict(self.states) #deepcopy(self.states)
        newT.thresholdReverse = list(self.thresholdReverse)
        return newT

    def __deepcopyDict__(self, aDict: Dict):
        newDict = dict()
        for key, value in aDict.items():
            newDict[key] = value
        return newDict

    
                    


#########################################
mycount = 0

def __routingCostByRecursion__(myTour: Tour):
    """
    Calculates the routing cost by recursion. Faster when no stochastic demand, slower otherwise.
    """
    return __routingCostFunc__(0,myTour.totalVehicleCap, myTour)

def __routingCostByYang__(myTour: Tour):
    """
    ONLY WORKS WITH INTEGER DEMAND!
    
    Uses a rather smart approach to calculate the routing cost by reverse calculation. 
    For each customer in the route reversed, the costs for refilling and continuing the route are calculated.
    Then, for decreasing remaining capacity after this customer, the cost for proceeding the route are calculated.
    Once the refilling costs are cheaper than proceeding, the corresponding remaining capacity is the threshold value.
    At this time, the remaining options for decreasing capacity should always be dealt with by refilling, as this is cheaper than continueing.

    Threshold value therefore means: if remaining capacity of vehicle after serving current customer is greater or equal to threshold value,
    than proceed to next customer. If remaining capacity is less than threshold, refill at depot, than proceed to next customer.

    This procedure is based on the works of Yang, Wen-Huei; Mathur, Kamlesh; Ballou, Ronald H. (2000): Stochastic Vehicle Routing Problem with Restocking, specifically pages 102-103. 

    Faster than routingCostByRecursion when stochastic demand, slower otherwise.

    Additionally, another "smart" approach is added: in each calculation of routing costs for a remaining demand of k (starting with k = vehicleCap),
    the routing costs for a remaining demand of vehicleCap-k get calculated, too - here called the "reverese" routing cost, proceedCostRevK. 
    The basic idea here is, that once those two costs are equal, the demands between k and vehicleCap-k create the same costs. 
    This allows to skip the explicit calculation of those "in-between" demands. 
    This procedure improves computation time for instances with large vehicleCaps. 

    """
    routingCost = 0
    refillCostListReverse = [None]*len(myTour.routeVector) # first entry is the cost of the last customer on tour
    proceedCostListReverse = [None]*len(myTour.routeVector)
    threshold = [None]*len(myTour.routeVector)
    customerReverse = [myTour.routeVector[i] for i in range(len(myTour.routeVector)-1,-1,-1)]
    if len(customerReverse)==0:
        print("Empty Route, no calculation.")
        myTour.strategy[myTour.facility][myTour.totalVehicleCap] = ["proceed",routingCost]
        myTour.thresholdReverse = list(threshold)
        return 0
    for cIndex in range(len(customerReverse)):
        atCustomerIndex, alreadyKnownCost, thresholdC = __getStoredRoutingCost__(myTour, cIndex)
        if atCustomerIndex != None:
            c = customerReverse[cIndex]
            proceedCostListReverse[cIndex] = alreadyKnownCost
            for i in range(0,thresholdC):
                myTour.strategy[c][i] = ["refill",alreadyKnownCost[i]]    
            for i in range(thresholdC,myTour.totalVehicleCap+1):
                myTour.strategy[c][i] = ["proceed",alreadyKnownCost[i]]
            threshold[cIndex]=thresholdC    
        else:
            c = customerReverse[cIndex]
            
            # last customer (or first customer in reverse order)
            if cIndex == 0:
                threshold[cIndex] = 0
                costBackToDepot = round(myTour.travelCostMatrix[c][myTour.facility],2)
                refillCostListReverse[cIndex] = costBackToDepot
                proceedCostListReverse[cIndex] = [costBackToDepot]*(myTour.totalVehicleCap+1)
                for i in range(0,myTour.totalVehicleCap+1):
                    myTour.strategy[c][i] = ["proceed",costBackToDepot]
            # other customers (previous customers)
            else:
                cNext = customerReverse[cIndex-1]
                # refillCost: cost if after serving customer cIndex the vehicle is refilled before visiting next customer
                refillCost = __refillCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse)
                refillCostListReverse[cIndex]= refillCost
                proceedCostListReverse[cIndex] = [None]*(myTour.totalVehicleCap+1)
                # k: remaining Cap after serving customer cIndex
                for k in range(myTour.totalVehicleCap,-1,-1):
                    proceedCost = 0
                    proceedCost = __proceedCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse, k)
                    proceedCost+= round(myTour.travelCostMatrix[c][cNext],2)
                    # For demand vehicleCap-k:
                    proceedCostRevK =  __proceedCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse, myTour.totalVehicleCap-k)
                    proceedCostRevK+= round(myTour.travelCostMatrix[c][cNext],2)
                    if proceedCostRevK <= refillCost and proceedCost < refillCost:
                        for m in range(myTour.totalVehicleCap-k-1,-1,-1):
                                myTour.strategy[c][m] = ["refill",refillCost]
                                proceedCostListReverse[cIndex][m] = refillCost
                        threshold[cIndex] = myTour.totalVehicleCap-k  
                        if proceedCostRevK == proceedCost:
                            # Case 1: proceedCostRevK of vehicleCap-k is equal to proceedCost of k
                            # so the cost for the demand "in-between" is the same.
                            for m in range(k,myTour.totalVehicleCap-k-1,-1):
                                myTour.strategy[c][m] = ["proceed",proceedCostRevK]
                                proceedCostListReverse[cIndex][m] = proceedCostRevK
                              
                        elif proceedCostRevK > proceedCost:
                            # Fall 2: berechne proceedCost weiter bis gleich proceedCostRevK
                            # Case 2: proceedCostRevK of vehicleCap-k is greater than proceedCost of k.
                            # so we need to find the remaining demand m for which they are equal,
                            # and then the cost for the demand "in-between" m and vehicleCap-k is the same.
                            for m in range(k,myTour.totalVehicleCap-k-1,-1):
                                proceedCost2 = __proceedCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse, m)
                                proceedCost2+= round(myTour.travelCostMatrix[c][cNext],2)
                                myTour.strategy[c][m] = ["proceed",proceedCost2]
                                proceedCostListReverse[cIndex][m] = proceedCost2

                                proceedCostRev2 = __proceedCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse, myTour.totalVehicleCap-m)
                                proceedCostRev2 += round(myTour.travelCostMatrix[c][cNext],2)
                                myTour.strategy[c][myTour.totalVehicleCap-m] = ["proceed",proceedCostRev2]
                                proceedCostListReverse[cIndex][myTour.totalVehicleCap-m] = proceedCostRev2

                                if proceedCost2 == proceedCostRev2:
                                    #for m2 in range(m,myTour.totalVehicleCap-k-1,-1):
                                    if m >= myTour.totalVehicleCap-m:
                                        1
                                    else:
                                        2
                                    for m2 in range(m,myTour.totalVehicleCap-m,-1):
                                        myTour.strategy[c][m2] = ["proceed",proceedCostRev2]
                                        proceedCostListReverse[cIndex][m2] = proceedCostRev2   
                                    break    
                        #
                        elif proceedCostRevK < proceedCost:
                            1 
                        break

                    if proceedCost <= refillCost:
                        myTour.strategy[c][k] = ["proceed",proceedCost]
                        threshold[cIndex] = k
                        proceedCostListReverse[cIndex][k] = proceedCost
                    else:
                        for m in range(k,-1,-1):
                            myTour.strategy[c][m] = ["refill",refillCost]
                            proceedCostListReverse[cIndex][m] = refillCost
                        break
                # While debugging I noticed that there are some cases where it is for some reason never cheaper to proceed to the next customer
                # than to refill. I couldn't quite figure out why, but to prevent the code from breaking I added this case here. It sets
                # the threshold value to vehicleCap+1, meaning that the vehicle is always refilled after serving a customer. 
                if threshold[cIndex] is None:
                    threshold[cIndex] = myTour.totalVehicleCap+1
                proceedCostListReverse[cIndex] = [round(cost,2) for cost in proceedCostListReverse[cIndex]]
            __storeRoutingCost__(myTour, proceedCostListReverse, cIndex, threshold[cIndex])
    # From Facility to first customer on route:
    cost = __proceedCostByYang__(myTour, len(myTour.routeVector), customerReverse+[myTour.facility], proceedCostListReverse, myTour.totalVehicleCap)
    routingCost += cost
    routingCost += myTour.travelCostMatrix[myTour.facility][c]
    myTour.strategy[myTour.facility][myTour.totalVehicleCap] = ["proceed",routingCost]
    myTour.thresholdReverse = list(threshold)
    
    return routingCost

def __storeRoutingCost__(myTour: Tour, costListReverse, cIndexToBeStored, threshold):
    """
    Test have shown that storing routing cost is quite expensiv, but still about 40% faster than Yang Routing Cost without storing. 
    """
    #return 0
    costDict = myTour.instance.costDict
    customerReverse = [myTour.routeVector[i] for i in range(len(myTour.routeVector)-1,-1,-1)]
    key = "F:"+str(myTour.facility)
    cIndex = 0
    while cIndex <= cIndexToBeStored:
        c = customerReverse[cIndex]
        key += ":"+str(c)
        cIndex += 1    
    costs = costListReverse[cIndexToBeStored]
    costs = __listToString__(costs+[threshold])
    if threshold is None:
        print()
    costDict.update({key:(cIndexToBeStored,costs)})
    
    return 0

def __getStoredRoutingCost__(myTour: Tour, cIndexRequired):
    #return None, None
    customerReverse = [myTour.routeVector[i] for i in range(len(myTour.routeVector)-1,-1,-1)]
    costDict = myTour.instance.costDict
    keyRequired = "F:"+str(myTour.facility)
    cIndex = 0
    while cIndex <= cIndexRequired:
        c = customerReverse[cIndex]
        keyRequired += ":"+str(c)
        cIndex += 1    
    if keyRequired in costDict.keys():
        atCustomerIndex, alreadyKnownCost = costDict[keyRequired]    
        listCostAndThreshold = __stringToList__(alreadyKnownCost)
        threshold = int(listCostAndThreshold.pop())
        alreadyKnownCost = listCostAndThreshold
        return atCustomerIndex, alreadyKnownCost, threshold
    else:
        return None,None,None
    
def __listToString__(mylist: List) -> Literal:
    myString = ""
    for i, s in enumerate(mylist):
    #for i in range(len(mylist)):
        if s is None:
            1
        myString+= str(s) + ";"
    return myString

def __stringToList__(myString: Literal) -> List:
    myList = list(myString.split(";"))
    myList.pop() # Just a ;
    #print(myList)
    myList = [float(string) for string in myList]
    return myList


def __proceedCostByYang__(myTour: Tour, cIndexRev, customerReverse: List, proceedCostListReverse: List, remainingCap: int, facility = False):
    cNextIndex = cIndexRev-1
    cNext = customerReverse[cNextIndex]
    proceedCost = 0
    facility = myTour.facility
    distance1 = myTour.travelCostMatrix[cNext][facility]
    distance2 = myTour.travelCostMatrix[facility][cNext]
    distanceRefill = distance1+distance2
    demandProb = myTour.demandProbMatrix[cNext-1]
    demandDict = myTour.instance.demand[cNext-1]
    vehicleCap = myTour.totalVehicleCap
    
    proceedCostListReversecNextIndex = proceedCostListReverse[cNextIndex]
    
    try:
        proceedCost = sum([v*proceedCostListReversecNextIndex[remainingCap-k] for k,v in demandDict.items() if k <= remainingCap])
        #proceedCost = sum([round(v*proceedCostListReversecNextIndex[remainingCap-k],2) for k,v in enumerate(demandProb) if k <= remainingCap and v > 0])
        proceedCost += sum([v*(proceedCostListReversecNextIndex[vehicleCap-k]+distanceRefill) for k,v in demandDict.items() if k > remainingCap])
        #proceedCost += sum([round(v*(proceedCostListReversecNextIndex[vehicleCap-k]+distanceRefill),2) for k,v in enumerate(demandProb) if k > remainingCap and v > 0])
    except:
        # This is a bug that rarely appears, but I dont know why. Somehow, there are None Values in proceedCostListReverse, and I dont get how they appear there. 
        proceedCost = 99999999999
    
    return proceedCost

def __kProb__(remainingCap, vehicleCap, demandProb, demandDict: Dict):
    #kWithPosProbRemaining = [k for k in range(0, remainingCap+1) if demandProb[k]>0]
    kWithPosProbRemaining = [k for k in demandDict.keys() if k in range(0, remainingCap+1)]
    #kWithPosProbOver = [k for k in range(remainingCap+1, vehicleCap+1) if demandProb[k]>0]
    kWithPosProbOver = [k for k in demandDict.keys() if k in range(remainingCap+1, vehicleCap+1)]
    return kWithPosProbOver, kWithPosProbRemaining

def __refillCostByYang__(myTour: Tour, cIndex, customerReverse: List, proceedCostListReverse: List):
    # Next = next customer in Tour after cIndex customer.
    # However, all lists are in reverse order, as we first calculate the costs for the last customer, then the second last and so on.
    # so next customer is before the current customer in the reversed list.
    c = customerReverse[cIndex]
    cNext = customerReverse[cIndex-1]
    cNextIndex = cIndex-1
    routingCost = 0
    proceedCost = 0
    routingCost += round(myTour.travelCostMatrix[c][myTour.facility] + myTour.travelCostMatrix[myTour.facility][cNext],2)
    proceedCost = __proceedCostByYang__(myTour, cIndex, customerReverse, proceedCostListReverse, myTour.totalVehicleCap)
    routingCost += proceedCost
    return routingCost

def __routingCostFunc__(currentElement, remainingCap, myTour:Tour):
    """
    Returns the Cost of Routing from this node onwards taking into account the two strategies "proceed" and "refill".
    :param currentElement: current Element in the Routing Vector, i.e. the first element to be visited might be Node #5
    :param remainingCap: remaining Capacity of Vehicle after having served the current Element
    :param myTour:Tour: Tour Class containing all relevant (static) Tour information.
    """
    

    routingCost = 0 # f_j(q): Cost after serving current element j with now remaining demand q, before continueing to next customer j+1
    
    #expRemainingDemand = __remainingExpectedDemand__(currentElement,myTour)
    maxRemainingDemand = __worstCaseRemainingDemand__(currentElement, myTour)
    maxRemainingDemand = myTour.totalVehicleCap
    
    key = str([currentElement, remainingCap])
    # Check if cost f_j(q) has already been calculated in this Tour.
    if key in myTour.states.keys():
        routingCost = myTour.states[key]
    else:
        # if next Element is the facility, the cost are just the trip back to facility, independent of remaining demand.
        if myTour.fullTrip[currentElement+1] == myTour.facility:
            routingCost = myTour.travelCostMatrix[myTour.fullTrip[currentElement]][myTour.fullTrip[currentElement+1]]
            global mycount
            mycount += 1
            myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["proceed",routingCost]
            #print(str(mycount))
        else:
            # If remainingCap is 0, then always refill. If remainingCap is equal to totalVehicleCap, no refilling is needed, so always proceed.
            # Otherwise, choose whatever is cheaper. 
            if remainingCap > 0 and remainingCap < myTour.totalVehicleCap:
                # if remaining Cap is greater than the maximum possible demand on the remaining tour, then proceed.
                if remainingCap >= maxRemainingDemand: #or remainingCap >= expRemainingDemand * 10:
                    routingCost = __proceed__(currentElement, remainingCap, myTour)
                    myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["proceed",routingCost]
                else:
                    # Here is the funky stuff.
                    proceedCost = __proceed__(currentElement, remainingCap, myTour)
                    refillCost = __refill__(currentElement, remainingCap, myTour)
                    if proceedCost < refillCost:
                        myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["proceed",proceedCost]
                        a = 1
                    else:
                        myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["refill",refillCost]
                        a = 1
                    routingCost = min(proceedCost, refillCost)
            # remaining cap is total Cap: proceed to next customer.
            elif remainingCap == myTour.totalVehicleCap:
                routingCost = __proceed__(currentElement, remainingCap, myTour)
                myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["proceed",routingCost]
            
                
            else:
                # remainingCap is 0
                routingCost = __refill__(currentElement, remainingCap, myTour)
                myTour.strategy[myTour.fullTrip[currentElement]][remainingCap] = ["refill",routingCost]
        
        myTour.states[key] = routingCost
    #print(routingCost)
    return routingCost

def __remainingExpectedDemand__(currentElement, myTour:Tour):
    """
    Calculates the expected remaining demand on the route from this currentElement on.
    """
    expDemand = 0
    for e in range(currentElement+1,len(myTour.fullTrip)):
        expDemandE = 0
        node = myTour.fullTrip[e]
        if node != myTour.facility:
            expDemandE = myTour.instance.expectedDemand[myTour.fullTrip[e]-1]
        expDemand+=expDemandE
    #print(expDemand)
    return expDemand

def __worstCaseRemainingDemand__(currentElement, myTour:Tour):
    """
    Calculates the worst case remaining demand: assuming every remaining node happens to need
    the highest demand possible for this node.
    I.e., last node has demand 1,2,3 with possibility 0.5,0.4 and 0.1: returns 3 as this is the highest
    demand possible.
    """
    worstCaseDemand = 0
    for e in range(currentElement+1,len(myTour.fullTrip)):
        wCDemandE = 0
        node = myTour.fullTrip[e]
        if node != myTour.facility:
            
            wCDemandE = myTour.instance.highestDemand[node-1]
        worstCaseDemand+=wCDemandE
    return worstCaseDemand

def __proceed__(currentElement, remainingCap, myTour:Tour):
    """
    Returns the Cost of Routing from this node onwards if it is decided to **proceed** to the next node.
    :param currentElement: current Element in the Routing Vector, i.e. the first element to be visited might be Node #5
    :param remainingCap: remaining Capacity of Vehicle after having served the current Element
    :param myTour:Tour: Tour Class containing all relevant (static) Tour information.
    """
    routingCost = 0
    routingCost += myTour.travelCostMatrix[myTour.fullTrip[currentElement]][myTour.fullTrip[currentElement+1]]
    routingCost += __routingCostOfDemandLessEqualCap__(currentElement,remainingCap,myTour)
    routingCost += __routingCostOfDemandGreaterCap__(currentElement, remainingCap, myTour)
    return routingCost

def __routingCostOfDemandLessEqualCap__(currentElement, remainingCap, myTour:Tour):
    """
    Returns the Cost of Routing from this node onwards if it is decided to **proceed** to the next node and the demand of the next node is less or equal to the remaining capacity in the vehicle.
    :param currentElement: current Element in the Routing Vector, i.e. the first element to be visited might be Node #5
    :param remainingCap: remaining Capacity of Vehicle after having served the current Element
    :param myTour:Tour: Tour Class containing all relevant (static) Tour information.
    """
    routingCost = 0
    demandProbCustomer = myTour.demandProbMatrix[myTour.fullTrip[currentElement+1]-1]
    for k in range(0,remainingCap+1):
        #print("Current Element: " + str(currentElement) + "; remainingCap: " + str(remainingCap) + "; k: " + str(k)) 
        p = demandProbCustomer[k]
        # If Probability of demand being k is 0, then also routingCost is 0 (for this part of the tree), so no calculation is necessary.
        if p > 0:
            routingCost += __routingCostFunc__(currentElement = currentElement+1,remainingCap=remainingCap-k,myTour=myTour)*p
    return routingCost

def __routingCostOfDemandGreaterCap__(currentElement, remainingCap, myTour:Tour):
    """
    Returns the Cost of Routing from this node onwards if it is decided to **proceed** to the next node and the demand of the next node exceeds the remaining capacity of the vehicle.
    An additional tour via the depot again to this next node is required. 
    :param currentElement: current Element in the Routing Vector, i.e. the first element to be visited might be Node #5
    :param remainingCap: remaining Capacity of Vehicle after having served the current Element
    :param myTour:Tour: Tour Class containing all relevant (static) Tour information.
    """
    routingCost = 0
    demandProbCustomer = myTour.demandProbMatrix[myTour.fullTrip[currentElement+1]-1]
    travelCost = myTour.travelCostMatrix[myTour.fullTrip[currentElement+1]][myTour.facility]
    for k in range(remainingCap+1, myTour.totalVehicleCap+1): 
        #print("Demand greater remainingCap " + str(remainingCap) + " with Demand at " + str(k))
        p = demandProbCustomer[k]
        # If Probability of demand being k is 0, then also routingCost is 0 (for this part of the tree), so no calculation is necessary.
        if p > 0:
            routingCost += 2*travelCost*p
            routingCost += __routingCostFunc__(currentElement = currentElement+1,remainingCap=remainingCap-k+myTour.totalVehicleCap, myTour=myTour)*p
            #routingCost += 100 #penalty
    return routingCost

def __refill__(currentElement, remainingCap, myTour:Tour):
    """
    Returns the Cost of Routing from this node onwards if it is decided to **refill** at the depot befor continuing to the next node.
    :param currentElement: current Element in the Routing Vector, i.e. the first element to be visited might be Node #5
    :param remainingCap: remaining Capacity of Vehicle after having served the current Element
    :param myTour:Tour: Tour Class containing all relevant (static) Tour information.
    """
    routingCost = 0
    routingCost += myTour.travelCostMatrix[myTour.fullTrip[currentElement]][myTour.facility]
    routingCost += myTour.travelCostMatrix[myTour.facility][myTour.fullTrip[currentElement+1]]
    demandProbCustomer = myTour.demandProbMatrix[myTour.fullTrip[currentElement+1]-1]
    for k in range(myTour.totalVehicleCap+1):
        p = demandProbCustomer[k]
        # If Probability of demand being k is 0, then also routingCost is 0 (for this part of the tree), so no calculation is necessary.
        if p > 0:
            routingCost += __routingCostFunc__(currentElement+1, remainingCap=myTour.totalVehicleCap-k, myTour=myTour)*p
    return routingCost
