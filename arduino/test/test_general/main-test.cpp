#include "include.h"

const int pin_PWM_Out = 3;

void setup() {
    pinMode(pin_PWM_Out, OUTPUT);
}

void loop() {
    analogWrite(pin_PWM_Out, 127);
    delay(1000);
    analogWrite(pin_PWM_Out, 255);
    delay(1000);
    analogWrite(pin_PWM_Out, 0);
}