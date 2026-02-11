#ifndef MOTOR_CONTROL  
#define MOTOR_CONTROL  

void motorsInit();
void encodersInit();
void encoder0Raw();
void encoder1Raw();
void motorsSpeedDistance();
void motor0Move(bool direction = 1, int speed);
void motor1Move(bool direction = 1, int speed);
bool motorsKill();

#endif