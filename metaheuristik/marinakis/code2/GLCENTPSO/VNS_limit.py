from numpy import random as rr
import copy
from typing import Dict, List
from datetime import datetime
import itertools as ii
#from LRPClassObjects.ClassSwarm import Swarm
#from LRPClassObjects.ClassSolution import Solution
#from LRPClassObjects.ClassTour import Tour
import metaheuristik.marinakis.code2.LRPClassObjects as LRPObj
Swarm = LRPObj.Swarm
Solution = LRPObj.Solution
Tour = LRPObj.Tour

class VNSClass:
    def __init__(self, swarm: Swarm, limit = 50):
        self.swarm = swarm
        self.limit: int = 50


    def VNS_limit(self, s: Solution, C_vns: int = None):
        """
        Creates new Solutions based on Variable Neighborhood Search
        Local Search operators (selection and combination) based on Marinakis [67]

        Number of iterations is limited.
        """
        swarm = self.swarm
        startTimeVNS = datetime.now()
        newS = copy.deepcopy(s)
        if C_vns == None:
            C_vns = rr.randint(1,11)
            #print("C_vns:" + str(C_vns))
        #C_vns = 11 # Debug
        if C_vns <= 2:
            # 2opt, 3opt or 2+3opt
            #newS = __2opt3optSwaps__(newS,swarm, C_vns=C_vns)
            newS = self.do2opt3optSwaps(newS, swarm,C_vns=C_vns )
        elif C_vns == 3:
            # 1-0
            newS = self.multipleRoutes_relocate(s,swarm,mode=1)
        elif C_vns == 4:
            # 2-0
            newS = self.multipleRoutes_relocate(s,swarm,mode=2)
        elif C_vns == 5:
            # 1-1
            newS = self.multipleRoutes_exchange(s, swarm, mode=1)
        elif C_vns == 6:
            # 2-2
            newS = self.multipleRoutes_exchange(s,swarm,mode=2)
        elif C_vns == 7:
            # 2 opt and 1-0 relocate
            newS = self.multipleRoutes_relocate(s,swarm, mode=1)
            #newS = __2opt3optSwaps__(newS,swarm,1)
        elif C_vns == 8:
            # 2opt and 1-1 exchange
            newS = self.multipleRoutes_exchange(s, swarm, mode=1)
            #newS = __2opt3optSwaps__(newS, swarm, 1)
        elif C_vns == 9:
            # 2opt and 3opt and 1-1 exchange
            newS = self.multipleRoutes_exchange(s,swarm, mode=1)
            #newS = __2opt3optSwaps__(newS,swarm,2)
        elif C_vns == 10:
            # 2opt, 3opt, 1-0 insert, 1-1 exchange
            #newS = __2opt3optSwaps__(s, swarm, 5)
            newS = self.multipleRoutes_relocate(newS, swarm, mode=1)
            newS = self.multipleRoutes_exchange(newS, swarm, mode=1)
        
        #startTimeSol = datetime.now()
        #if not swarm.getSolution(newS):
        returnsol = s
        if swarm.isNewSolution(newS):
            if newS.updateSolution():
                swarm.storeSolution(newS)
                #stopTimeSol = datetime.now()
                #elapsedTimeSol = (stopTimeSol-startTimeSol).total_seconds()    
                #print("Time sol examination: " + str(elapsedTimeSol))
                if newS.totalCost < s.totalCost:
                    #return newS
                    returnsol = newS
                else:
                    #return s
                    returnsol = s
            else: 
                # No feasible Solution created, so carry on with previous Solution.
                #return s
                returnsol = s
        else:
            if newS.totalCost< s.totalCost:
                newS.updateSolution()
                #return newS
                returnsol = newS
            else:
                #return s
                returnsol = s
        stopTimeVNS = datetime.now()
        elapsedTimeVNS = (stopTimeVNS-startTimeVNS).total_seconds()
        #print("Time " + str(C_vns) + " VNS: " + str(elapsedTimeVNS))
        swarm.solutions = dict() 
        return returnsol
    

    def do2opt3optSwaps(self,s: Solution, swarm: Swarm, C_vns: int):
        """
        Handler Function for 2opt and 3opt. Returns a Solution with updated Tours.
        - C_vns = 1 -> 2opt
        - C_vns = 2 -> 3opt
        - C_vns = 5 -> 2opt and 3opt
        """
        newS = copy.deepcopy(s)
        for tourIndex in range(len(newS.tours)):
            tour = copy.deepcopy(newS.tours[tourIndex])
            if C_vns == 1:
                newTour = copy.deepcopy(self.singleRoute_2opt_limit(tour))
                newS.tours[tourIndex] = copy.deepcopy(newTour)
                newS.routes[newS.instance.facilities.index(newTour.facility)] = copy.deepcopy(newTour.routeVector)
            elif C_vns == 2:
                newTour = copy.deepcopy(self.singleRoute_3opt_limit(tour))
                newS.tours[tourIndex] = copy.deepcopy(newTour)
                newS.routes[newS.instance.facilities.index(newTour.facility)] = copy.deepcopy(newTour.routeVector)
        newS.pointerVectorByRoutes(newS.routes)
        newS.routingVector = [j for i in newS.routes for j in i]
        return newS


    def multipleRoutes_exchange(self,s: Solution, swarm: Swarm, mode: int):
        """
        Exchange the customers of two routes. 
        Does all combinations possible for the routes Parameter of the Solution Class.
        Then glues the routes Parameter together to create the routingVector and calls updateSolution. 
        
        Returns the best new created solution. If no new solution has been created, returns the given solution.

        Does *not change* the depot vector or pointer vector, as customers are exchanged from one open depot to another open depot.
        """
        
        bestExchangeSol: Solution = None
        
        lsMax: int = self.limit

        if mode == 1:
            routePairs = list(ii.combinations([r for r in s.routes if len(r)>0],2))
            routePairsWithCustomers = [(r1,)+(r2,) + (c1,c2) for r1,r2 in routePairs for c1 in r1 for c2 in r2] # list with all combinations of tuple (r1, r2, c1, c2)
            randomIndices = list(rr.choice(len(routePairsWithCustomers),min(lsMax,len(routePairsWithCustomers)),replace=False))
            randomTourPairsWithCustomers = [routePairsWithCustomers[pairIndex] for pairIndex in randomIndices]
            for r1, r2, c1, c2 in randomTourPairsWithCustomers:
                r1 = list(r1)
                r2 = list(r2)
                r1Index = s.routes.index(r1)
                r2Index = s.routes.index(r2)
                c1Index = r1.index(c1)
                c2Index = r2.index(c2)    
                newRoutes = [r[:] for r in s.routes]
                newRoutes[r1Index][c1Index] = c2
                newRoutes[r2Index][c2Index] = c1
                newPVector = s.pointerVectorByRoutes(newRoutes)
                newRVector = [j for i in newRoutes for j in i]
                newDVector = s.depotVectorByRoutes(newRoutes)
                sNew = copy.deepcopy(s)
                sNew.pointerVector = newPVector
                sNew.routingVector = newRVector
                sNew.depotVector = newDVector
                #if not swarm.getSolution(sNew):
                if swarm.isNewSolution(sNew):
                    #startTimeUS = datetime.now()
                    if sNew.updateSolution(swarm.tours):
                        #stopTimeUS = datetime.now()
                        #elapsedTimeUS = (stopTimeUS-startTimeUS).total_seconds()
                        swarm.storeSolution(sNew)
                        if bestExchangeSol == None:
                            bestExchangeSol = copy.deepcopy(sNew)
                        else:
                            if bestExchangeSol.totalCost > sNew.totalCost:
                                bestExchangeSol = copy.deepcopy(sNew)
                                # reset counter, as new best has been found
                                #lsNum = 0
                    #
                else:
                    sNew = copy.deepcopy(swarm.getSolutionByVectorsOfSolution(sNew))
                    if bestExchangeSol == None:
                            bestExchangeSol = copy.deepcopy(sNew)
                    else:
                        if bestExchangeSol.totalCost > sNew.totalCost:
                            bestExchangeSol = copy.deepcopy(sNew)
        elif mode == 2:
            routePairs = list(ii.combinations([r for r in s.routes if len(r)>0],2))                        
            routePairsWithCustomers = [(r1,)+(r2,) + (c1a,c1b,c2a,c2b) for r1,r2 in routePairs for c1a in r1 for c2a in r2 for c1b in r1 for c2b in r2 if c1a != c1b and c2a != c2b] # list with all combinations of tuple (r1, r2, c1, c2)
            randomIndices = list(rr.choice(len(routePairsWithCustomers),min(lsMax,len(routePairsWithCustomers)),replace=False))
            randomTourPairsWithCustomers = [routePairsWithCustomers[pairIndex] for pairIndex in randomIndices]
            for r1, r2, c1a, c1b, c2a, c2b in randomTourPairsWithCustomers:
                r1 = list(r1)
                r2 = list(r2)
                r1Index = s.routes.index(r1)
                r2Index = s.routes.index(r2)
                c1aIndex = r1.index(c1a)
                c1bIndex = r1.index(c1b)
                c2aIndex = r2.index(c2a)    
                c2bIndex = r2.index(c2b)    
                newRoutes = [r[:] for r in s.routes]
                newRoutes[r1Index][c1aIndex] = c2a
                newRoutes[r1Index][c1bIndex] = c2b
                newRoutes[r2Index][c2aIndex] = c1a
                newRoutes[r2Index][c2bIndex] = c1b
                newPVector = s.pointerVectorByRoutes(newRoutes)
                newRVector = [j for i in newRoutes for j in i]
                newDVector = s.depotVectorByRoutes(newRoutes)
                sNew = copy.deepcopy(s)
                sNew.pointerVector = newPVector
                sNew.routingVector = newRVector
                sNew.depotVector = newDVector
                #if not swarm.getSolution(sNew):
                if swarm.isNewSolution(sNew):
                    #startTimeUS = datetime.now()
                    if sNew.updateSolution(swarm.tours):
                        #stopTimeUS = datetime.now()
                        #elapsedTimeUS = (stopTimeUS-startTimeUS).total_seconds()
                        swarm.storeSolution(sNew)
                        if bestExchangeSol == None:
                            bestExchangeSol = copy.deepcopy(sNew)
                        else:
                            if bestExchangeSol.totalCost > sNew.totalCost:
                                bestExchangeSol = copy.deepcopy(sNew)
                                # reset counter, as new best has been found
                                #lsNum = 0
                    #
                else:
                    sNew = copy.deepcopy(swarm.getSolutionByVectorsOfSolution(sNew))
                    if bestExchangeSol == None:
                            bestExchangeSol = copy.deepcopy(sNew)
                    else:
                        if bestExchangeSol.totalCost > sNew.totalCost:
                            bestExchangeSol = copy.deepcopy(sNew)

        if bestExchangeSol == None:
            bestExchangeSol = s
        return bestExchangeSol

    def multipleRoutes_relocate(self,s: Solution, swarm: Swarm, mode: int):
        """
        For each customer in every route, relocate it at all possible places in the other routes (including closed routes/depots).
        Calculate the resulting Solution.
        Return best Relocate-Solution.

        Does change routingVector and pointerVector, and possibly also depotVector, if after relocation no customer
        is served by a facility anymore.
        """
        bestRelocateSol: Solution = copy.deepcopy(s)
        
        lsMax: int = self.limit
        
        # Combinations of two tours and one/two customer from  one tour, later placed at a random position
        routePairs = list(ii.combinations([r for r in s.routes if len(r)>0],2))
        
        
        if mode == 1:
            routePairsWithCustomers = [(r1,)+(r2,) + (c,) for r1,r2 in routePairs for c in r1] # list with all combinations of tuple (r1, r2, c)
            randomIndices = list(rr.choice(len(routePairsWithCustomers),min(lsMax,len(routePairsWithCustomers)),replace=False))
            randomTourPairsWithCustomers = [routePairsWithCustomers[pairIndex] for pairIndex in randomIndices]
            for r1, r2, c in randomTourPairsWithCustomers:
                # remove c from t1 and place it randomly in t2
                r1 = list(r1)
                r2 = list(r2)
                r1Index = s.routes.index(r1)
                r2Index = s.routes.index(r2)
                r1.remove(c)
                r2.insert(rr.randint(0,max(len(r2)-1,1)),c)
                newRoutes = [r[:] for r in s.routes]
                newRoutes[r1Index] = r1
                newRoutes[r2Index] = r2
                newPVector = s.pointerVectorByRoutes(newRoutes)
                newRVector = [j for i in newRoutes for j in i]
                newDVector = s.depotVectorByRoutes(newRoutes)
                sNew = copy.deepcopy(s)
                sNew.pointerVector = newPVector
                sNew.routingVector = newRVector
                sNew.depotVector = newDVector
                #if not swarm.getSolution(sNew):
                if swarm.isNewSolution(sNew):
                    #startTimeUS = datetime.now()
                    if sNew.updateSolution(swarm.tours):
                        #stopTimeUS = datetime.now()
                        #elapsedTimeUS = (stopTimeUS-startTimeUS).total_seconds()
                        swarm.storeSolution(sNew)
                        if bestRelocateSol == None:
                            bestRelocateSol = copy.deepcopy(sNew)
                        else:
                            if bestRelocateSol.totalCost > sNew.totalCost:
                                bestRelocateSol = copy.deepcopy(sNew)
                                # reset counter, as new best has been found
                                #lsNum = 0
                    #
                else:
                    sNew = copy.deepcopy(swarm.getSolutionByVectorsOfSolution(sNew))
                    if bestRelocateSol == None:
                            bestRelocateSol = copy.deepcopy(sNew)
                    else:
                        if bestRelocateSol.totalCost > sNew.totalCost:
                            bestRelocateSol = copy.deepcopy(sNew)
                            # reset counter, as new best has been found
                            #lsNum = 0
                
        elif mode == 2:
            routePairsWithTwoCustomers = [(r1,)+(r2,) + (c1,c2) for r1,r2 in routePairs for c1 in r1 for c2 in r1 if c1 != c2] # list with all combinations of tuple (r1, r2, c1, c2)
            randomIndices = list(rr.choice(len(routePairsWithTwoCustomers),min(lsMax,len(routePairsWithTwoCustomers)),replace=False))
            randomTourPairsWithTwoCustomers = [routePairsWithTwoCustomers[pairIndex] for pairIndex in randomIndices]
            for r1, r2, c1, c2 in randomTourPairsWithTwoCustomers:
                # remove c from t1 and place it randomly in t2
                r1 = list(r1)
                r2 = list(r2)
                r1Index = s.routes.index(r1)
                r2Index = s.routes.index(r2)
                r1.remove(c1)
                r1.remove(c2)
                pos = rr.randint(0,max(len(r2)-1,1))
                r2 = r2[:pos]+[c1,c2]+r2[pos:]
                newRoutes = [r[:] for r in s.routes]
                newRoutes[r1Index] = r1
                newRoutes[r2Index] = r2
                newPVector = s.pointerVectorByRoutes(newRoutes)
                newRVector = [j for i in newRoutes for j in i]
                newDVector = s.depotVectorByRoutes(newRoutes)
                sNew = copy.deepcopy(s)
                sNew.pointerVector = newPVector
                sNew.routingVector = newRVector
                sNew.depotVector = newDVector
                #if not swarm.getSolution(sNew):
                if swarm.isNewSolution(sNew):
                    #startTimeUS = datetime.now()
                    if sNew.updateSolution(swarm.tours):
                        #stopTimeUS = datetime.now()
                        #elapsedTimeUS = (stopTimeUS-startTimeUS).total_seconds()
                        swarm.storeSolution(sNew)
                        if bestRelocateSol == None:
                            bestRelocateSol = copy.deepcopy(sNew)
                        else:
                            if bestRelocateSol.totalCost > sNew.totalCost:
                                bestRelocateSol = copy.deepcopy(sNew)
                                # reset counter, as new best has been found
                                #lsNum = 0
                    #
                else:
                    sNew = copy.deepcopy(swarm.getSolutionByVectorsOfSolution(sNew))
                    if bestRelocateSol == None:
                            bestRelocateSol = copy.deepcopy(sNew)
                    else:
                        if bestRelocateSol.totalCost > sNew.totalCost:
                            bestRelocateSol = copy.deepcopy(sNew)
                            # reset counter, as new best has been found
                            #lsNum = 0
                
        
        

        if bestRelocateSol == None:
            bestRelocateSol = s
        return bestRelocateSol


    def singleRoute_2opt_limit(self,tour: Tour):
        """
        :param routeVector: ordered list containing the elements of the route.
        does limited number of 2opt swaps
        """
        lsNum: int = 0
        lsMax: int = self.limit
        newTour = copy.deepcopy(tour)
        bestTour = copy.deepcopy(newTour)
        routeVector = newTour.routeVector
        #if len(routeVector)==12:
        #    print()

        pairs = list(ii.combinations(routeVector,2))
        randomIndices = list(rr.choice(len(pairs),min(lsMax,len(pairs)),replace=False))
        randomPairs = [pairs[pairIndex] for pairIndex in randomIndices]
        for i,j in randomPairs:
            iIndex = routeVector.index(i)
            jIndex = routeVector.index(j)
            if iIndex>jIndex:
                temp = iIndex
                iIndex = jIndex
                jIndex = temp
            newRouteVector = self.__singleRoute_2opt_swap__(routeVector,iIndex,jIndex)
            newTour.routeVector = copy.deepcopy(newRouteVector)
            newTour.__updateFullTrip__()
            newTour.updateRoutingCost()
            if bestTour != None:
                if bestTour.routingCost > newTour.routingCost:
                    bestTour = copy.deepcopy(newTour)
                    #lsNum = 0
            else:
                bestTour = copy.deepcopy(newTour)
            lsNum +=1
        return bestTour

    def __singleRoute_2opt_swap__(self,routeVector: list(), pos1: int, pos2: int):
        """
        Does a 2opt swap, returns one new routeVector (list).
        :param routeVector: given Route to be swapped
        :param pos1: Position in Vector, where route is cut (node before midpart)
        :param pos2: Position in Vector where route is cut (End of Midpart)
        """
        t1 = list()
        t1+=routeVector[:pos1+1]
        mid = list(routeVector[pos1+1:pos2+1])
        mid.reverse() 
        t1+=mid
        t1+=routeVector[pos2+1:]

        return t1




    def singleRoute_3opt_limit(self,tour: Tour):
        """
        :param routeVector: ordered list containing the elements of the route.
        does limited number of 3opt swaps
        """
        lsNum: int = 0
        lsMax: int = self.limit
        newTour = copy.deepcopy(tour)
        bestTour = copy.deepcopy(newTour)
        createdToursDict = dict()
        createdToursDict.update({str(tour.routeVector):tour})
        #createdRoutes: List[int] = list()
        #createdRoutes.append(tour.routeVector)
        routeVector = newTour.routeVector

        triplets = list(ii.combinations(routeVector,3))
        indexTriplets = list(ii.combinations(range(len(routeVector)),3))
        randomIndices = list(rr.choice(len(triplets),min(lsMax,len(triplets)),replace=False))
        randomTriplets = [triplets[pairIndex] for pairIndex in randomIndices]
        randomIndexTriplets = [indexTriplets[pairIndex] for pairIndex in randomIndices]
        
        for i,j,k in randomIndexTriplets:
            if not (i<j<k):
                i,j,k = (sorted((i,j,k)))
            FourNewRouteVectors = self.__singleRoute_3opt_swap__(routeVector,i,j,k)
            for newRouteVector in FourNewRouteVectors:
                # 3opt swap creates 4 Routes. Some of them might be due to the way they are created be 
                # identical to the given input tour.
                #if newRouteVector != tour.routeVector:
                if str(newRouteVector) not in createdToursDict.keys():
                    newTour.routeVector = copy.deepcopy(newRouteVector)
                    newTour.__updateFullTrip__()
                    newTour.updateRoutingCost()
                    createdToursDict.update({str(newRouteVector):newTour})
                else:
                    #newTour = copy.deepcopy(tour)
                    newTour = copy.deepcopy(createdToursDict[str(newRouteVector)])
                if bestTour != None:
                    if bestTour.routingCost > newTour.routingCost:
                        bestTour = copy.deepcopy(newTour)
                        #lsNum = 0
                else:
                    bestTour = copy.deepcopy(newTour)
            lsNum +=1
        return bestTour

    def __singleRoute_3opt_swap__(self,routeVector:list(), pos1: int, pos2: int, pos3:int):
        """
        Does a 3opt swap, returning the 4 possible "unique" (meaning routes that can not also be created by 2opt) routes.
        """
        t1 = list()
        tAll = list()
        part1 = list()
        part2 = list()
        part3 = list()
        part4 = list()

        part1 += routeVector[:pos1+1]
        part2 += routeVector[pos1+1:pos2+1]
        part3 += routeVector[pos2+1:pos3+1]
        part4 += routeVector[pos3+1:]
        #e)
        t1 += part1
        a: List = list(part3)
        a.reverse()
        t1 += a
        t1 += part2
        t1 += part4
        tAll.append(copy.deepcopy(t1))
        #f)
        t1 = list()
        t1 += part1
        a: List= list(part2)
        a.reverse()
        t1 += a
        a: List = list(part3)
        a.reverse()
        t1 += a
        t1 += part4
        tAll.append(copy.deepcopy(t1))
        #g)
        t1 = list()
        t1 += part1
        t1 += part3
        a: List = list(part2)
        a.reverse()
        t1 += a
        t1 += part4
        tAll.append(copy.deepcopy(t1))
        #h)
        t1 = list()
        t1 += part1
        t1 += part3
        t1 += part2
        t1 += part4
        tAll.append(copy.deepcopy(t1))
        return tAll