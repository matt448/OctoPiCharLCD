#!/usr/bin/python
#
#--------------------------------------
# OctoPi monitoring code
# 
# Author: Matthew McMillan
#         @matthewmcmillan
#        
# http://matthewcmcmillan.blogspot.com
#--------------------------------------
#
#--------------------------------------
#  20x4 LCD code with backlight control
#  and text justification
#
# Author : Matt Hawkins
# Date   : 06/04/2015
#
# http://www.raspberrypi-spy.co.uk/
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)   - RPi GPIO #25
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe       - RPi GPIO #24
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4             - RPi GPIO #23
# 12: Data Bit 5             - RPi GPIO #17
# 13: Data Bit 6             - RPi GPIO #21
# 14: Data Bit 7             - RPi GPIO #22
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import requests
from subprocess import *

# Define GPIO to LCD mapping
LCD_RS = 25
LCD_E  = 24
LCD_D4 = 23
LCD_D5 = 17
LCD_D6 = 21
LCD_D7 = 22
LED_ON = 15

# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

def main():
  # Main program block

  # Configure GPIO Pins as outputs
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # EN
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable

  # Initialise display
  lcd_init()


  while True:
    ipaddr = getipaddr()
    print 'IP ADDR: ' + str(ipaddr)
    r = requests.get('http://127.0.0.1/api/printer')
    print 'STATUS CODE: ' + str(r.status_code)
    # Non 200 status code means the printer isn't responding
    if r.status_code == 200:
        printeronline = True 
        hotendactual = r.json()['temps']['tool0']['actual']
        hotendtarget = r.json()['temps']['tool0']['target']
        hotmsg = ('Hotend:') + str(hotendactual) + chr(223) + '/' + str(hotendtarget) + chr(223)
        print hotmsg
        bedactual = r.json()['temps']['bed']['actual']
        bedtarget = r.json()['temps']['bed']['target']
        bedmsg = ('   Bed:') + str(bedactual) + chr(223) + '/' + str(bedtarget) + chr(223)
    else:
        printeronline = False
        hotmsg = 'Printer not online'
        bedmsg = ''

    # Only check job status if the printer is online
    if printeronline:
        print 'PRINTER ONLINE'
        r = requests.get('http://127.0.0.1/api/job')
    else:
        print 'PRINTER OFFLINE'

    # Send some centred test
    lcd_string(ipaddr,LCD_LINE_1,2)
    lcd_string(hotmsg,LCD_LINE_2,1)
    lcd_string(bedmsg,LCD_LINE_3,1)
    lcd_string('',LCD_LINE_4,1)

    time.sleep(3) # 3 second delay


    # Blank display
    #lcd_byte(0x01, LCD_CMD)


def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line,style):
  # Send string to display
  # style=1 Left justified
  # style=2 Centred
  # style=3 Right justified

  if style==1:
    message = message.ljust(LCD_WIDTH," ")
  elif style==2:
    message = message.center(LCD_WIDTH," ")
  elif style==3:
    message = message.rjust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_backlight(flag):
  # Toggle backlight on-off-on
  GPIO.output(LED_ON, flag)

def getipaddr():
        cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output.rstrip()

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Shutdown",LCD_LINE_1,2)
    GPIO.cleanup()
