#ifndef SERIAL_CTRL
#define SERIAL_CTRL

#include "Arduino.h"  // doesn't need pch.h as no external vars/functions

void serialInit();
void serialRead();  // read serial
extern uint8_t target_Id; 
extern uint8_t target_Led_Pwm; 
extern uint8_t target_Dir;
extern uint8_t target_Speed;
extern const int LED_PIN;

#endif