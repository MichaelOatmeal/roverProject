#include "pch.h"

void setup() {
  motorsInit();
  encodersInit();
  serialInit();
  pinMode(LED_PIN, OUTPUT);  // onboard LED has no pwm
}

void loop() {
  serialRead();
	switch (target_Id) {
	case 0x00:
		motorsKill();
		break;
	case 0x03:
		analogWrite(LED_PIN, target_Led_Pwm);
		break;

	case 0x04:
		motor0Move(target_Dir, target_Speed);
		break;

	case 0x05:
		motor1Move(target_Dir, target_Speed);
		break;
	}
}