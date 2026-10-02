#include "pch.h"
	uint32_t now;
	uint32_t last_Motor;

void setup() {
	// set up motors
	motor0.begin(motor0ISR);
	motor1.begin(motor1ISR);

	sei();  // re-enables interrupts

	serialInit();  // start serial connection

	last_Motor = millis();
}

void loop() {
	incomingRead();
	incomingDispatch();
	motorKinematics();

	now = millis();
	if (now - last_Motor >= 100) {  // 10Hz
		last_Motor = now;

		Packet_t packet;
		packet.fields.id = MOT_OUT;
		packet.fields.data.mot_out.rpm0 = motor0.getRPM();
		packet.fields.data.mot_out.rpm1 = motor1.getRPM();
		outgoingWrite(packet);
	}

	
}