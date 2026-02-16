#include "headers/pch.h"

void setup() {
  motorsInit();
  encodersInit();
  serialInit();
  pinMode(LED_PIN, OUTPUT);  // onboard LED has no pwm
}

void loop() {
  serialRead();
  if(target_Id == 0x01) {
    analogWrite(LED_PIN, target_Led_Pwm);
  motor0Move(127); // left motor, forwards, half speed
  motor1Move(0, 127);  // right motor, backwards, half speed
}