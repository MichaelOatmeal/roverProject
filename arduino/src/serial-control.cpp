/* TODO:
- add error codes
*/

#include "serial-control.h"

struct __attribute__((packed)) PacketIn{  // message id, then data
  uint8_t id;
  uint8_t byte1;
	uint8_t byte2;
	uint8_t byte3;
	uint8_t byte4;

};

const int LED_PIN = 13;
uint8_t target_Id;
uint8_t target_Led_Pwm;
uint8_t target_Dir;  
uint8_t target_Speed;
bool header = 0;

void serialInit() {
    Serial.begin(115200);
}

void serialRead() {
	target_Id = 0;
	if(Serial.available() > 0) {

		uint8_t next_Byte = Serial.peek();
		if((next_Byte == 0xFF) && (header == 0)) {  // check if header is valid
			header = 1;
			Serial.read();  // eat header byte
		}

		if((header == 1) && (Serial.available())){  // check for valid header and waiting data
			next_Byte = Serial.peek();  // store packet id
			switch (next_Byte) {  // check id
			case 0x00:  // emergency motor kill
				Serial.read();
				break;
			case 0x03:
				if(Serial.available() >= 2) {  // wait for full packet
				PacketIn cmd;
				Serial.readBytes((uint8_t*)&cmd, 2);
				header = 0;

				target_Id = cmd.id;
				target_Led_Pwm = cmd.byte1;
				}
				break;

			case 0x04:
			case 0x05:
				if(Serial.available() >= 3) {  // wait for full packet
				PacketIn cmd;
				Serial.readBytes((uint8_t*)&cmd, 3);
				header = 0;

				target_Id = cmd.id;
				target_Dir = cmd.byte1;
				target_Speed = cmd.byte2;
				}
				break;

			default:
				Serial.read();  // eat invalid data
				header = 0;
				break;
			}

		} else {
			Serial.read();  // eat invalid header
		}
	}
}