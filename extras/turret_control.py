import serial
import pyautogui as gui
import time
import math
import numpy as np
import cv2
from imutils.video import VideoStream
import imutils

#cap = cv2.VideoCapture(0)
cap = VideoStream(usePiCamera=True).start()
time.sleep(2.0)
#premade face detection CNN
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
scale = .7
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())#('hogcascade_pedestrians.xml')

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
    #value = input("enter the positions in the form x#y#")
    #pan = 180*(mx/screenX)
    #tilt = 180*(my/screenY)
    
    # send the angle over serial
    
    # writes the pan angle then the tilt angle
    #print("pan, tilt: ",pan,", ",tilt)
    #write something over serial
    #time.sleep(.2)
    #ser.write(value.encode('ascii'))
    #use builtin webcam with realtime face detection


    # Capture frame-by-frame
    frame = cap.read()
    if frame is None:
        print("frame error")
        break
    #greyscale the image
    #frame = cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
    w = frame.shape[1]
    h = frame.shape[0]
    gray = frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray,(int(w*scale),int(h*scale)))
    #forward pass greyscale image into body classifier
    '''
    bodies = hog.detectMultiScale(gray)
    #draw bounding box
    for(x,y,w,h) in bodies[0]:
        oX = int(x/scale)
        oY = int(y/scale)
        oW = int(w/scale)
        oH = int(h/scale)
        img = cv2.rectangle(frame, (oX,oY), (oX+oW, oY+oH), (255,0,0), 2)
        #img = cv2.rectangle(gray, (x,y), (x+w, y+h), (255,0,0), 2)
        #body_gray = gray[y:y+h, x:x+w]
    #forward pass greyscale image into face classifier
    '''
    faces = face_cascade.detectMultiScale(gray, 1.1, 3)
    #draw bounding box
    for(x,y,w,h) in faces:
        #print ("face bb: ", x,y)
        oX = int(x/scale)
        oY = int(y/scale)
        oW = int(w/scale)
        oH = int(h/scale)
        img = cv2.rectangle(frame, (oX,oY), (oX+oW, oY+oH), (255,0,0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        #pass face bounding box into eye detector if face is detected
        '''
        if len(faces) > 0:
            eyes = eye_cascade.detectMultiScale(roi_gray, minSize = (int(w/20),int(h/20)), maxSize=(int(w/6),int(h/6)), minNeighbors=5)
            for(x2,y2,w2,h2) in eyes[0:((len(faces))*2)]:
                img2 = cv2.rectangle(roi_color, (x2,y2), (x2+w2, y2+h2), (0,255,0), 2)
        '''
    if len(faces) > 0:
        bbX,bbY,bbW,bbH = faces[0]/scale
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        x_delta = ((bbX + (bbW/2))/(frame_width/2))
        y_delta = ((bbY + (bbH/2))/(frame_height/2))
        angle_delta_x = x_delta/(2*math.tan(30))
        angle_delta_y = y_delta/(2*math.tan(30))
        if (bbX+bbW/2) > (frame_width/2):
            pan = pan + 15*angle_delta_x
        elif (bbX+bbW/2) < (frame_width/2):
            pan = pan - 15*angle_delta_x
        if (bbY+bbH/2) > (frame_height/2):
            tilt = tilt - 15*angle_delta_y
        elif (bbY+bbH/2) < (frame_height/2):
            tilt = tilt + 15*angle_delta_y
    #else:
        #pan= pan + (math.sin(time.time()))
        #tilt = tilt+(((y + (h/2))/scale)/(frame.shape[0]/2))
            
    if arduino_connected:
        ser.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))
# Display the resulting frame
    #cv2.imshow('grey', gray)
    cv2.imshow('frame', frame)
    #cv2.imshow('body', body_gray)
    if cv2.waitKey(1) & 0xFF == ord('q'): #kill with q key
        break

# When everything done, release the capture
#cap.release()
cv2.destroyAllWindows()
