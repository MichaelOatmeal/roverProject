/*
Target ID code table
| Direction     | Category  | Message ID | Content                                           |
| ------------- | --------- | ---------- | ------------------------------------------------- |
| Pi –> Arduino | Admin     | 0x01       | Emergency state X - run routine and await command |
|               |           | 0x02       | Exit emergency state                              |
|               |           | 0x03       | Toggle verbose telemetry                          |
|               |           | 0x04       | Toggle audio alerts                               |
|               |           | 0x05       | Debug 1 (eg live PID tuning)                             |
|               |           | 0x06       | Debug 2 (eg live PID)                             |
|               | Command   | 0x10       | Move motors                                       |
|---------------|-----------|------------|---------------------------------------------------|
| Arduino –> Pi | Admin     | 0x80       | Error (eg missing expected component)             |
|               | Telemetry | 0x90       | Motors RPM                                        |
|               |           | 0x91       | Encoder counts (verbose)                          |
|               |           | 0x92       | Motors electronics                                |
|               |           | 0xA0       | Battery voltage and current                       |
|               |           | 0xA1       | Battery temperature                               |
|               |           | 0xB0       | Raw IMU                                           |
|               |           | 0xB1       | Raw GNSS                                          |
|---------------|-----------|------------|---------------------------------------------------|
| Bidirectional | Admin     | 0xFE       | Heartbeat                                         |
*/

// TODO: Update Packet structure to the following:
// Message ID - message target (ie system, motorX)
// Flags - bitmap structure containing extra data (ie motor directions, 
// D0-3 - data bytes
// CRC8 - checksum for data validation
// Terminator - end byte for COBS framing using 0x00

#ifndef SERIAL_CTRL
#define SERIAL_CTRL

#include "Arduino.h"
#include <pch.h> 

bool serialInit();

typedef enum DataId_t : uint8_t {
  EMG 		= 0x01,  	// modify emergency states
  ERR 		= 0x02,  	// error codes
  DEBUG 	= 0x03,  	// verbose/debug data
  CONFIG 	= 0x04,  	// export settings, eg motor CPR, IMU precision
  MOT_IN 	= 0x10,  	// motor commands
  MOT_OUT = 0x11,  	// motor rpm data
  IMU 		= 0x20,   // imu data
  MAG 		= 0x21,		// magnetometer data
  BARO 		= 0x22,		// barometer data
  BATT_IV = 0x30,  	// voltage and current across the entire system
  TEMP 		= 0x31,  	// temperature across the entire system
  HBEAT		= 0xFE		// heartbeat
} DataId_t;

typedef enum EmgId_t : uint8_t {  // emergency id type
  PROX_CRIT = 0x01,		// proximity sensor at critical distance
  WTR_CRIT  = 0x02,		// water detected in chassis
  TEMP_CRIT = 0x03,		// high temps in chassis
  PWR_LOSS	= 0x04,		// main power lost, backup compute power only (flags high power components as unavailable)
  CONN_LOSS	= 0x05,		// serial connection compromised (persistent, will not trust serial unless dedicated message is received intact or jumper is bridged)
} EmgId_t;

typedef struct __attribute__((packed)) MotIn_t {
  int16_t rpm0;  						// 2 bytes...
  int16_t rpm1;  						// 2 bytes...
  uint8_t reserved[12];  			// 12 bytes...
} MotIn_t;  // = 4+12 bytes

typedef struct __attribute__((packed)) Error_t {
  uint32_t timestamp;  			// 4 bytes...
  uint8_t code;  						// 1 bytes...
  uint8_t reserved[11];  			// 11 bytes...
} Error_t;  // = 5+11 bytes

typedef struct __attribute__((packed)) Emg_t {
  EmgId_t code;  						// 1 byte...
  uint8_t reserved[15];  			// 15 bytes...
} Emg_t;  // = 1+15 bytes

typedef struct __attribute__((packed)) MotOut_t {
  int16_t rpm0;  						// 2 bytes...
  int16_t rpm1;  						// 2 bytes...
  uint8_t reserved[12];  			// 12 bytes...
} MotOut_t;  // = 4+12 bytes

typedef struct __attribute__((packed)) IMU_t {
  int16_t accel[3];  				// 2 * 3 bytes...
  int16_t gyro[3];  				// 2 * 3 bytes...
  uint8_t reserved[4];  			// 4 bytes...
} IMU_t;  // = 16 bytes

typedef struct __attribute__((packed)) Mag_t {
  uint32_t timestamp;  			// 4 bytes...
  int16_t mag[3];  					// 2 * 3 bytes...
  uint8_t reserved[6];  			// 6 bytes...
} Mag_t;  // = 10+6 bytes

typedef struct __attribute__((packed)) Baro_t {
  uint32_t timestamp;  			// 4 bytes...
  int32_t pressure; 				// 4 bytes...
  int16_t temperature;  		// 2 bytes...
  uint8_t reserved[6];  			// 6 bytes...
} Baro_t;  // = 10+6 bytes


typedef struct __attribute__((packed)) PacketFields_t {

  DataId_t id;  // 1 byte
  uint8_t sequence;  // 1 byte, global rolling packet number

  union {
    IMU_t imu;
    Mag_t mag;
    Baro_t baro;
    MotIn_t mot_in;
    MotOut_t mot_out;
    Emg_t emg;
    Error_t err;
  } data;  // = 16 bytes

  uint8_t crc8;  // 1 byte
} PacketFields_t;  // 19 bytes, 115200/21 < 5000 packets/sec


typedef union __attribute__((packed)) Packet_t {
  PacketFields_t fields;
  uint8_t raw[sizeof(PacketFields_t)];
} Packet_t;

static_assert(sizeof(MotIn_t) == 16);
static_assert(sizeof(Error_t) == 16);
static_assert(sizeof(Emg_t) == 16);
static_assert(sizeof(MotOut_t) == 16);
static_assert(sizeof(IMU_t) == 16);
static_assert(sizeof(Mag_t) == 16);
static_assert(sizeof(Baro_t) == 16);

static_assert(sizeof(PacketFields_t) == 19);
static_assert(sizeof(Packet_t) == 19);

// handlers
void handler_HEARTBEAT();

void handler_EMG(Emg_t cmd);

void handler_MOT_IN(MotIn_t cmd);

void handler_ERR(Error_t cmd);

/*  // handlers are only needed for incoming packets
void handler_MOT_RPM(MotOut_t cmd);

void handler_IMU(IMU_t cmd);

void handler_MAG(Mag_t cmd);

void handler_BARO(Baro_t cmd);
*/

void incomingRead();
void incomingDispatch();
bool outgoingWrite(Packet_t packet);

#endif