/* TODO:
- add crc8 and COBS

Packet Structure:
	current - header, id, data1, data2, data3, data4
	target - id, data1, data2, ..., dataX, flags, crc8, cobs terminator

Packet parser breakdown:
	read bytes and place in buffer until 0x00 is read
	decode cobs
	check crc8, discard if bad and update packet loss
	read id
	read data bytes (length implicit from id, use lookup table)
	decode flags bitmap
	execute command

CRC8 breakdown:
	(crc) xor (next byte)
	for the next 8 bits (ie loop 8 times), perform bitwise long division w/ no carries:
		if leading bit of (crc) is 1, shift towards MSB [trim MSB] and then xor with (poly)
		else just shift
	return crc

	bool crc8_decoder(uint8_t crc_rx, uint8_t *data, uint8_t length) {
		uint8_t crc_calc = 0x00  // crc starts as 0x00
		for (uint8_t i = 0; i < length; i++) { // for each byte in data array
			crc_calc ^= data[i] // 0x00 XOR data byte
			for (uint8_t j = 0; j < 8; j++) { // for each bit in the byte
				if (crc_calc & 0x80) { // if binary starts with 1
					crc_calc = (crc_calc << 1) ^ 0x07 // shift by 1 place then xor with poly 00
				} else {
					crc_calc = crc_calc << 1 // else just shift
				}
			}
		}
		if (crc_rx == crc_calc) {return true} else {return false}
	}

*/

#include "serial-control.h"

Packet_t packetRcv;

uint8_t nowByte = 0;
uint8_t packetByteCounter = 0;
bool packetRcvReady = false;
bool packetStrReady = false;
bool packetSndReady = false;

uint8_t lastSequence = 0;
bool haveSequence = false;
uint8_t outgoingSequence = 0;


bool serialInit() {
  Serial.begin(230400); return true;
}

// handlers defined in serial-control.h

uint8_t crc8(const uint8_t* data, size_t len) {
	uint8_t crc = 0x00;

	while (len--)	{
		crc ^= *data++;

		for (uint8_t i = 0; i < 8; i++) {
			if (crc & 0x80)
				crc = (crc << 1) ^ 0x07;
			else
				crc <<= 1;
		}
	}

	return crc;
}

bool outgoingWrite(Packet_t packet) {

	// Calculate CRC over everything except the CRC byte
	packet.fields.sequence = outgoingSequence++;	

	packet.fields.crc8 =
		crc8(packet.raw, sizeof(packet.raw) - 1);

	if (Serial.availableForWrite() >= (sizeof(Packet_t) + 2)) {

		Serial.write(0xAA);
		Serial.write(packet.raw, sizeof(packet.raw));
		Serial.write(0x55);

		return true;
	}

	return false;
}

//void constructPacket(uint8_t type, )

void incomingRead() {
	while (Serial.available() > 0 && !packetRcvReady) {

		uint8_t b = Serial.read();

		// waiting for packet header
		if (!packetStrReady) {
			if (b == 0xAA) {
				packetStrReady = true;
				packetByteCounter = 0;
			}
			continue;
		}

		// inside a packet
		if (b == 0x55) {
			if (packetByteCounter == sizeof(packetRcv.raw)) {

				// CRC byte is the final byte of the packet
				uint8_t receivedCRC = packetRcv.raw[sizeof(packetRcv.raw) - 1];

				// calculate CRC over everything except the CRC byte
				uint8_t calculatedCRC = crc8(packetRcv.raw, sizeof(packetRcv.raw) - 1);

				if (receivedCRC == calculatedCRC) {packetRcvReady = true;}
				else {packetRcvReady = false;}  // Bad packet
			}

			packetStrReady = false;
			packetByteCounter = 0;
			continue;
		}

		// avoid overflow the packet buffer
		if (packetByteCounter < sizeof(packetRcv.raw)) {
			packetRcv.raw[packetByteCounter++] = b;
		} else {
			// too many bytes 
			packetStrReady = false;
			packetByteCounter = 0;
		}
	}
}

