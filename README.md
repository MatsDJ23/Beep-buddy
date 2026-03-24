This project uses a variant of the RPI pico 2, in my case the RP2350-plus there are other controllers that also work with this code just make sure the pinout is the same as this one.

The microcontroller has to run adafruit circuitpython with the libaries from the /lib folder.

Parts required for this project:
- RP2350-plus (Or any microcontroller with the same pinout)
- full size breadboard
- 19 Wires (length varies)
- 2 resistors
- Buzzer
- Led
- tactile switch
- Another button, preferebly one with longer wires for easy use
- 2x16 LCD screen
- 5V breadboard power supply

The buzzer and the led in my code are connected via the same gpio pin because they only have to be controlled at the same time. The gpio setup can be found at the top of the code file.

On the picture of the beep buddy breadbord on the top left is a cable, it doesn't show it on the picture but this connects to the second button refered to in the code as big_button.