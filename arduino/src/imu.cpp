#include "imu.h"

Sensor_IMU::Sensor_IMU(
	bool lis3mdl_Present,
	bool lsm6ds_Present):
	
	lis3mdl_Present_(lis3mdl_Present),
  lsm6ds_Present_(lsm6ds_Present),
	lis3mdl_Success_(false),
	lsm6ds_Success_(false)
	{
	// code to run on init
	}

void Sensor_IMU::begin() {
	if (lis3mdl_Present_) {lis3mdl_Success_ = lis3mdl.begin_I2C();}
	if (lis3mdl_Success_) {
	  lis3mdl.setDataRate(LIS3MDL_DATARATE_155_HZ);
    lis3mdl.setRange(LIS3MDL_RANGE_4_GAUSS);
    lis3mdl.setPerformanceMode(LIS3MDL_MEDIUMMODE);
    lis3mdl.setOperationMode(LIS3MDL_CONTINUOUSMODE);
    lis3mdl.setIntThreshold(500);
    lis3mdl.configInterrupt(false, false, true, // enable z axis
														true, // polarity
														false, // don't latch
														true); // enabled!
	}

	if (lsm6ds_Present_) {lsm6ds_Success_ = lsm6ds.begin_I2C();}

}

void Sensor_IMU::read() {
	if (lsm6ds_Success_) {lsm6ds.getEvent(&imu_Accel_, &imu_Gyro_, &imu_Temp_);}
  if (lis3mdl_Success_) {lis3mdl.getEvent(&imu_Mag_);}
}

Sensor_IMU imu;