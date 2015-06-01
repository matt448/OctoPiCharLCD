#!/usr/bin/python

import json
import requests
import math
import time

import Adafruit_CharLCD as LCD

# Raspberry Pi pin configuration:
lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 21
lcd_d7        = 22
#lcd_backlight = 4

lcd_columns = 20
lcd_rows    = 4

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                            lcd_columns, lcd_rows)


lcd.message('   OctoPiCharLCD\n')

r = requests.get('http://127.0.0.1/api/printer')

if r.status_code == 200:
    hotendactual = r.json()['temps']['tool0']['actual']
    hotendtarget = r.json()['temps']['tool0']['target']
    bedactual = r.json()['temps']['bed']['actual']
    bedtarget = r.json()['temps']['bed']['target']

hotmsg = ('HOTEND: ') + str(hotendactual) + '/' + str(hotendtarget) + '\n'
lcd.message(hotmsg)
bedmsg = ('   BED: ') + str(bedactual) + '/' + str(bedtarget) + '\n'
lcd.message(bedmsg)

