#!/usr/bin/env python
# encoding: utf-8

from RPLCD import i2c
#from time import sleep

import adafruit_shtc3
import board
import json
import RPi.GPIO as GPIO
import sys
import time
from functions import getPublicIP

GPIO.setwarnings(False)

i2cb = board.I2C()   # uses board.SCL and board.SDA
sht = adafruit_shtc3.SHTC3(i2cb)

# set trigger temps
start_heat = 20
start_cool = 74

led_heat = 23 # pin16
led_cool = 24 # pin18
led_power = 25 # pin22
relay_heat = 17 # pin11
relay_cool = 27 # pin13

heat = "Heat"
cool = "Cool"
off = "Off"
current_state = off

lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'

address = 0x27
port = 1

lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap, cols=cols, rows=rows)
    
def setup():
    print("    Setup")
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(relay_heat, GPIO.OUT)
    GPIO.setup(relay_cool, GPIO.OUT)
    GPIO.setup(led_heat, GPIO.OUT)
    GPIO.setup(led_cool, GPIO.OUT)
    GPIO.setup(led_power, GPIO.OUT)

    # turn relays and LEDs off
    GPIO.output(relay_heat, False)
    GPIO.output(relay_cool, False)
    GPIO.output(led_power, False)
    GPIO.output(led_heat, False)
    GPIO.output(led_cool, False)

    lcd.write_string('Current Temp:') # row 1, 15
    lcd.crlf()
    lcd.write_string('Current Mode:') # row 2, 15
    lcd.crlf()
    lcd.write_string('Heat on at:        F') # row 3, 15
    lcd.crlf()
    lcd.write_string('Cool on at:        F') # row 4, 15
    setDisplay_Triggers()

def turnOn(which):
    print("Switching on " + which)
    if which == heat:
        if current_state == cool:
            turnOff(cool)
        GPIO.output(relay_heat, GPIO.HIGH)
        GPIO.output(led_heat, True)
    else:
        if current_state == heat:
            turnOff(heat)
        GPIO.output(relay_cool, GPIO.HIGH)
        GPIO.output(led_cool, True)

def turnOff(which):
    print("Switching off " + which)
    if which == heat:
        GPIO.output(relay_heat, GPIO.LOW)
        GPIO.output(led_heat, False)        
    else:
        GPIO.output(relay_cool, GPIO.LOW)
        GPIO.output(led_cool, False)

def doLoop():
    current_state = off
    while True:
        #try:
            celsius, relative_humidity = sht.measurements
            fahrenheit = (celsius * 1.8) + 32
            print("%0.1f F" % fahrenheit)
            text = "%0.1f F" % fahrenheit
            setDisplay_CurrentTemp(text)
            #return json.dumps({'temperature': "%0.1f F" % fahrenheit,
            #                   'humidity': "%0.1f %%" % relative_humidity})
            
            if fahrenheit > start_heat and fahrenheit < start_cool:
                if current_state != off:
                    turnOff(heat)
                    turnOff(cool)
                    current_state = off
            else:
                if fahrenheit <= start_heat:
                    if current_state != heat:
                        turnOn(heat)
                        current_state = heat
                else:
                    if fahrenheit >= start_cool:
                        if current_state != cool:
                            turnOn(cool)
                            current_state = cool

            setDisplay_CurrentState(current_state)
            time.sleep(2)

        #except KeyboardInterrupt:
        #    print("KeyboardInterrupt")
        #    break

        #except:
        #    print("except") # not helpful lol
        #    time.sleep(0.5)

def setDisplay_CurrentTemp(temp):
    lcd.cursor_pos = (0,14) # base zero
    lcd.write_string(temp)
def setDisplay_CurrentState(state):
    lcd.cursor_pos = (1,14) # base zero
    lcd.write_string(state)

def setDisplay_Triggers():
    lcd.cursor_pos = (2,14) # base zero
    lcd.write_string(str(start_heat))
    lcd.cursor_pos = (3,14) # base zero
    lcd.write_string(str(start_cool))


def Cleanup():
    print("    Cleanup")
    GPIO.setup(relay_heat, False)
    GPIO.setup(relay_cool, False)
    GPIO.setup(led_power, False)
    GPIO.setup(led_heat, False)
    GPIO.setup(led_cool, False)
    GPIO.cleanup()

    lcd.clear()
    lcd.backlight_enabled = False
    lcd.close(clear=True)

if __name__ == '__main__':
    print("Start")

    try:
        setup()
        GPIO.output(led_power, True)
    #GPIO.output(led_power, True)
    #time.sleep(.25)
    #GPIO.output(led_power, False)

    #GPIO.output(led_heat, True)
    #time.sleep(.25)
    #GPIO.output(led_heat, False)

    #GPIO.output(led_cool, True)
    #time.sleep(.25)
    #GPIO.output(led_cool, False)
    
    #GPIO.output(led_power, True)
        doLoop()
    
        Cleanup()
        print("End")

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        Cleanup()

