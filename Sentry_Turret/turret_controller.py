import serial
import math
import random
# this is a class that is used to control the turret 
class TurretController:
    def __init__(self):
        self.arduino_connected = False
        #set initial angles to 90, which is centered 
        self.pan = 90
        self.tilt = 90
        self.serial = self.init_servos()
        self.send_angles(self.pan,self.tilt)
    def init_servos(self):
        try:
            ser = serial.Serial('/dev/ttyACM0',9600,timeout=1)
            self.arduino_connected = True
            print("servo controller connected on /dev/ttyACM0")
        except:
            try:
                ser = serial.Serial('/dev/ttyACM1',9600,timeout=1)
                self.arduino_connected = True
                print("servo controller connected on /dev/ttyACM1")
            except:
                self.arduino_connected = False
                print("could not find the servo controller")
        return ser

    def send_angles(self, pan, tilt):
        #update internal pan and tilt values
        self.pan = pan
        self.tilt = tilt
        #make sure that the serial connection exists
        if self.arduino_connected and self.serial is not None:
            self.serial.write(('x'+str(int(pan))+'y'+str(int(tilt))).encode('ascii'))
        else:
            print("the servos are not connected")
    def send_angles_from_deltas(self,deltaX,deltaY):
        #calculate the angles from pixel deltas
        sensitivityX =0.1
        sensitivityY =0.1
        angle_delta_x = sensitivityX*abs(deltaX/(2*math.tan(30)))
        angle_delta_y = sensitivityY*abs(deltaY/(2*math.tan(30)))
        pan = self.pan
        tilt = self.tilt
        if(deltaX >0):
            pan = int(self.pan - angle_delta_x)
        elif(deltaX < 0):
            pan = int(self.pan + angle_delta_x)
        if(deltaY > 0):
            tilt = int(self.tilt - angle_delta_y)
        elif(deltaY < 0):
            tilt = int(self.tilt + angle_delta_y)
        print("pan: ",pan,"tilt: ",tilt,
             "anglePan",angle_delta_x, "angleTilt:", angle_delta_y)
        self.send_angles(pan,tilt)
    def random_motion(self):
        pan = random.randint(0,180)
        tilt = random.randint(30,130)
        self.send_angles(pan,tilt)