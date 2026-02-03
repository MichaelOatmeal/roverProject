# Motor Driver Boards

Driver boards which allow the motor to recieve commands from the real-time microcontroller. Though motors can theoretically be directly connected to the microcontroller, the 5V output and low current wouldn't be enough for anything beyond the smallest of hobby motors. There's also a risk of damaging the GPIO pins due to back EMF (motor sending high voltage back to power supply).

### In the specs...

Current is written as `[max continuous draw]/[peak draw]`.  
Safety margin is calculated as `[max continouos draw]/[peak motor draw]`.

## V0
### Options and Specs
**Model A**: [Dual channel 10A](https://thepihut.com/products/10a-5v-30v-2-channel-dc-motor-driver)  
**Specs**:  
 - Channels: 2  
 - Current: 10/30A  
 - Voltage: 5/30V  
 - Reverse Polarity Protection (RPP): No  
 - I/O Pins: 4  
 - Cost: £22.20  

**Model B**: [Dual channel 7A](https://thepihut.com/products/2x7a-dc-motor-driver)  
**Specs**:  
 - Channels: 2  
 - Current: 7/50A  
 - Voltage: 7/24V  
 - Reverse Polarity Protection (RPP): Yes  
 - I/O Pins: 6  
 - Cost: £20.20  

**Model C**: [Single channel 43A](https://www.amazon.co.uk/JZK-BTS7960B-Double-Stepper-H-Bridge/dp/B09HGBM5D2)  
**Specs**:  
 - Channels: 1  
 - Current: 43A (likely cont.)  
 - Voltage: 5.5/27V  
 - Reverse Polarity Protection (RPP): N/A  
 - I/O Pins: 6 
 - Cost: £7.19  

### Key Notes and Comparisons
- Model C is a single channel board and thus is the cheapest option; one board per motor means greater redundancy, but takes up more space.  
- Model C also seems to have the highest continuous current output per channel (unconfirmed), more than 6x that of Model B. However, the V0 motors draw a max of 7A each, so only Model A lacks a safety margin.  
- Model A lacks RPP, but this can be mitigated via thorough wiring checks.  

### Final Decision
**Model A** is the best V0 choice - it has the most appropriate safety margin, and requires the fewest I/O pins for full control. The lack of RPP does pose risk, but this is offset by its clear labelling and addition of test buttons. Model B can also easily be used as an alternative, though not at full motor load.