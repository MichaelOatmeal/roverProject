#ifndef TIMER
#define TIMER

#include <Arduino.h>

#define	TIMER_SUCCESS 0x00
#define	TIMER_UNAVAIL	0x01
#define	TIMER_OVERFLOW 0x02


class Timer {
	public:
		Timer();

		uint8_t set(uint16_t duration);

		volatile bool A_ready;

		uint16_t ticksCounty;
		uint8_t prescalerBits;
		uint8_t prescalerValue;
		uint8_t timerCounter;

	private:
		
};

extern Timer timer;

#endif