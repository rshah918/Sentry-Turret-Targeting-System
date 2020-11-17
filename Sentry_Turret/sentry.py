# this is the main control script
import turret_controller
import numpy as np
import random
import time
import NN.inference
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import cv2
#setup the turret controller
class Sentry():
    def __init__(self):
        self.setup()
    def setup(self):
        self.turret = turret_controller.TurretController()
        self.turret.send_angles(90,90)
        self.nn = NN.inference.InferenceTPU()
        self.cap = cv2.VideoCapture(0)
    def select_target(self,pixel_deltas=[]):
        '''Calculate the Euclidean Distance between the image center and each detected human.
        Selects the closest human to the center of the frame as the target'''
        selected_target = []
        if(len(pixel_deltas) > 0):
            largest_target = 0
            min_distance = 999
            for target in pixel_deltas:
                deltaX = target[0]
                deltaY = target[1]
                targetWidth = target[2]
                targetHeight = target[2]
                targetSize = targetWidth*targetHeight
                euclideanDistance = math.sqrt((deltaX**2)+(deltaY**2))
                '''if euclideanDistance < min_distance:
                    selected_target = [deltaX, deltaY]'''
                if targetSize > largest_target:
                    largest_target = targetSize
                    selected_target = [deltaX, deltaY]
        return selected_target
    def start(self):
        while True:
            _,image = self.cap.read()
	        # show the frame
            deltas,image = self.nn.run_inference(image)
            #print(deltas)
            targetDelta = self.select_target(deltas)
            
            if(len(targetDelta)>0):
                print(targetDelta)
                self.turret.send_angles_from_deltas(targetDelta[0],targetDelta[1])
            cv2.imshow("Frame", image)
            key = cv2.waitKey(1) & 0xFF
            #self.rawCapture.truncate(0)

sentry = Sentry()
sentry.start()
#setup the camera

#for each frame run inference
