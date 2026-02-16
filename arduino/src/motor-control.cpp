#include "Arduino.h"

/* TODO:
 - Double check the MOTOR_CPR value - 16 or 64?
 - Add simple autonomous functions ie 'forward(distance, speed)'
 - Test best value for CALC_RATE_MS
*/

// --- Declarations --- //

// pins to motor driver board (MDD10A)
const int MOTOR_0_DIR = 4; 
const int MOTOR_0_PWM = 5; 
const int MOTOR_1_DIR = 7; 
const int MOTOR_1_PWM = 6; 

// pins to motor encoders
// encoder counts are more reliable when pins are interrupt capable
const int MOTOR_0_ENCA = 8; 
const int MOTOR_0_ENCB = 2; 
const int MOTOR_1_ENCA = 9; 
const int MOTOR_1_ENCB = 3; 

// store previous encoder channel for comparison
byte motor0_EncA_Last;
byte motor0_EncB_Last;
byte motor1_EncA_Last;
byte motor1_EncB_Last;

// rpm & distance travelled calculation values
const int CALC_RATE_MS = 100;  // rate at which speeds and distance are calculated in ms
const int MOTOR_CPR = 16;
const int WHEEL_DIAM = 0.08;  // diameter in metres
const int WHEEL_CIRC = PI * WHEEL_DIAM; // circumference in metres
float motor0_RPM = 0;  // speed in revolutions per minute
float motor1_RPM = 0;
float motor0_MPS = 0;  // speed in metres per second
float motor1_MPS = 0;
float motor0_Distance = 0;  // cumulative distance travelled
float motor1_Distance = 0;

volatile int motor0_Duration;  // the number of the pulses counted
volatile int motor1_Duration;

volatile bool motor0_Direction;  // the rotation direction
volatile bool motor1_Direction;  

unsigned long motors_Last_Time;  // last time motor rpm was checked

// --- Functions --- //

void encoder0Raw() {  // convert encoders signals to counts and direction
    int encA_State = digitalRead(MOTOR_0_ENCA);  // current 'A' value
    int encB_State = digitalRead(MOTOR_0_ENCB);  // current 'B' value

    if((motor0_EncA_Last != encA_State) || (motor0_EncB_Last != encB_State)) {  // has signal changed?
        if(motor0_EncA_Last == encA_State) {  // if 'A' is the same...
            motor0_Direction = (encB_State == HIGH) ? true : false;  // ...then 'B' must have changed, so direction based off of 'B'...
        } else {
            motor0_Direction = (encA_State == encB_State) ? true : false;  // else direction based off of 'A' relative to 'B'
        }
        (!motor0_Direction) ? ++motor0_Duration : --motor0_Duration; // incrementing pulse counter

    }

    motor0_EncA_Last = encA_State;
    motor0_EncB_Last = encB_State; 
}

void encoder1Raw() {  // convert encoders signals to counts and direction
    int encA_State = digitalRead(MOTOR_1_ENCA);  // current 'A' value
    int encB_State = digitalRead(MOTOR_1_ENCB);  // current 'B' value

    if((motor1_EncA_Last != encA_State) || (motor1_EncB_Last != encB_State)) {  // has signal changed?
        if(motor1_EncA_Last == encA_State) {  // if 'A' is the same...
            motor1_Direction = (encB_State == HIGH) ? true : false;  // ...then 'B' must have changed, so direction based off of 'B'...
        } else {
            motor1_Direction = (encA_State == encB_State) ? true : false;  // else direction based off of 'A' relative to 'B'
        }
        (!motor1_Direction) ? ++motor1_Duration : --motor1_Duration; // incrementing pulse counter
    }

    motor1_EncA_Last = encA_State;
    motor1_EncB_Last = encB_State;
}

void motorsInit() {  // initialize motor pins
    pinMode(MOTOR_0_DIR, OUTPUT);
    pinMode(MOTOR_0_PWM, OUTPUT);
    pinMode(MOTOR_1_DIR, OUTPUT);
    pinMode(MOTOR_1_PWM, OUTPUT);
}

void encodersInit() {  // initialize encoder pins
    pinMode(MOTOR_0_ENCA, INPUT);
    attachInterrupt(digitalPinToInterrupt(MOTOR_0_ENCB), encoder0Raw, CHANGE);
    pinMode(MOTOR_1_ENCA, INPUT);
    attachInterrupt(digitalPinToInterrupt(MOTOR_1_ENCB), encoder1Raw, CHANGE);
}

void motorsSpeedDistance() {  // get raw motor values and convert to rpm/mps
    encoder0Raw();
    encoder1Raw();

    unsigned long motors_Current_Time = millis();
    unsigned long motors_Elapsed_Time = motors_Current_Time - motors_Last_Time;
    
    if(motors_Elapsed_Time >= CALC_RATE_MS) {  // Calculate every >100ms
        motor0_RPM = (motor0_Duration / MOTOR_CPR) / (motors_Elapsed_Time / 60000.0);
        motor1_RPM = (motor1_Duration / MOTOR_CPR) / (motors_Elapsed_Time / 60000.0);
        
        motor0_MPS = motor0_RPM * WHEEL_CIRC / 60;
        motor1_MPS = motor1_RPM * WHEEL_CIRC / 60;

        motor0_Distance += motor0_MPS / motors_Elapsed_Time;
        motor1_Distance += motor1_MPS / motors_Elapsed_Time;

        motor0_Duration = 0;  // Reset counters and update time
        motor1_Duration = 0;
        motors_Last_Time = motors_Current_Time;
    }
}

void motor0Move(bool direction = 1, int speed) {  // simple direction and speed controls
    digitalWrite(MOTOR_0_DIR, direction);
    analogWrite(MOTOR_0_PWM, speed);
}

void motor1Move(bool direction = 1, int speed) {  // simple direction and speed controls
    digitalWrite(MOTOR_1_DIR, direction);
    analogWrite(MOTOR_1_PWM, speed); // analogWrite for PWM
}

bool motorsKill() {  // completely cuts power to motors
    pinMode(MOTOR_0_PWM, OUTPUT);
    pinMode(MOTOR_1_PWM, OUTPUT);
    pinMode(MOTOR_0_DIR, OUTPUT);
    pinMode(MOTOR_1_PWM, OUTPUT);
    return(true);
}
