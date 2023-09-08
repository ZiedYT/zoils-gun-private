const int motor1 = 27;
const int motor2 = 14;

void setup() {
  Serial.begin(115200);
  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);
  digitalWrite(motor1, HIGH);
  digitalWrite(motor2, HIGH);
  Serial.write("....");
}

void loop() {
  String command = Serial.readStringUntil('\n'); 
  if (command=="0"){
    digitalWrite(motor1, HIGH);
    digitalWrite(motor2, HIGH);
  }
  else if (command=="1"){
    digitalWrite(motor1, LOW);
  }
  else if (command=="2"){
    digitalWrite(motor2, LOW);
  }

  
  delay(10);
}
