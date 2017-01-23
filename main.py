from ImageProcess import Frame
from time import sleep
from BluetoothController import BluetoothController
from Checkpoint import CheckpointType, Checkpoint
from Area import Area
from Point import Point
import math
from BotController import Bot
import cv2
from AStar import *
#from FindDirectionality import Direction, Orientation,MovementFunctions


#connect Bluetooth
BluetoothController.connect()
Bot.Stop()
Bot.setBotSpeed(100)

Frame.connect(1)
Bot.resource = CheckpointType("Resource", "yellow",(0,255,255))
#Bot.obstacle = CheckpointType("Obstacle", "purple",(255,0,0))
Bot.botFront = CheckpointType('botFront', 'green',(0,255,0))
Bot.botBack = CheckpointType('botBack', 'red',(0,0,255))
# while True:
#     Frame.capture_frame()
#     Frame.show_frame()
#     k = cv2.waitKey(1) &0xFF
#     if k == 27:
#         break

#while True:

Frame.townHall = Checkpoint(0,Point(0,0),0,0,0)
#Frame.capture_frame()
#resource_checkPoints = Frame.processStream(Bot.resource)
#initially find center of townhall by finding bot center
Bot.UpdateProperties()

#save value to townHallPosition
#Bot.townHall = Checkpoint(0,Bot.position,0,0,0,0)
#Frame.townHall = Checkpoint(0,Bot.position,0,0,0,0)

resource_checkPoints = Frame.processStream(Bot.resource)

#obstacle_checkPoints = Frame.processStream(Bot.obstacle)
#cv2.imshow("init",Frame.resized)
#AStar.calculate(resource_checkPoints,obstacle_checkPoints)
Bot.currentTarget = Checkpoint(0, Point(0, 0), 0, 0, 0)

Bot.Traverse(resource_checkPoints )