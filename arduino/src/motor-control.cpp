#include <motor-control.h>

Motor::Motor(  // construction definition
	uint8_t l_pwm_pin, 
	uint8_t r_pwm_pin, 
	uint8_t enc_a_pin, 
	uint8_t enc_b_pin, 
	bool inv_dir,
	int counts_per_rev, 
	float wheel_diam):

	L_PWM_PIN_(l_pwm_pin),
	R_PWM_PIN_(r_pwm_pin),
	ENC_A_PIN_(enc_a_pin),
	ENC_B_PIN_(enc_b_pin),
	INV_DIR_(inv_dir),
	WHEEL_DIAM_(wheel_diam), 
	WHEEL_CIRC_(PI * wheel_diam),
	CPR_(counts_per_rev),
	encoderCounts_(0),
	targetRPM_(0),
	currentRPM_(0),
	currentMPS_(0.0f),
	distance_(0.0f)
	{
	// code to run on instance creation		
	}

void Motor::begin(void (*isr)()) {
  // initialise motor & encoder pins
	pinMode(L_PWM_PIN_, OUTPUT);
	pinMode(R_PWM_PIN_, OUTPUT);
	analogWrite(L_PWM_PIN_, 0); 
	analogWrite(R_PWM_PIN_, 0);

	pinMode(ENC_A_PIN_, INPUT_PULLUP);
	pinMode(ENC_B_PIN_, INPUT_PULLUP);
	attachInterrupt(digitalPinToInterrupt(ENC_A_PIN_), isr, CHANGE);
	//attachInterrupt(digitalPinToInterrupt(ENC_B_PIN_), isr, CHANGE);  // encB isn't on an interrupt capable pin yet

	encA_Last_ = digitalRead(ENC_A_PIN_);
	encB_Last_ = digitalRead(ENC_B_PIN_);

	motor_Last_ = millis();
}

void Motor::setRPM(int16_t rpm) {
  if (INV_DIR_ == true) {
		rpm = -rpm;
	}  
	
	targetRPM_ = rpm;

    // PWM magnitude must always be positive
    uint8_t pwm = constrain(abs(rpm), 0, 255);
    
		// set to 0 to avoid signal overlap
		analogWrite(R_PWM_PIN_, 0);
    analogWrite(L_PWM_PIN_, 0);

    if (rpm > 0) {
        // Forward
        analogWrite(R_PWM_PIN_, 0);
        analogWrite(L_PWM_PIN_, pwm);
    }
    else if (rpm < 0) {
        // Reverse
        analogWrite(L_PWM_PIN_, 0);
        analogWrite(R_PWM_PIN_, pwm);
    }
    else {
        // Stop
        analogWrite(L_PWM_PIN_, 0);
        analogWrite(R_PWM_PIN_, 0);
    }
}

void Motor::encoderInterrupt() {  // read encoder
	bool A = digitalRead(ENC_A_PIN_);
	bool B = digitalRead(ENC_B_PIN_);

	if (A == B) {
		++encoderCounts_;
	} else {
		--encoderCounts_;
	}

	encA_Last_ = A;
	encB_Last_ = B;
}

void Motor::updateKinematics() {  // calculate RPM, MPS, and distance travelled
	uint32_t now_ = millis();
	uint32_t dt = now_ - motor_Last_;
	
	if(dt >= CALC_RATE_MS_) {  // Calculate every >100ms
		noInterrupts();  // stop encoderCounts from being changed during calculations
		int32_t counts = encoderCounts_;

		encoderCounts_ = 0;
		interrupts();

		if (INV_DIR_) {
				counts = -counts;
		}

		currentRPM_ =
			(float(counts) / float(CPR_)) /
			(float(dt) / 60000.0f);
		
		currentMPS_ = currentRPM_ * WHEEL_CIRC_ / 60.0f;

		distance_ += currentMPS_ * (dt / 1000.0f);

		motor_Last_ = now_;
	}
}

void Motor::stop() {  // kills motors
		digitalWrite(L_PWM_PIN_, LOW); 
		digitalWrite(R_PWM_PIN_, LOW); 
	}


// create motor instances
Motor motor1(6, 5, 2, 4);
Motor motor0(9, 10, 3, 7, true);

// group together functions

void motorKinematics() {
	motor0.updateKinematics();
	motor1.updateKinematics();
}

// ISRs can't be defined within a class due to the implicit `this*`
// Global wrappers for ISRs, less robust than a lookup table/instance list but works fine for a set amount of motors
void motor0ISR() {motor0.encoderInterrupt();}
void motor1ISR() {motor1.encoderInterrupt();}