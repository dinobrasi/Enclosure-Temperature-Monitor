#!/usr/bin/env python
# encoding: utf-8

from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from cfg import config
from RPLCD import i2c
from time import sleep

import board
import busio
import json
import RPi.GPIO as GPIO
import smbus
import sys
import time

bi2c = busio.I2C(SCL, SDA)
pca = PCA9685(bi2c)
pca.frequency = 50

servo0 = servo.Servo(pca.channels[0], min_pulse=600, max_pulse=2600)
servo1 = servo.Servo(pca.channels[1], min_pulse=600, max_pulse=2600)

GPIO.setwarnings(False)

off = config["off"]
heat = config["heat"]
cool = config["cool"]
current_state = off

vent_side_open = config["vent_side_open"]
vent_side_closed = config["vent_side_closed"]
vent_front_open = config["vent_front_open"]
vent_front_closed = config["vent_front_closed"]

gpio_lcd_switch = config["gpio_lcd_switch"]
gpio_led_heat = config["gpio_led_heat"]
gpio_led_cool = config["gpio_led_cool"]
gpio_led_power = config["gpio_led_power"]
gpio_led_closed = config["gpio_led_closed"]
gpio_led_open = config["gpio_led_open"]
gpio_relay_cool = config["gpio_relay_cool"]
gpio_relay_heat = config["gpio_relay_heat"]
gpio_sensor_gate = config["gpio_sensor_gate"]

start_heat = config["start_heat"]
start_cool = config["start_cool"]

lcd = i2c.CharLCD(config["i2c_expander"],
                  config["address"],
                  port=config["port"],
                  charmap=config["charmap"],
                  cols=config["cols"],
                  rows=config["rows"],
                  backlight_enabled=config["lcd_state"])

bus = smbus.SMBus(1)
busconfig = [0x00, 0x00]
bus.write_i2c_block_data(0x18, 0x01, busconfig)
bus.write_byte_data(0x18, 0x08, 0x03)

gate_state_last = ""
gate_state_this = ""

