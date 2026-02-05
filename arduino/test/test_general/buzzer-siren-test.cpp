#include "include.h"

const int pin_Buzzer = 10;
int beep_State = 0;
int beep_Start = 0;


bool playBeep(int beepDuration, int gapDuration) {
    if (beep_State == 0) {
        // start the beep
        tone(pin_Buzzer, NOTE_C3, beepDuration);
        beep_Start = millis();
        beep_State = 1;
        return false; // still beepin'
    }
    else if (beep_State == 1 && millis() - beep_Start >= beepDuration) {
        // start delay between beeps
        noTone(pin_Buzzer);
        beep_Start = millis();
        beep_State = 2;
        return false; // still beepin'
    }
    else if (beep_State == 2 && millis() - beep_Start >= gapDuration) {
        // ready to beep again
        beep_State = 0;
        return true;
    }
}

void buzzerSiren(int siren_Level) {
    switch (siren_Level) {
    case 1: // debug alert for audible feedback
        playBeep(500, 10000);
        break;
    case 2: // warning alert for minor errors such as navigation failure or loss of signal
        playBeep(1000, 3000);
        break;
    case 3: // emergency alert for fatal errors such as no power or motor response
        playBeep(500, 1000);
        break;
    default:
        break;
    }
}