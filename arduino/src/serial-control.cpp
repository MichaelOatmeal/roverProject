/* TODO:
- add error codes
*/

#include "serial-control.h"

struct __attribute__((packed)) PacketIn{
    uint8_t id;  // ID of command in hex
    uint8_t led_Pwm;  // 0-255
};

const int LED_PIN = 13;
uint8_t target_Id;
uint8_t target_Led_Pwm;

void serialInit() {
    Serial.begin(115200);
}

void serialRead() {
    if(Serial.available() > 0) {
        uint8_t next_Byte = Serial.peek();
        if(next_Byte == 0xFF) {  // check if header is valid
            if(Serial.available() >= int(sizeof(PacketIn)) + 1) {  // wait for full packet inc. header
                PacketIn cmd;
                Serial.read();  // eat header byte
                Serial.readBytes((uint8_t*)&cmd, sizeof(PacketIn));

                if(cmd.id > 0xFF) {  // check if data invalid
                    Serial.println("ERR, PARSE: cmd.id = " + cmd.id);
                } else if(cmd.led_Pwm > 0xFF) {
                    Serial.println("ERR, PARSE: cmd.led_Pwm = " + cmd.led_Pwm);
                } else {  // globalise packet values
                target_Id = cmd.id;
                target_Led_Pwm = cmd.led_Pwm;
                }
            }
        } else {
        Serial.read();  // eat invalid data
        }
    }
}