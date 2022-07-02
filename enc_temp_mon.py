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
from cfg import config

GPIO.setwarnings(False)

i2cb = board.I2C()
sht = adafruit_shtc3.SHTC3(i2cb)
current_state = config["off"]
lcd = i2c.CharLCD(config["i2c_expander"],
                  config["address"],
                  port=config["port"],
                  charmap=config["charmap"],
                  cols=config["cols"],
                  rows=config["rows"])
    
def setup():
    print("    Setup")
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(config["lcd_switch"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config["relay_heat"], GPIO.OUT)
    GPIO.setup(config["relay_cool"], GPIO.OUT)
    GPIO.setup(config["led_heat"], GPIO.OUT)
    GPIO.setup(config["led_cool"], GPIO.OUT)
    GPIO.setup(config["led_power"], GPIO.OUT)

    # turn relays and LEDs off
    GPIO.output(config["relay_heat"], False)
    GPIO.output(config["relay_cool"], False)
    GPIO.output(config["led_power"], False)
    GPIO.output(config["led_heat"], False)
    GPIO.output(config["led_cool"], False)

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
    if which == config["heat"]:
        if current_state == config["cool"]:
            turnOff(config["cool"])
        GPIO.output(config["relay_heat"], GPIO.HIGH)
        GPIO.output(config["led_heat"], True)
    else:
        if current_state == config["heat"]:
            turnOff(config["heat"])
        GPIO.output(config["relay_cool"], GPIO.HIGH)
        GPIO.output(config["led_cool"], True)

def turnOff(which):
    print("Switching off " + which)
    if which == config["heat"]:
        GPIO.output(config["relay_heat"], GPIO.LOW)
        GPIO.output(config["led_heat"], False)        
    else:
        GPIO.output(config["relay_cool"], GPIO.LOW)
        GPIO.output(config["led_cool"], False)

def doLoop():
    current_state = config["off"]
    lcd_state = config["lcd_state"]
    
    while True:
        #if 1 == 1:
        try:
            celsius, relative_humidity = sht.measurements
            fahrenheit = (celsius * 1.8) + 32
            print("%0.1f F" % fahrenheit)
            text = "%0.1f F" % fahrenheit
            setDisplay_CurrentTemp(text)
            #return json.dumps({'temperature': "%0.1f F" % fahrenheit,
            #                   'humidity': "%0.1f %%" % relative_humidity})
            
            if fahrenheit > config["start_heat"] and fahrenheit < config["start_cool"]:
                if current_state != config["off"]:
                    turnOff(config["heat"])
                    turnOff(config["cool"])
                    current_state = config["off"]
            else:
                if fahrenheit <= config["start_heat"]:
                    if current_state != config["heat"]:
                        turnOn(config["heat"])
                        current_state = config["heat"]
                else:
                    if fahrenheit >= config["start_cool"]:
                        if current_state != config["cool"]:
                            turnOn(config["cool"])
                            current_state = config["cool"]

            if GPIO.input(config["lcd_switch"]) == GPIO.LOW:
                if lcd_state == True:
                    lcd_state = False
                else:
                    lcd_state = True
                lcd.backlight_enabled = lcd_state

            setDisplay_CurrentState(current_state)
            time.sleep(config["loop_delay"])

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            break

        except:
            print("except") # not helpful lol
            time.sleep(0.5)

def setDisplay_CurrentTemp(temp):
    lcd.cursor_pos = (0,14) # base zero
    lcd.write_string(temp)

def setDisplay_CurrentState(state):
    lcd.cursor_pos = (1,14) # base zero
    lcd.write_string(state + " ")

def setDisplay_Triggers():
    lcd.cursor_pos = (2,14) # base zero
    lcd.write_string(str(config["start_heat"]))
    lcd.cursor_pos = (3,14) # base zero
    lcd.write_string(str(config["start_cool"]))

def Cleanup():
    print("    Cleanup")
    GPIO.setup(config["relay_heat"], False)
    GPIO.setup(config["relay_cool"], False)
    GPIO.setup(config["led_power"], False)
    GPIO.setup(config["led_heat"], False)
    GPIO.setup(config["led_cool"], False)
    GPIO.cleanup()
    lcd.clear()
    lcd.backlight_enabled = False
    lcd.close(clear=True)

if __name__ == '__main__':
    print("Start")

    #print(str(config["start_heat"]))
    try:
        setup()
        GPIO.output(config["led_power"], True)
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
