#include <Arduino.h>
#include <timer.h>

Timer::Timer() {timerCounter = 0;}  // construction definition

uint8_t Timer::set(uint16_t duration) {  // duration in ms
	TCNT1 = 0;  // clear counter
	TCCR1B &= ~0b111;  // clear prescalar bits

  TCCR1A = 0;           // Init Timer1A
  TCCR1B = 0;           // Init Timer1B


	prescalerBits = 0;
	ticksCounty = 0;

	TCCR1B |= (1 << WGM12);  // set CTC mode - Clear Timer on Compare match

	const uint16_t prescalerList[5] = {1, 8, 64, 256, 1024};
  const uint8_t bits[5] = {0b1, 0b10, 0b11, 0b100, 0b101}; 

  for (int i=0; i < 5; i++) {
    uint32_t ocr = (((uint64_t)F_CPU / 1000UL) * duration / prescalerList[i]) - 1;
    if (ocr <= 0xFFFF) {prescalerBits = bits[i]; ticksCounty = (uint16_t)ocr; break;}
    }


  TCCR1B |= prescalerBits;  // set prescalar to appropriate value
	
  OCR1A = ticksCounty;  // use timer A

	// Clear any old compare match
	TIFR1 |= (1 << OCF1A);
  TIMSK1 |= (1 << OCIE1A);  // Enable Timer COMPA Interrupt

	Serial.print("Timer set for ");
	Serial.println(duration);

	return TIMER_SUCCESS;
}

Timer timer;

ISR(TIMER1_COMPA_vect)
{
	timer.A_ready = true;
	TIMSK1 &= ~(1 << OCIE1A);  // disable COMPA interrupts
	timer.timerCounter++;
}

