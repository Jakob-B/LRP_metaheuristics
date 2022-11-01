from numpy import arctan
from typing import List	

class splittingPolicy:
    """
    The splittingPolicy object is used to determine if a given point in 2-dimensional space(xCoord, yCoord) is within a radial area measured from the center (0,0).
    An openingDegree and a closingDegree parameter split the 2-dimensional space clockwise in a radial area, a so called splittingPolicy.
    If a given point is within this area then this point is a feasible point for this splittingPolicy.

    I.e. for openingDegree = 10 and closingDegree = 160, every point that is in the radial area between 10 and 160 degrees 
    measured from the center point (0,0) is a feasible point. 

    An optional excludePolicy parameter defines another radial area which might overlap with the previous area: at those overlaps
    a point is NOT feasible (the point is excluded, hence the name). 
    """
    def __init__(self, openingDegree: float, closingDegree: float, excludePolicy = None):
        if openingDegree == closingDegree:
            raise ValueError("openingDegree needs to be different from closing degree.")
        self.openingDegree = openingDegree
        self.closingDegree = closingDegree
        self.excludePolicy: splittingPolicy = excludePolicy

    def checkIfNodeFulfillsPolicy(self, xCoord, yCoord, xCenter, yCenter):
        """
        
        """
        xCoord -= xCenter
        yCoord -= yCenter 
        fulfill = False
        
        if xCoord == 0 and yCoord == 0:
            fulfill = True
            return fulfill
        

        # Determine bearing of given coordinates:
        if xCoord > 0 and yCoord > 0:
            alpha = arctan(xCoord/yCoord)
            bearing = alpha
        elif xCoord > 0 and yCoord < 0:
            alpha = arctan(xCoord/yCoord)
            bearing = 180 - alpha
        elif xCoord < 0 and yCoord < 0:
            alpha = arctan(xCoord/yCoord)
            bearing = 180 + alpha
        elif xCoord < 0 and yCoord > 0:
            alpha = arctan(xCoord/yCoord)
            bearing = 360 - alpha
        elif xCoord == 0: 
            if yCoord > 0:
                bearing = 0
            elif yCoord < 0:
                bearing = 180
        elif yCoord == 0:
            if xCoord > 0:
                bearing = 90
            elif xCoord < 0:
                bearing = 270
        else:
            raise ValueError("You forgot something.")

        # Determine if bearing is in radial area
        if self.openingDegree > self.closingDegree:
            if bearing >= self.openingDegree or bearing <= self.closingDegree:
                fulfill = True
        else:
            if bearing >= self.openingDegree and bearing <= self.closingDegree:
                fulfill = True

        # Check if point is in excludePolicy
        if self.excludePolicy != None:
            fulfill = not self.excludePolicy.checkIfNodeFulfillsPolicy(xCoord,yCoord, xCenter, yCenter)

        return fulfill



def createSplittingPolicies():
    splittingPolicies: List[splittingPolicy] = list()
    params = [
        # 1- 16
        region(270,0,90),
        region(270,45,90),
        region(270,22.5,90),
        region(270,67.5,90),
        # 17 - 32
        region(225,0,90),
        region(225,45,90),
        region(225,22.5,90),
        region(225,67.5,90),
        # 33 - 48
        region(180,0,90),
        region(180,45,90),
        region(180,22.5,90),
        region(180,67.5,90),
        # 49 - 56
        [(*region(270,0,270)[iIndex],splittingPolicy(*region(90,90,90)[iIndex])) for iIndex in range(len(region(270,0,270)))],
        [(*region(270,45,270)[iIndex],splittingPolicy(*region(90,135,90)[iIndex])) for iIndex in range(len(region(270,45,270)))],
        [(*region(270,22.5,270)[iIndex],splittingPolicy(*region(90,112.5,90)[iIndex])) for iIndex in range(len(region(270,22.5,270)))],
        [(*region(270,67.5,270)[iIndex],splittingPolicy(*region(90,157.5,90)[iIndex])) for iIndex in range(len(region(270,67.5,270)))]
    ]
    params = [j for i in params for j in i]
    for p in params:
        splittingPolicies.append(splittingPolicy(*p))
    
    return splittingPolicies

def region(spread: int, offset: int, rotateBy: int):
    """
    Returns a List of Tuple(~region) containing startDegree and stopDegree, spanning a radial area.
    :param spread: degrees to be covered from start to stop ~ size of the radial
    :param offset: degrees by which the first region is offset from 0°
    :param rotateBy: degrees by which the region gets rotated (360/rotateBy ~ num of regions created)
    """
    region: List[(int,int)] = list()
    rotated = 0
    while rotated < 360:
        start = offset + rotated
        if start > 360: start -= 360 
        stop = start + spread
        if stop > 360: stop -= 360
        region.append((start,stop))
        rotated += rotateBy
    return region