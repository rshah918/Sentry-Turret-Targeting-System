import serial
import pyautogui as gui
import time
import math
import numpy as np
import cv2
from imutils.video import VideoStream
import imutils

#cap = cv2.VideoCapture(0)

#premade face detection CNN
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

arduino_connected = True

try:
    ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
except:
    arduino_connected = False
    print("could not fin the arduino")

#ser.flush()
screenX, screenY = gui.size()
mx,my = gui.position()
pan = 90
tilt = 90
if arduino_connected:
    ser.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))

while True:
    mx,my = gui.position()
    pan = 180*(mx/screenX)
    tilt = 180*(my/screenY)
    
    # send the angle over serial
    
    # writes the pan angle then the tilt angle
    print("pan, tilt: ",pan,", ",tilt)
    #write something over serial
    #time.sleep(.2)
    ser.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))

