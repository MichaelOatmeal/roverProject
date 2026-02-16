#include "Arduino.h"
#include "serial-control.h"

void setup() {
  serialInit();
  pinMode(LED_PIN, OUTPUT);  // onboard LED has no pwm
}

void loop() {
  serialRead();
  if(target_Id == 0x01) {
    analogWrite(LED_PIN, target_Led_Pwm);
  }
}