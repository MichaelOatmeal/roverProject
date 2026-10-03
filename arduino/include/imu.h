#ifndef SENSORS_H
#define SENSORS_H

#include <Adafruit_LIS3MDL.h>
#include <Adafruit_LSM6DSOX.h>

class Sensor_IMU {
	public:
		Sensor_IMU(
			bool lis3mdl_present = true,
			bool lsm6ds_present = true
		);

		void begin();
		void read();

		sensors_event_t getAccel() const {return imu_Accel_;}
    sensors_event_t getGyro() const {return imu_Gyro_;}
    sensors_event_t getMag() const {return imu_Mag_;}
    sensors_event_t getTemp() const {return imu_Temp_;}


	private:
		bool lis3mdl_Present_;
		bool lis3mdl_Success_;
		bool lsm6ds_Present_;
		bool lsm6ds_Success_;

		sensors_event_t imu_Accel_;
		sensors_event_t imu_Gyro_;
		sensors_event_t imu_Mag_;
		sensors_event_t imu_Temp_;

		Adafruit_LSM6DSOX lsm6ds;
		Adafruit_LIS3MDL lis3mdl;

		const uint8_t CALC_RATE_MS_ = 100;  // 10 Hz
};

extern Sensor_IMU imu;


#endif