#ifndef MOTOR_CONTROL  
#define MOTOR_CONTROL  

void motorsInit();
void encodersInit();
void encoder0Raw();
void encoder1Raw();
void motorsSpeedDistance();
void moveMotor1(bool direction, int speed);
void moveMotor2(bool direction, int speed);
bool motorsKill();

#endif