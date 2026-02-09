#include "Arduino.h"

/* TODO:
 - Double check the MOTOR_CPR value - 16 or 64?
 - Add simple autonomous functions ie 'forward(distance, speed)'
 - 
*/

// --- Declarations --- //

// pins to motor driver board
const int MOTOR_0_DIR = 1;
const int MOTOR_0_PWM = 2;
const int MOTOR_1_DIR = 3;
const int MOTOR_1_PWM = 4;

// pins to motor encoders
// encoder counts are more reliable when pins are interrupt capable
const int MOTOR_0_ENCA = 5;
const int MOTOR_0_ENCB = 6;
const int MOTOR_1_ENCA = 7;
const int MOTOR_1_ENCB = 8;

// store previous encoder channel for comparison
byte motor0_EncA_Last;
byte motor0_EncB_Last;
byte motor1_EncA_Last;
byte motor1_EncB_Last;

// motor rpm calculation values
const int MOTOR_CPR = 16;
float motor0_RPM = 0;
float motor1_RPM = 0;

volatile int motor0_Duration;  // the number of the pulses
volatile int motor1_Duration;

volatile bool motor0_Direction;  // the rotation direction
volatile bool motor1_Direction;

unsigned long motors_Last_Time;  // last time motor rpm was checked

inline void motorsInit() {
    pinMode(MOTOR_0_DIR, OUTPUT);
    pinMode(MOTOR_0_PWM, OUTPUT);
    pinMode(MOTOR_1_DIR, OUTPUT);
    pinMode(MOTOR_1_PWM, OUTPUT);
}

inline void encodersInit() {
    bool direction = true; //default -> Forward
    pinMode(MOTOR_0_ENCB,INPUT);  
    attachInterrupt(digitalPinToInterrupt(MOTOR_0_ENCA), encoder0Raw, CHANGE);
    pinMode(MOTOR_1_ENCB,INPUT);
    attachInterrupt(digitalPinToInterrupt(MOTOR_1_ENCA), encoder1Raw, CHANGE);
}

void encoder0Raw() {
    int encA_State = digitalRead(MOTOR_0_ENCA);  // current 'A' value
    int encB_State = digitalRead(MOTOR_0_ENCB);  // current 'B' value

    if((motor0_EncA_Last != encA_State) || (motor0_EncB_Last != encB_State)) {  // has signal changed?
        if(motor0_EncA_Last == encA_State) {  // if 'A' is the same...
            motor0_Direction = (encB_State == HIGH) ? true : false;  // ...then 'B' must have changed, so direction based off of 'B'...
        } else {
            motor0_Direction = (encA_State == encB_State) ? true : false;  // else direction based off of 'A' relative to 'B'
        }
    }

    motor0_Duration = (!motor0_Direction) ? motor0_Duration++ : motor0_Duration--; // incrementing pulse counter

    motor0_EncA_Last = encA_State;
    motor0_EncB_Last = encB_State; 
}

void encoder1Raw() {
    int encA_State = digitalRead(MOTOR_1_ENCA);  // current 'A' value
    int encB_State = digitalRead(MOTOR_1_ENCB);  // current 'B' value

    if((motor1_EncA_Last != encA_State) || (motor1_EncB_Last != encB_State)) {  // has signal changed?
        if(motor1_EncA_Last == encA_State) {  // if 'A' is the same...
            motor1_Direction = (encB_State == HIGH) ? true : false;  // ...then 'B' must have changed, so direction based off of 'B'...
        } else {
            motor1_Direction = (encA_State == encB_State) ? true : false;  // else direction based off of 'A' relative to 'B'
        }
        motor1_Duration = (!motor1_Direction) ? ++motor1_Duration : --motor1_Duration; // incrementing pulse counter
    }

    motor1_EncA_Last = encA_State;
    motor1_EncB_Last = encB_State;
}

int motorsRPM() {  // get raw motor values and convert to rpm
    encoder0Raw();
    encoder1Raw();

    unsigned long motors_Current_Time = millis();
    unsigned long motors_Elapsed_Time = motors_Current_Time - motors_Last_Time;
    
    if(motors_Elapsed_Time >= 100) {  // Calculate every >100ms
        float motor0_RPM = (motor0_Duration / MOTOR_CPR) / (motors_Elapsed_Time / 60000.0); // revolutions over time in mins
        float motor1_RPM = (motor1_Duration / MOTOR_CPR) / (motors_Elapsed_Time / 60000.0);
        
        motor0_Duration = 0;  // Reset counter and update time
        motor1_Duration = 0;
        motors_Last_Time = motors_Current_Time;
    }
}

void motor0Move(bool direction, int speed) {  // simple direction and speed controls
    digitalWrite(MOTOR_0_DIR, direction);
    digitalWrite(MOTOR_0_PWM, speed);
}

void motor1Move(bool direction, int speed) {
    digitalWrite(MOTOR_1_DIR, direction);
    digitalWrite(MOTOR_1_PWM, speed);
}