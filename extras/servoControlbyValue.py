import serial
import pyautogui as gui
import time
import numpy as np
import cv2

ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
ser.flush()
screenX, screenY = gui.size()
mx,my = gui.position()

while True:
    mx,my = gui.position()
    value = input("enter the positions in the form x#y#")
    pan = 180*(mx/screenX)
    tilt = 180*(my/screenY)
    
    # send the angle over serial
    
    # writes the pan angle then the tilt angle
    #print("pan, tilt: ",pan,", ",tilt)
    #write something over serial
    #time.sleep(.2)
    #ser.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))
    ser.write(value.encode('ascii'))

