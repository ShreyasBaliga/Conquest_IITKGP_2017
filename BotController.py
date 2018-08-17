import copy
import timeit
from time import sleep, time
import cv2
import FindDirectionality
from AStar import AStar
from BluetoothController import BluetoothController
from Checkpoint import Checkpoint, CheckpointShape, CheckpointType
from Config import Config
from Draw import Draw
from FindDirectionality import Direction, MovementFunctions, Orientation
from ImageProcess import Frame
from Point import Point
from Utils import Utils


class Bot(object):

    position = Point(0, 0)
    angle = 0
    botFront = None  #CheckpointType('botFront', 'green',(0,255,0))
    botBack = None  #CheckpointType('botBack', 'red',(0,0,255))
    resource = None  #Checkpoint object
    prevBack = None  #Checkpoint object
    prevFront = None  #Checkpoint object
    currentTarget = None  #Checkpoint object
    currentResource = None  #Checkpoint object
    currentNode = None  #Checkpoint object
    townHall = None  #Checkpoint object
    runOnce = True
    optimizedAStarPath = None
    currentSpeed = 0
    currentCommand = ''

    @staticmethod
    def UpdateProperties():
        '''
        param-None
        returns-Bot.position[Type-str], Bot.angle[Type-int]
        This function is used loads of times.
        If not run before, it initializes the bot's position as the townhall.
        Otherwise, it gives back the position of the bot at every instant when it's running.
        It also does  little bit of image processing in the function botImageProperties() where it shows
        the bot process speed and the time elapsed.
        But mainly, it gives the bot's position and angle.
        '''
        Config.startTime = int(timeit.default_timer() * 1000)
        Frame.capture_frame()

        backCheckPointList = Frame.processStream(Bot.botBack)
        frontCheckPointList = Frame.processStream(Bot.botFront)

        #print str(Frame.isItMyFirstTime)

        #print "BOT Contours " + str(len(backCheckPointList))  + " , " + str(len(frontCheckPointList))
        if (len(backCheckPointList) <= 0 or len(frontCheckPointList) <= 0):
            print("Failed to Capture bot position !!! >>>>>>>>>>>>>> ")
            Bot.moveDirection(Direction.BACKWARD, False)
            #sleep(1)
            Bot.Stop()
        else:
            backCheckPoint = None
            frontCheckPoint = None
            if len(backCheckPointList) > 0 and len(frontCheckPointList) > 0:
                Bot.prevBack = backCheckPointList[0]
                Bot.prevFront = frontCheckPointList[0]
            Bot.position.x = (
                Bot.prevBack.center.x + Bot.prevFront.center.x) / 2
            Bot.position.y = (
                Bot.prevBack.center.y + Bot.prevFront.center.y) / 2
            Bot.angle, temp = Utils.angleBetweenPoints(Bot.prevBack.center,
                                                       Bot.prevFront.center)

            if Bot.runOnce:  #Frame.runTimeCounter == 6:
                Frame.townHall = Checkpoint(0, copy.deepcopy(Bot.position), 0,
                                            0, 0)
                Bot.runOnce = False
                Frame.runOnce = False
            else:
                #resource_checkPoints = Frame.processStream(Bot.resource)
                #obstacles_checkPoints = Frame.processStream(Bot.obstacle)

                Frame.botImageProperties(Bot.currentResource, Bot.currentNode,
                                         Bot.currentTarget, Bot.prevBack,
                                         Bot.prevFront, Bot.position)
                if Bot.optimizedAStarPath != None:
                    Draw.path(Bot.optimizedAStarPath)

            #print "Townhall center is:" + str(Frame.townHall.center.toString())
            Frame.drawCircle(Bot.position, (0, 255, 0))
            '''gives the bot angle'''
            cv2.putText(Frame.resized, "           BOT @" +
                        Bot.position.toString() + " | A: " + str(Bot.angle),
                        Bot.position.get_coordinate(),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        tempTime = Config.endTime = int(timeit.default_timer() * 1000)
        '''show time'''
        cv2.putText(
            Frame.resized,
            "Processing Time : " + str(Config.endTime - Config.startTime),
            (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(Frame.resized,
                    "Time Elapsed  : " + str(Config.endTime / 1000), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        Frame.show_frame()
        Config.endTime = int(timeit.default_timer() * 1000)
        #print "Per frame : " + str((Config.endTime - Config.startTime)) + " | Time elapsed : " + str(Config.endTime/1000)
        return Bot.position, Bot.angle

    @staticmethod
    def Stop():
        BluetoothController.send_command("s")

    @staticmethod
    def Blink():
        BluetoothController.send_command("k")

    @staticmethod
    def moveDirection(direction, updateProperties=True):
        '''
        param-direction [Type-str] - pass direction of the bot, updateProperties [Type-bool, default = True]
        returns-None
        Also, if the bot is not in the camera range, the updateProperties parameter is False so that the position is not 
        updated again. Based on the direction that the bot had to run, it sends the command to move in that direction. Usually forward
        or any other direction
        '''
        #Bot.setBotSpeed(Config.moveSpeed)

        if direction == Direction.FORWARD:
            BluetoothController.send_command(Direction.command[direction],
                                             "Forward : ^^^^^^^^^^^^^^^^^ ")
        else:
            BluetoothController.send_command(Direction.command[direction],
                                             "direction: " + direction)
        if updateProperties == True:
            Bot.UpdateProperties()

    @staticmethod
    def changeOrientation(orientation):
        '''
        param-orientation[Type-str]
        returns-None
        Based on the orientation, it sends the command to move in that direction.
        '''
        #Bot.setBotSpeed(Config.turnSpeed)
        if orientation == Orientation.SPOT_LEFT:
            BluetoothController.send_command(Orientation.command[orientation],
                                             "Left    : <<<<<<<<<<<<<<<<<")
        elif orientation == Orientation.SPOT_RIGHT:
            BluetoothController.send_command(Orientation.command[orientation],
                                             "Right   : >>>>>>>>>>>>>>>>>")
        else:
            BluetoothController.send_command(Orientation.command[orientation],
                                             "orientation: " + orientation)
        Bot.UpdateProperties()

    @staticmethod
    def Traverse(ListOfResources, ListOfObstacles=None):
        '''
        param-ListOfResources [Type-Checkpoint], ListOfObstacles [Type-Checkpoint, default = None]
        returns-None
        It takes in the list of all the resources and the obstacles if any
        It does a little bit of image processing i.e. printing the townhall center
        It checks each target in the list of resources. Also, if the bot is in the angle window and in the range of the resource,
        it moves forward. If it is not in the angle window, it turns till it gets to tht angle window. Then it keeps moving forward
        till it reaches the resource. If it is in the resource range, it stops and blinks an LED. The LED blink is initialized here.
        '''
        print "Townhall center is:" + str(Frame.townHall.center.toString())
        for target in ListOfResources:
            Bot.currentTarget = target
            Bot.currentResource = target
            print " | Target Angle: " + str(Bot.currentTarget.angle)
            Bot.UpdateProperties()
            blinkFlag = 0
            '''find list of PathPoints to traverse'''
            # path = Utils.generatePath(Bot.position, Bot.currentTarget.center)
            tempCounter = 0
            if target.path != None:
                for node in target.path:

                    Bot.currentNode = node
                    angle, dist = Utils.angleBetweenPoints(Bot.position, node)
                    Bot.currentTarget = Checkpoint(0, node, 0, angle, None)

                    firstAdjustLoop = False
                    '''if the bot is in the 25X25 area range, then the the funtion returns True'''
                    if Point.inRange(Bot.position, node):
                        print 'Reached Destination  <<<<<<<<<<<<<<<< '
                        Bot.Stop()
                        if (blinkFlag % target.noOfSkips
                            ) == (target.noOfSkips - 1) & blinkFlag == 1:
                            sleep(0.1)
                            Bot.changeOrientation(Orientation.SPOT_LEFT)
                            print 'BLINKING LED !!!!!!!!!!!!!! '
                            sleep(0.1)
                            Bot.Blink()
                            #sleep(4.6)
                            firstAdjustLoop = True

                    else:
                        while not Point.inRange(Bot.position, node):
                            if firstAdjustLoop != True:
                                Bot.currentTarget.angle, distance = Utils.angleBetweenPoints(
                                    Bot.position, Bot.currentTarget.center)
                                if (distance > Config.reduceSpeedAt):
                                    Bot.setBotSpeed(Config.moveSpeed)
                                else:
                                    Bot.setBotSpeed(
                                        Utils.map(distance, 0,
                                                  Config.reduceSpeedAt, 150,
                                                  Config.moveSpeedNear))
                                Bot.moveDirection(Direction.FORWARD)
                                firstAdjustLoop = False
                            tempCounter += 1
                            #print "Distance from center is:" + str(Utils.distance(Bot.position,target.center))
                            while Bot.angle <= (
                                    Bot.currentTarget.angle -
                                    Config.targetAngleRange
                            ) or Bot.angle >= (
                                    Bot.currentTarget.angle +
                                    Config.targetAngleRange
                            ):  ##while the bot angle is in the angle window
                                #print " " , (Bot.currentTarget.angle - Config.targetAngelRange) % 360, Bot.angle,  (Bot.currentTarget.angle + Config.targetAngelRange) % 360
                                if Point.inRange(Bot.position, node):
                                    Bot.Stop()
                                    break

                                orientation, speed = Utils.determineTurn(
                                    Bot.angle, Bot.currentTarget.angle,
                                    Utils.distance(Bot.position,
                                                   Bot.currentTarget.center))
                                Bot.setBotSpeed(speed)
                                Bot.changeOrientation(orientation)
                                '''update bot's angle with respect to target'''
                                Bot.currentTarget.angle, dist = Utils.angleBetweenPoints(
                                    Bot.position, Bot.currentTarget.center)
                    '''found the target'''
                    print 'Reached Destination  >>>>>>>>>> '
                    Bot.Stop()
                    if target.noOfSkips == 1 or (blinkFlag % target.noOfSkips
                                                 ) == target.noOfSkips - 1:
                        sleep(0.1)
                        Bot.changeOrientation(Orientation.SPOT_LEFT)
                        print 'BLINKING LED !!!!!!!!!!!!!! '
                        sleep(0.1)
                        Bot.Blink()

                        # >>>>>>> Value changes for 200 RPM
                        sleep(1)
        print "REACHED ALL DESTINATIONS!!!!!!!!!!!!!!!!!"
        Bot.Stop()
        #sleep(100)
        '''its time to stop the first traverse'''

    @staticmethod
    def setBotSpeed(speed):
        '''if current speed is different than previous speed, set speed'''

        if speed != Bot.currentSpeed and speed in range(0, 256):
            BluetoothController.send_command("X" + str(speed) + "$")
            Bot.currentSpeed = speed


if __name__ == '__main__':
    botFront_green = CheckpointType('botFront', 'green', (0, 255, 0))
    botBack_red = CheckpointType('botBack', 'red', (0, 0, 255))
    resourceList = []
    resourceList.append(Checkpoint(0, Point(275, 0), 0, 0, 0))
    Bot.UpdateProperties()
    townhall = Checkpoint(0, Bot.position, 0, 0, 0, 0)
    BluetoothController.connect()
    Bot.Traverse(resourceList, townhall)