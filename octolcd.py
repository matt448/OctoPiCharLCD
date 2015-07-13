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

import time
import requests
from subprocess import *
from lcdscreen import LCDScreen

# Define GPIO to LCD mapping
lcd = LCDScreen({
        'pin_rs': 25,
        'pin_e': 24,
        'pins_db': [23, 17, 27, 22],
        'backlight': 18,
        'dimensions': [20, 4]
})


def main():
  # Main program block

  while True:
    #Get IP address of the OctoPrint server
    ipaddr = getipaddr()
    ipaddrmsg = '--' + str(ipaddr) + '--'
    #print 'IP ADDR: ' + str(ipaddr)

    # Get the temperatures of the hotend and bed
    r = requests.get('http://127.0.0.1/api/printer')
    #print 'STATUS CODE: ' + str(r.status_code)
    # Non 200 status code means the printer isn't responding
    if r.status_code == 200:
        printeronline = True 
        hotendactual = r.json()['temps']['tool0']['actual']
        hotendtarget = r.json()['temps']['tool0']['target']
        hotmsg = ('Hotend:') + str(hotendactual) + chr(223) + '/' + str(hotendtarget) + chr(223)
        bedactual = r.json()['temps']['bed']['actual']
        bedtarget = r.json()['temps']['bed']['target']
        bedmsg = ('   Bed:') + str(bedactual) + chr(223) + '/' + str(bedtarget) + chr(223)
    else:
        printeronline = False
        hotmsg = ''
        bedmsg = ' 3D Printer offline'

    # Only check job status if the printer is online
    if printeronline:
        r = requests.get('http://127.0.0.1/api/job')
        printtime = r.json()['progress']['printTimeLeft']
        if printtime is None:
            printtimemsg = '00:00:00'
        else:
            printhours = int(printtime/60/60)
            if printhours > 0:
                printminutes = int(printtime/60)-(60*printhours)
            else:
                printminutes = int(printtime/60)
            printseconds = int(printtime % 60)
            printtimemsg = str(printhours).zfill(2) + ':' + str(printminutes).zfill(2) + ':' + str(printseconds).zfill(2)

        printpercent = r.json()['progress']['completion']
        if printpercent is None:
            printpercentmsg = '---%'
        else:
            printpercent = int(printpercent)
            if printpercent < 10:
                printpercentmsg = '  ' + str(printpercent) + '%'
            elif (printpercent >= 10) and (printpercent < 100):
                printpercentmsg = ' ' + str(printpercent) + '%'
            else:
                printpercentmsg = str(printpercent) + '%'

    # Write data to the LCD screen
    lcd.message(ipaddrmsg, 'left')
    lcd.message(hotmsg, 'left')
    lcd.message(bedmsg, 'center')
    if printeronline:
        lcd.message(printtimemsg + '        ' + printpercentmsg, 'left')
    else:
        lcd.message('', 'left')

    time.sleep(3) # 3 second delay


def getipaddr():
        cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output.rstrip()

def cleanup():
    lcd_byte(0x01, LCD_CMD)
    lcd.message("Shutdown", 'center')
    GPIO.cleanup()

if __name__ == '__main__':

  try:
    main()
  finally:
    cleanup() 
