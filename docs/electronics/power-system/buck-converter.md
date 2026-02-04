# Buck Converter
Different components often operate at different voltages, but a battery can only provide one voltage level. You could use several batteries to group a system into its various voltages, but a much simpler solution is to convert, for example, 12V into 5V using a buck converter.

### In the specs...
Describe how specs are laid out + other info that may help understand the page

## V0
### Options and Specs  
**Model A**: [5V 1.2A MPM3610](https://thepihut.com/products/adafruit-mpm3610-5v-buck-converter-breakout-21v-in-5v-out-at-1-2a)  
**Specs**:  
 - V-in: 6/21V
 - V-out: 5V
 - Max current: 1.2A
 - Pre-soldered: No
 - Cost: £6.00

**Model B**: [20W Adjustable Converter](https://thepihut.com/products/20w-adjustable-dc-dc-buck-converter-with-digital-display)  
**Specs**:  
 - V-in: 4/40V
 - V-out: 3V3/5V
 - Max current: 5/3A
 - Pre-soldered: Yes
 - Cost: £4.70 

### Key Notes & Comparisons
Model A only outputs a fixed voltage and current, whereas B can provide a wide range (6W vs 20W respectively).
A is potentially much cooler than B at the same voltage due to its lower max current.
A has a significantly smaller footprint than B, but lacks conveniences such as self-calibration and RPP.

### Final Decision
**Model B** is the best choice for V0, as it has a much larger safety margin in terms of current, can output over twice as much power, and comes with pre-soldered connectors. The adjustable voltage also means it can be re-used for other components. Model A may be good for future use in isolated circuits where space and simplicity are essential.