def setup():
    #print("    Setup")
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(gpio_lcd_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(gpio_relay_heat, GPIO.OUT, initial=GPIO.HIGH) # high so they are in their default state when powered up
    GPIO.setup(gpio_relay_cool, GPIO.OUT, initial=GPIO.HIGH) # high so they are in their default state when powered up
    GPIO.setup(gpio_led_heat, GPIO.OUT)
    GPIO.setup(gpio_led_cool, GPIO.OUT)
    GPIO.setup(gpio_led_power, GPIO.OUT)
    GPIO.setup(gpio_sensor_gate, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(gpio_led_open, GPIO.OUT)
    GPIO.setup(gpio_led_closed, GPIO.OUT)
    
    # turn relays and LEDs off
    GPIO.output(gpio_relay_heat, True)
    GPIO.output(gpio_relay_cool, True)
    GPIO.output(gpio_led_power, False)
    GPIO.output(gpio_led_heat, False)
    GPIO.output(gpio_led_cool, False)
    
    GPIO.output(gpio_led_open, False)
    GPIO.output(gpio_led_closed, False)
    
    lcd.write_string('Temp:   F Mode:') # row 1, 6 - 1, 17
    lcd.crlf()
    lcd.write_string('Heat:   F Cool:   F') # row 2, 6 - 2, 17
    lcd.crlf()
    lcd.write_string('Vent: ') # row 3, 6
    lcd.crlf()
    lcd.write_string('Gate: ') # row 4, 6

    doOpen()
    setDisplay_Triggers()

def setGateFile(state):
    #print("set gate file:", state)
    MyFile = open("/home/tim/Documents/etm/www/index.html", "w+")
    MyFile.write(state)
    MyFile.close()

def turnOn(which):
    #print("    Relay: Switching on " + which)
    if which == heat:
        if current_state == cool:
            turnOff(cool)
        doClose();
        GPIO.output(gpio_relay_heat, GPIO.LOW)
        GPIO.output(gpio_relay_cool, GPIO.LOW) # need fan to do heat as well
        GPIO.output(gpio_led_heat, True)
    else:
        if current_state == heat:
            turnOff(heat)
        doOpen()
        GPIO.output(gpio_relay_cool, GPIO.LOW)
        GPIO.output(gpio_led_cool, True)

def turnOff(which):
    #print("    Relay: Switching off " + which)
    if which == heat:
        GPIO.output(gpio_relay_heat, GPIO.HIGH)
        GPIO.output(gpio_led_heat, False)
        doOpen()
    else:
        GPIO.output(gpio_relay_cool, GPIO.HIGH)
        GPIO.output(gpio_led_cool, False)

def doOpen():
    #print("    Vent: Open")
    servo0.angle = vent_side_open
    servo1.angle = vent_front_open
    setDisplay_Vent("Open")
    
def doClose():
    #print("    Vent: Closed")
    servo0.angle = vent_side_closed
    servo1.angle = vent_front_closed
    setDisplay_Vent("Closed")

def doLoop():
    current_state = off
    lcd_state = config["lcd_state"]
    gate_state_last = ""
    gate_state_this = ""    
    gate_sensor = gpio_sensor_gate
    gate_led_open = gpio_led_open
    gate_led_closed = gpio_led_closed
    
    while True:
        try:
            sensor_state = GPIO.input(gate_sensor)
            if sensor_state == False:
                GPIO.output(gate_led_open, False)
                GPIO.output(gate_led_closed, True)
                gate_state_this = "Closed" # for display
            else:
                GPIO.output(gate_led_open, True)
                GPIO.output(gate_led_closed, False)
                gate_state_this = "Open" # for display
            
            if gate_state_last != gate_state_this:
                if (gate_state_this == "Open"):
                    GPIO.output(gpio_led_open, True)
                    GPIO.output(gpio_led_closed, False)
                    setGateFile("open") # for api
                else:
                    GPIO.output(gpio_led_open, False)
                    GPIO.output(gpio_led_closed, True)
                    setGateFile("closed") # for api

                setDisplay_Gate(gate_state_this)
            
            gate_state_last = gate_state_this
            
            data = bus.read_i2c_block_data(0x18, 0x05, 2)
            celsius = ((data[0] & 0x1F) * 256) + data[1]
            if celsius > 4095:
                    celsius -= 8192
            celsius = celsius * 0.0625
            fahrenheit = (celsius * 1.8) + 32
            text = "%0.0f" % fahrenheit
            setDisplay_CurrentTemp(text)
            
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

            if GPIO.input(gpio_lcd_switch) == GPIO.LOW:
                if lcd_state == True:
                    lcd_state = False
                else:
                    lcd_state = True
            
            lcd.backlight_enabled = lcd_state
            setDisplay_CurrentState(current_state)
            time.sleep(config["loop_delay"])

        except KeyboardInterrupt:
            #print("KeyboardInterrupt")
            break

        except:
            print("Error!") # not helpful lol
            time.sleep(0.5)

def setDisplay_CurrentTemp(temp):
    lcd.cursor_pos = (0,6) # base zero
    lcd.write_string(temp)

def setDisplay_CurrentState(state):
    lcd.cursor_pos = (0,16) # base zero
    if state == off:
        state = "Off "
    lcd.write_string(state)

def setDisplay_Triggers():
    lcd.cursor_pos = (1,6) # base zero
    lcd.write_string(str(start_heat))
    lcd.cursor_pos = (1,16) # base zero
    lcd.write_string(str(start_cool))

def setDisplay_Vent(state):
    lcd.cursor_pos = (2,6) # base zero
    lcd.write_string(state)

def setDisplay_Gate(state):
    lcd.cursor_pos = (3,6) # base zero
    lcd.write_string(state)

def doCleanup():
    #print("    doCleanup")
    GPIO.cleanup()
    lcd.clear()
    lcd.backlight_enabled = False
    lcd.close(clear=True)
    pca.deinit()

if __name__ == '__main__':
    #print("Start")

    try:
        setup()
        GPIO.output(gpio_led_power, True)
        doLoop()
        doCleanup()
        #print("End")

    except KeyboardInterrupt:
        #print("KeyboardInterrupt")
        doCleanup()