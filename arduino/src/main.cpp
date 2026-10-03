#include "pch.h"
	uint32_t now;
	uint32_t last_Motor;
	uint32_t last_Accel;
	uint32_t last_Mag;
	uint32_t last_Temp;
	uint32_t last_Gyro;



void setup() {
	// set up motors
	motor0.begin(motor0ISR);
	motor1.begin(motor1ISR);
	imu.begin();

	sei();  // re-enables interrupts

	serialInit();  // start serial connection

	last_Motor = millis();
	last_Accel = millis();
	last_Mag = millis();
	last_Temp = millis();
	last_Gyro = millis();
}

void loop() {
	incomingRead();
	incomingDispatch();
	motorKinematics();
	imu.read();

	now = millis();
	if (now - last_Motor >= 100) {  // 10Hz
		last_Motor = now;

		Packet_t packet{};
		packet.fields.id = MOT_OUT;
		packet.fields.data.mot_out.rpm0 = motor0.getRPM();
		packet.fields.data.mot_out.rpm1 = motor1.getRPM();
		outgoingWrite(packet);
	}

	if (now - last_Accel >= 200) {  // 5Hz
		// accel + gyro
		Packet_t packet{};
		packet.fields.id = ACCEL;
		packet.fields.data.accel.x = imu.getAccel().acceleration.x;
		packet.fields.data.accel.y = imu.getAccel().acceleration.y;
		packet.fields.data.accel.z = imu.getAccel().acceleration.z;
		outgoingWrite(packet);
		last_Accel = now;
	}

	if (now - last_Gyro >= 200) {  // 5Hz
		// gyro
		Packet_t packet{};
		packet.fields.id = GYRO;
		packet.fields.data.gyro.x = imu.getGyro().gyro.x;
		packet.fields.data.gyro.y = imu.getGyro().gyro.y;
		packet.fields.data.gyro.z = imu.getGyro().gyro.z;
		outgoingWrite(packet);
		last_Gyro = now;
	}

	if (now - last_Mag >= 200) {  // 5Hz
		// mag
		Packet_t packet{};
		packet.fields.id = MAG;
		packet.fields.data.mag.x = imu.getMag().magnetic.x;
		packet.fields.data.mag.y = imu.getMag().magnetic.y;
		packet.fields.data.mag.z = imu.getMag().magnetic.z;
		outgoingWrite(packet);
		last_Mag = now;
	}

	if (now - last_Temp >= 200) {  // 5Hz
		// temp
		Packet_t packet{};
		packet.fields.id = TEMP;
		memcpy(packet.fields.data.temp.id, "IMU", 3);
		packet.fields.data.temp.temp = imu.getTemp().temperature;
		outgoingWrite(packet);
		last_Temp = now;
	}
}