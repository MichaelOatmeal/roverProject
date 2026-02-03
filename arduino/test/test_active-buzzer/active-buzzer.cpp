#include "Arduino.h"
#include "pitches.h"
 
// notes in the melody
int melody[] = {
  NOTE_C5, NOTE_C5, NOTE_C6, NOTE_G5, NOTE_FS5, NOTE_F5, NOTE_DS5, NOTE_C5, NOTE_DS5, NOTE_F5};

// relative duration of each note
int durations[] = {
  250, 250, 500, 750, 500, 500, 500, 250, 250, 250
};

//first note of each musical phrase
int melodyNoteOne[] = {
  NOTE_C5, NOTE_AS4, NOTE_A4, NOTE_GS4
};

int duration = 0;
 
void setup() {
};
 
void loop() { 
  for (int startNote = 0; startNote < 4; startNote++) {
    melody[0] = melodyNoteOne[startNote];
    melody[1] = melodyNoteOne[startNote];

    for (int thisNote = 0; thisNote < 10; thisNote++) {
      duration = durations[thisNote]*0.55; //multiplier changes tempo
      // pin8 outputs the voice
      tone(8, melody[thisNote], duration);
      
      // dleays for note duration as tone() is non-blocking
      delay(duration);
    }
  }
}