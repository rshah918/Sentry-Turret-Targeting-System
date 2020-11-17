#include <Servo.h>
int incomingByte;
Servo servo1;  // create servo object to control a servo
Servo servo2;
int pan = 90;
int tilt = 90;

int tiltMin = 45;
int tiltMax = 140;

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("-------------------------");
  Serial.println("ARos is loading....");
  delay(1000);
  Serial.println("ARos loaded succesfully");
  Serial.println("-------------------------");
  pinMode(6, OUTPUT);
  servo1.attach(4);  // attaches the servo on pin 9 to the servo object
  servo2.attach(9);
}

void loop() {

    incomingByte = Serial.read();
    if(incomingByte == 'x'){
      pan = Serial.parseInt();
      servo1.write(pan);
    }
    if(incomingByte == 'y'){
      tilt = Serial.parseInt();
      tilt = constrain(tilt,tiltMin,tiltMax);
      servo2.write(tilt);
    }
    if(incomingByte == 'l'){
      int mode = Serial.parseInt();
      if(mode == 0){
        digitalWrite(6, LOW);
      }
      else{
        digitalWrite(6, HIGH);
      }
      
    }
        
}
