#include "headers/pch.h"

void setup() {
    motorsInit();
    encodersInit();
    Serial.begin(115200);
}

void loop() {
    motor0Move(127); // left motor, forwards, half speed
    motor1Move(0, 127);  // right motor, backwards, half speed
}