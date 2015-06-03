# OctoPiCharLCD
Show OctoPrint status on a character LCD display

This app will show some status info for OctoPrint on a 20x4 character LCD display. The LCD display is connected to Raspberry Pi GPIO pins and the data is pulled from the OctoPrint API.

##Installation
TODO - Add installation instructions (required apt packages, python libraries, init script)

##Screenshot
![Screenshot](screenshot.jpg)

##LCD Wiring

LCD Pin # | LCD Pin Desc | Connection
:---------: |------------|-----------
1         | GND          | Ground
2         | 5V           | 5V
3         | Contrast     | Center pin 10k pot
4         | RS           | RPi GPIO #25
5         | R/W          | Ground
6         | EN           | RPi GPIO #24
7         | Data Bit 0   | NOT USED N/C
8         | Data Bit 1   | NOT USED N/C
9         | Data Bit 2   | NOT USED N/C
10        | Data Bit 3   | NOT USED N/C
11        | Data Bit 4   | RPi GPIO #23
12        | Data Bit 5   | RPi GPIO #17
13        | Data Bit 6   | RPi GPIO #21
14        | Data Bit 7   | RPi GPIO #22
15        | LCD Backlight +5v   | 5V
16        | LCD Backlight GND | Ground
