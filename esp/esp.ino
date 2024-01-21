#include <Servo.h>
Servo ESC;
const int motor1 = 27;
const int motor2 = 14;
const int escPin = 12;

void setup() {
  Serial.begin(115200);
  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);
  digitalWrite(motor1, HIGH);
  digitalWrite(motor2, HIGH);
  ESC.attach(escPin,1000,2000)
  Serial.write("....");
}

void loop() {
  String command = Serial.readStringUntil('\n'); 
  if (command=="0"){
    digitalWrite(motor1, HIGH);
    digitalWrite(motor2, HIGH);
    ESC.write(0);
  }
  else if (command=="1"){
    digitalWrite(motor1, LOW);
    ESC.write(180);
  }
  else if (command=="2"){
    digitalWrite(motor2, LOW);
    ESC.write(180);
  }

  
  delay(10);
}
