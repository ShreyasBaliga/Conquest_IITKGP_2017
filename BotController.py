##Assign to Shreyas
##This is to define the commands which are to be sent to the BluetoothController
##Example-define forward='f'
##Functionalities required-
##  move bot in 8 directions
##  bot stop
##  bot speed control
##  bot orientation (i.e. clock or aclock)
##  should contain the bot class with all it's properties
from Point import Point
from BluetoothController import BluetoothController
from ImageProcess import Frame
from Checkpoint import Checkpoint,CheckpointType
import FindDirectionality
from FindDirectionality import Direction, Orientation,MovementFunctions
import FindDirectionality
from Utils import  Utils
from time import sleep
import copy
import cv2
class Bot(object):
    AngleRange = 12
    position = Point(0, 0)
    angle = 0
    botFront = None#CheckpointType('botFront', 'green',(0,255,0))
    botBack = None #CheckpointType('botBack', 'red',(0,0,255))
    resource = None
    prevBack = None
    prevFront = None
    currentTarget = None
    currentNode = None
    townHall = None
    runOnce = True
    aStarPath = None
    @staticmethod
    def UpdateProperties():
        #assume that you are calling Akshay's Image proccesing function
        Frame.capture_frame()
        
        backCheckPointList = Frame.processStream(Bot.botBack)
        frontCheckPointList = Frame.processStream(Bot.botFront)
        
        #print str(Frame.isItMyFirstTime)

        #print "BOT Contours " + str(len(backCheckPointList))  + " , " + str(len(frontCheckPointList))
        if(len(backCheckPointList) <=0 or len(frontCheckPointList)  <= 0):
            print "Failed to Capture bot position !!! >>>>>>>>>>>>>> "
        else:
            backCheckPoint = None
            frontCheckPoint = None
            if len(backCheckPointList) > 0 and len(frontCheckPointList) > 0:
                Bot.prevBack = backCheckPointList[0]
                Bot.prevFront = frontCheckPointList[0]
            
            #print "Counter is:" + str(Frame.runTimeCounter)

            Bot.position.x = (Bot.prevBack.center.x + Bot.prevFront.center.x) / 2
            Bot.position.y = (Bot.prevBack.center.y + Bot.prevFront.center.y) / 2
            Bot.angle, temp = Utils.angleBetweenPoints(Bot.prevBack.center, Bot.prevFront.center)
            #print "Bot Position:" + Bot.position.toString() + " | Angle: " + str(Bot.angle)
            #sleep(1)
            #Frame.botPosition = 
            
            if Bot.runOnce:#Frame.runTimeCounter == 6:
                Frame.townHall = Checkpoint(0,copy.deepcopy(Bot.position),0,0,0)
                Bot.runOnce = False
                Frame.runOnce = False
            else:
                #TODO Move to ImageProess
                cv2.circle(Frame.resized,Bot.currentTarget.center.get_coordinate(),30,(255,150,0),2,8)
                #Frame.drawCircle(Bot.currentTarget.center,(255,0,0))
                if Bot.currentNode != None:
                    cv2.circle(Frame.resized,Bot.currentNode.get_coordinate(),20,(0,0,255),2,4)
                    #Frame.drawCircle(Bot.currentNode,(255,0,0))
                    cv2.putText(Frame.resized, "         Target @" + Bot.currentTarget.center.toString() + " | A: "  + str(Bot.currentTarget.angle) , Bot.currentTarget.center.get_coordinate(), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
                cv2.putText(Frame.resized, "   " + str(Utils.distance(Bot.position,Bot.currentTarget.center)), Utils.midPoint(Bot.position,Bot.currentTarget.center).get_coordinate(), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                if Bot.currentNode != None:
                    cv2.arrowedLine(Frame.resized,Bot.position.get_coordinate(), Bot.currentNode.get_coordinate(), (255,150,0), 2,0,0,0.1)#draws line from one point ti the other, last arg means thickness
                cv2.arrowedLine(Frame.resized,Bot.prevBack.center.get_coordinate(), Bot.prevFront.center.get_coordinate(), (255,255,255), 10,0,0,1)#draws line from one point ti the other, last arg means thickness
                #cv2.arrowedLine(Frame.resized,Point(Bot.prevBack.center)- 5000, ), Bot.prevFront.center.get_coordinate(), (255,255,255), 10,0,0,1)#draws line from one point ti the other, last arg means thickness
                cv2.arrowedLine(Frame.resized,Bot.prevBack.center.get_coordinate(),Utils.getPointFromAngle(Bot.prevBack.center, Bot.prevFront.center),(255,255,25), 1,0,0,1)
                Frame.drawCircle(Frame.townHall.center,(0,255,255))
                resource_checkPoints = Frame.processStream(Bot.resource)
             


            #print "Townhall center is:" + str(Frame.townHall.center.toString())
            Frame.drawCircle(Bot.position,(0,255,0))
            cv2.putText(Frame.resized, "           BOT @" +Bot.position.toString() + " | A: "  + str(Bot.angle) , Bot.position.get_coordinate(), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        Frame.show_frame()
        return Bot.position, Bot.angle

    @staticmethod
    def turnAntiClockwise():
        BluetoothController.send_command("ac")
    @staticmethod
    def turnClockwise():
        BluetoothController.send_command("c")
    @staticmethod
    def Stop():
        BluetoothController.send_command("s")
    @staticmethod
    def Blink():
        BluetoothController.send_command("blink")
    @staticmethod
    def moveDirection(direction):
        Bot.setBotSpeed(100)
        BluetoothController.send_command(Direction.command[direction])

        print "direction: " + direction
        #sleep(0.1)
        #Bot.Stop()
        Bot.UpdateProperties()
    @staticmethod
    def changeOrientation(orientation):
        Bot.setBotSpeed(100)
        BluetoothController.send_command(Orientation.command[orientation])

        print "orientation: " + orientation
        #sleep(0.1)

        Bot.UpdateProperties()
        #return Bot.position, Bot.angle    
    @staticmethod
    def Traverse(ListOfResources, ListOfObstacles = None):
        print "Townhall center is:" + str(Frame.townHall.center.toString())
        for target in ListOfResources:
            Bot.currentTarget = target
            print " | Target Angle: " + str(Bot.currentTarget.angle)
            Bot.UpdateProperties()
            #TODO call aStar algorithm
            #TODO take in a_star_search in generatePath function
            ''''if ListOfObstacles == None:
                path = Utils.generatePath(Bot.position, Bot.currentTarget.center)
            else:
                path = Utils.generatePath(Bot.position, Bot.currentTarget.center,a_star_search())'''
            #find list of PathPoints to traverse
            path = Utils.generatePath(Bot.position, Bot.currentTarget.center)

            for node in path:
                #print path
                Bot.currentNode = node
                angle, dist = Utils.angleBetweenPoints(Bot.position,node)
                Bot.currentTarget = Checkpoint(0,node,0,0,angle)
                # if Point.inRange(Bot.position, node):
                #     print 'Reached Destination  <<<<<<<<<<<<<<<< '
                #     # Bot.Stop()
                #     # Bot.Blink()
                #     BluetoothController.send_command(Orientation.SPOT_RIGHT)
                #     sleep(5)
                    
                # else:
                while not Point.inRange(Bot.position, node):
                    #print "Distance from center is:" + str(Utils.distance(Bot.position,target.center))
                    while Bot.angle <= (Bot.currentTarget.angle - Bot.AngleRange)%360 or Bot.angle >= (Bot.currentTarget.angle + Bot.AngleRange)%360:##receive red_point & green_point parameters
                        if Point.inRange(Bot.position, node):
                            Bot.Stop()
                            break
                        orientation = Utils.determineTurn3(Bot.angle, Bot.currentTarget.angle)
                        Bot.changeOrientation(orientation)
                    print "##############################################################################"
                    
                        
                    Bot.moveDirection(Direction.FORWARD)
                #Bot.Stop()
                # Bot.Blink()
                print 'Reached Destination  >>>>>>>>>> '
                BluetoothController.send_command(Orientation.SPOT_RIGHT)
                #print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
                # Bot.Stop()
                # sleep(5)
                
               
            #Bot.BackToTownhall(ListOfObstacles = None)
                            
                ##TODO wait for some time

    @staticmethod
    def setBotSpeed(speed):
        if speed in range(0,100):
            BluetoothController.send_command("X" + str(speed))



if __name__ == '__main__':
    botFront_green = CheckpointType('botFront', 'green',(0,255,0))
    botBack_red = CheckpointType('botBack', 'red',(0,0,255))
    resourceList = []
    resourceList.append(Checkpoint(0,Point(275,0),0,0,0))
    Bot.UpdateProperties()
    townhall=Checkpoint(0,Bot.position,0,0,0,0)
    BluetoothController.connect()
    Bot.Traverse(resourceList,townhall)