void incomingDispatch() {  // assigns meaning to packets
	if (!packetRcvReady) {return;}

	// verify sequence no. matches (non-erroneous while still being worked on)
	uint8_t sequence = packetRcv.fields.sequence;
	if (haveSequence) {
		uint8_t expectedSequence = lastSequence + 1;

		if (sequence != expectedSequence) {
		}
	}

	lastSequence = sequence;
	haveSequence = true;


	switch(packetRcv.fields.id) {
		case HBEAT:
    	handler_HEARTBEAT();
    	break;
		case MOT_IN:
			handler_MOT_IN(packetRcv.fields.data.mot_in);
			break;
		case ERR:
			handler_ERR(packetRcv.fields.data.err);
			break;
		case EMG:
			handler_EMG(packetRcv.fields.data.emg);
			break;
		default:
			break;}

	packetRcvReady = false;

}


// incoming handlers

void handler_HEARTBEAT() {

    Packet_t response{};

    response.fields.id = HBEAT;

    outgoingWrite(response);
}

void handler_EMG(Emg_t cmd) {
  switch (cmd.code) {
		case WTR_CRIT:
			break;
	}
}

void handler_MOT_IN(MotIn_t cmd) {
	if (cmd.rpm0 == 0) {motor0.stop();}  // full brake when 0
	else {motor0.setRPM(cmd.rpm0);}

	if (cmd.rpm1 == 0) {motor1.stop();}  // full brake when 0
	else {motor1.setRPM(cmd.rpm1);}
};

void handler_ERR(Error_t cmd) {
  switch (cmd.code) {
		case 0x01:  // example
			break;
  }
}


/*
void serialReadDep() {
  if((header == 0) && (Serial.available())) {
    next_Byte = Serial.peek();
    if((next_Byte == 0xFF)) {  // check if header is valid
      header = 1;
      Serial.read();  // eat header byte
      heartbeatIn = millis();  // reset heartbeat timer
    } else { Serial.read();} // eat invalid byte
	}

	if((header == 1) && (Serial.available())) {  // check for valid header and waiting data
		heartbeatIn = millis();  // reset heartbeat timer if receiving packet, including invalid data
		next_Byte = Serial.peek();  // store packet id
		switch (next_Byte) {  // check id
			case 0x00:  // insert emergency action here
				target_Id = Serial.read();
				header = 0;
				break;

			case 0x01:  // motor0 command
			case 0x02:  // motor1 command
				if(Serial.available() >= 5) {  // wait for full packet
					Packet cmd;
					Serial.readBytes((uint8_t*)&cmd, sizeof(cmd));  // read packet and assign to the variable cmd 
					header = 0;  // reset header

					// globalise serial data
					target_Id = cmd.id;
					target_Dir = cmd.byte1;
					target_Speed = cmd.byte2;
				}
				break;

			case 0xFE:  // serial heartbeat, only received when silent for 500ms
				Serial.read();
				if(Serial.availableForWrite()) {  // respond with ACK message
					Serial.write(0xFF);
					Serial.write(0xFE);
				}
				header = 0;
				break;

			default:
				Serial.read();  // eat invalid data
				header = 0;
				break;
		}
	}

	uint32_t now = millis();
	if(now - heartbeatIn > heartbeatInterval) {  // action to take if heartbeat stops
		motorsKill();
		digitalWrite(13, HIGH);
	}
}

void serialWriteDep(Packet cmd_Out) {  // write data to the serial bus
	uint32_t now = millis();
  if (now - lastSerialOut <= SERIAL_OUT_RATE_MS) return;
	lastSerialOut = now;
	if (now - heartbeatIn >= heartbeatInterval) return;  // action to take if heartbeat stops

	switch (cmd_Out.id) {
		case 0x00:  // ACK motor kill
			if (Serial.availableForWrite()) {
				Serial.write(0xFF); Serial.write(cmd_Out.id);}
			break;

		case 0x01:  // motor0 encoder values
		case 0x02:  // motor1 encoder values
			if(Serial.availableForWrite() >= 6) {
				Serial.write(0xFF); Serial.write((uint8_t*)&cmd_Out, sizeof(cmd_Out));}  // convert Out packet to raw bytes
			break; 
		}
	prev_Cmd_Out = cmd_Out;
}
	*/