# Motors
High quality motors are an essential component for any mobile vehicle project, and so selecting the appropriate models is key.
  
## Notes
In the specs, encoder values are written as `[motor shaft count]/[output shaft count]` CPR (Counts Per Revolution). For example, a `24/72` CPR encoder reads at 24 CPR on the motor shaft and 72 CPR on the output shaft, describing a 1:3 geared motor.  
Similarly, current values are written as `[min. current]/[stall current]` A. For example, a `0.35/6` A motor runs at 0.35A under no load ad has a maximum draw of 6A.

## V0
### Options and Specs
**Model A**: [12V 251RPM 18kgcm](https://thepihut.com/products/metal-dc-geared-motor-w-encoder-12v-251rpm-18kg-cm)  
**Specs**:  
 - Output Shaft: 6mm D-shaft
 - Torque: 18kgcm  
 - Speed: 251 RPM  
 - Encoder: 16/700 CPR, Hall sensor
 - Voltage: 12V  
 - Current: 0.35/7A  
 - Weight: 205g
 - Cost: £15.90  

**Model B**: [12V 122RPM 38kgcm](https://thepihut.com/products/metal-dc-geared-motor-w-encoder-12v-122rpm-38kg-cm)  
**Specs**:  
 - Output Shaft: 6mm D-shaft
 - Torque: 38kgcm  
 - Speed: 122 RPM  
 - Encoder: 16/1440 CPR, Hall sensor
 - Voltage: 12V  
 - Current: 0.35/7A  
 - Weight: 205g
 - Cots: £27.90    

### Key Notes & Comparisons
Model B has more than 2x more torque than Model A, but this is unimportant as both can handle the full weight of V0.  
Using 80mm wheels at half of max RPM, Model A and B could achieve `pi*0.08*125.5/60 = 0.53 m/s` and `pi*0.08*61/60 = 0.26 m/s` respectively due to RPM differences.  
B has double the effective encoder precision, but this is unimportant as precise wheel precision is unnecessary here.
B is also twice as expensive due to the higher internal gear ratio.

### Final Decision
**Model A** is the best V0 choice - much lower cost while providing a suitably modest amount of torque and encoder accuracy compared to alternatives. It has (at best) double the velocity and still matches power system requirements perfectly. The 6mm D-shaft is also a common size and suits many COTS wheels via direct drive.