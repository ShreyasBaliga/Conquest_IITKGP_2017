##Open to everyone
##Any person who creates a helper function can place it here
##After adding a function please menrion it in the intital comments
##Contains-
##  Angle for marker()
##  distance formula()

from math import *
import numpy as np
from Point import Point
import copy
from FindDirectionality import *
class Utils(object):

    @staticmethod
    def angleBetweenPoints(origin,position):
        
        deltaY = position.y - origin.y
        deltaX = position.x - origin.x
        angleInDegrees = round(atan2(deltaY, deltaX) * float(180) / 3.14)
        if angleInDegrees < 0: 
            #angle is in I and II Quad, ie between 0 to -180, so map it to 0,180
            angleInDegrees = Utils.map(angleInDegrees,0,-180,0,180)
        else:
            #angle is in III and IV Quad, ie between 0 to -180, so map it to 360,180
            angleInDegrees = Utils.map(angleInDegrees,0,180,360,180)
        return angleInDegrees, Utils.distance(origin, position)

    @staticmethod
    def distance(pt1,pt2):
        dist = round(sqrt(((pt1.x-pt2.x)*(pt1.x-pt2.x))+((pt1.y-pt2.y)*(pt1.y-pt2.y))))
        return dist
    @staticmethod
    def map(value, in_min, in_max, out_min, out_max):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def midPoint(point1,point2):
        return Point((point1.x + point2.x)/2,(point1.y + point2.y)/2)
    @staticmethod
    def getQuadrant(angle):
        if angle in range(0, 91): return 1
        if angle in range(91, 181): return 2
        if angle in range(181, 271): return 3
        if angle in range(271, 360): return 4    

    @staticmethod
    def getPointFromAngle(p1,p2):
        x=(101*p2.x)-(p1.x*100)
        y=(101*p2.y)-(p1.y*100)
        return (x,y)

    @staticmethod
    def determineTurn(botAngle, targetAngle,distance): #TODO fix it !
        deltaAngle = botAngle - targetAngle
        # find positive/negative of angle
        deltaAngleDirection = None
        if deltaAngle < 0 :
            deltaAngleDirection = False
        else:
            deltaAngleDirection = True
        if deltaAngle >= 180:
            deltaAngle -= 360
        deltaAngle %= 360
        absDeltaAngle = abs(deltaAngle)

        mappedAngle = absDeltaAngle /2 #round(Utils.map(absDeltaAngle,0,360,0,15))
        #print " angle " + str(deltaAngle) + " distance " + str(distance) + " mappedAngle " + str(mappedAngle) + " absDeltaAngle " + str(absDeltaAngle)
        
        if deltaAngle >= 180:
            #if absDeltaAngle >= 240:
            #    return Orientation.SPOT_LEFT, mappedAngle, deltaAngleDirection
            #el
            if absDeltaAngle > mappedAngle:# and distance > 180:
                return Orientation.SPOT_LEFT, mappedAngle, deltaAngleDirection
            else:
                return Orientation.SPOT_LEFT, mappedAngle, deltaAngleDirection
        else:
            #if absDeltaAngle >= 60:
            #    return Orientation.SPOT_RIGHT, mappedAngle, deltaAngleDirection
            #el
            if absDeltaAngle > mappedAngle:#  and distance > 180:
                return Orientation.SPOT_LEFT, mappedAngle, deltaAngleDirection
            else:
                return Orientation.SPOT_RIGHT, mappedAngle, deltaAngleDirection
        
    @staticmethod
    def generatePath(botPosition, targetPosition, aStarPath=None):
        finalPath = []

        #path for FirstPast
        firstPass = []
        pathToTarget = []
        pathToTarget.append(botPosition) #botPosition
        if aStarPath != None:
            pathToTarget += copy.deepcopy(aStarPath)
        pathToTarget.append(targetPosition) #target Position
        noOfSkips = len(pathToTarget) - 1
        firstPass += copy.deepcopy(pathToTarget) #from bot postion to target
        #delete target from reversed pathToTarget
        del pathToTarget[len(pathToTarget) - 1]
        pathToTarget.reverse()
        firstPass += copy.deepcopy(pathToTarget)

        finalPath += copy.deepcopy(firstPass)       
        del firstPass[0]
        finalPath += copy.deepcopy(firstPass)

        del finalPath[0]
        return finalPath, noOfSkips
    
    
if __name__ == '__main__':

    turn = Utils.determineTurn3(180, 0)    
    print turn


'''
    @staticmethod
    def angleBetweenPoints(origin,position):
        # adj=float((((p1.x-p2.x)*(p1.x-p2.x))+((p1.y-p1.y)*(p1.y-p1.y)))^(1/2))
        # print adj
        # hyp=float((((p1.x-p2.x)*(p1.x-p2.x))+((p1.y-p2.y)*(p1.y-p2.y)))^(1/2))
        # print hyp
        # cos=float(adj/hyp)
        # print cos
        # angle = math.acos(float(cos))
        # ang=round(math.degrees(angle),2)
        dist2 = math.sqrt(float(abs((origin.y - position.y )*(origin.y - position.y ))))
        dist = math.sqrt(float(abs(((origin.x - position.x)*(origin.x - position.x))+((origin.y - position.y )*(origin.x - position.y)))))
        sinn = float(dist2/dist)
        
        if sinn > 1:
            sinn = 1
        if sinn < 0:
            sinn = 0        angle = math.asin(float(sinn))
        angle = round(math.degrees(angle), 2)
        if position.x > origin.x and position.y > origin.y:
            angle = 270 + angle
        elif position.x < origin.x and position.y > origin.y:
            angle = 270 - angle
        elif position.x < origin.x and position.y < origin.y:
            angle = angle + 90
        elif origin.x < position.x and origin.y > position.y:
            angle = 90 - angle
        return angle,dist
'''
