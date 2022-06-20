#!/usr/bin/env python
# encoding: utf-8

import adafruit_shtc3
import board
import json
import RPi.GPIO as GPIO
import sys
import time
from functions import getPublicIP

GPIO.setwarnings(False)

i2c = board.I2C()   # uses board.SCL and board.SDA
sht = adafruit_shtc3.SHTC3(i2c)

# set trigger temps
start_heat = 20
start_cool = 70

led_heat = 22 # pin16
led_cool = 28 # pin18
led_power = 25 # pin22
relay_heat = 17 # pin11
relay_cool = 27 # pin13

heat = "heat"
cool = "cool"

# waiting for the network at boot. I know there is a setting, but it wasn't working for me.
#net = "eth0"
net = "wlan0"
expected_ip = "192.168.1.16"
waiting = True
counter = 0
while waiting:
    public_ip = getPublicIP(net)
    sys.stdout.write("[" + str(counter) + "] Waiting for IP Address " + expected_ip + ". Getting: " + public_ip + "\r")
    sys.stdout.flush()
    if expected_ip == public_ip:
        waiting = False
    else:
        counter = counter + 1
        if counter == 1000:
            waiting = False 
    
    time.sleep(1)

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
    current_state = "still off"
    while True:
        try:
            celsius, relative_humidity = sht.measurements
            fahrenheit = (celsius * 1.8) + 32
            print("%0.1f F" % fahrenheit)
            #return json.dumps({'temperature': "%0.1f F" % fahrenheit,
            #                   'humidity': "%0.1f %%" % relative_humidity})            
            if fahrenheit > start_heat:
                if current_state != heat:
                    turnOn(heat)
                    current_state = heat
            else:
                if fahrenheit > start_cool:
                    if current_state != cool:
                        turnOn(cool)
                        current_state = cool
                
            time.sleep(2)

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            break

        except:
            print("except") # not helpful lol
            time.sleep(0.5)
    
def Cleanup():
    print("    Cleanup")
    GPIO.setup(relay_heat, False)
    GPIO.setup(relay_cool, False)
    GPIO.setup(led_power, False)
    GPIO.setup(led_heat, False)
    GPIO.setup(led_cool, False)
    GPIO.cleanup()

if __name__ == '__main__':
    print("Start")
    setup()

    GPIO.output(led_power, True)
    time.sleep(.25)
    GPIO.output(led_power, False)

    GPIO.output(led_heat, True)
    time.sleep(.25)
    GPIO.output(led_heat, False)

    GPIO.output(led_cool, True)
    time.sleep(.25)
    GPIO.output(led_cool, False)
    
    GPIO.output(led_power, True)
    doLoop()
    
    Cleanup()
    print("End")
