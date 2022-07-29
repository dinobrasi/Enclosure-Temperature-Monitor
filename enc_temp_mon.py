#!/usr/bin/env python
# encoding: utf-8

from RPLCD import i2c
from time import sleep

#2022-07-23 import adafruit_shtc3
import board
import json
import RPi.GPIO as GPIO
import smbus
import sys
import time
#2022-07-23 from functions import getPublicIP

# new
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
bi2c = busio.I2C(SCL, SDA)
pca = PCA9685(bi2c)
pca.frequency = 50
openVal = 90
closedVal = 180

servo0 = servo.Servo(pca.channels[0], min_pulse=600, max_pulse=2600)
# new - end

from cfg import config

GPIO.setwarnings(False)

#2022-07-23 i2cb = board.I2C()
#2022-07-23 sht = adafruit_shtc3.SHTC3(i2cb)

current_state = config["off"]
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

    GPIO.setup(config["lcd_switch"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config["relay_heat"], GPIO.OUT, initial=GPIO.HIGH) # high so they are in their default state when powered up
    GPIO.setup(config["relay_cool"], GPIO.OUT, initial=GPIO.HIGH) # high so they are in their default state when powered up
    GPIO.setup(config["led_heat"], GPIO.OUT)
    GPIO.setup(config["led_cool"], GPIO.OUT)
    GPIO.setup(config["led_power"], GPIO.OUT)
    GPIO.setup(config["sensor_gate"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config["gate_led_open"], GPIO.OUT)
    GPIO.setup(config["gate_led_closed"], GPIO.OUT)
    
    # turn relays and LEDs off
    GPIO.output(config["relay_heat"], True)
    GPIO.output(config["relay_cool"], True)
    GPIO.output(config["led_power"], False)
    GPIO.output(config["led_heat"], False)
    GPIO.output(config["led_cool"], False)
    
    GPIO.output(config["gate_led_open"], False)
    GPIO.output(config["gate_led_closed"], False)
    
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
    MyFile = open("/home/tim/Documents/www/templates/index.html", "w+")
    MyFile.write(state)
    MyFile.close()

def turnOn(which):
    #print("    Relay: Switching on " + which)
    if which == config["heat"]:
        if current_state == config["cool"]:
            turnOff(config["cool"])
        doClose();
        GPIO.output(config["relay_heat"], GPIO.LOW)
        GPIO.output(config["relay_cool"], GPIO.LOW) # need fan to do heat as well
        GPIO.output(config["led_heat"], True)
    else:
        if current_state == config["heat"]:
            turnOff(config["heat"])
        doOpen()
        GPIO.output(config["relay_cool"], GPIO.LOW)
        GPIO.output(config["led_cool"], True)

def turnOff(which):
    #print("    Relay: Switching off " + which)
    if which == config["heat"]:
        GPIO.output(config["relay_heat"], GPIO.HIGH)
        GPIO.output(config["led_heat"], False)
        doOpen()
    else:
        GPIO.output(config["relay_cool"], GPIO.HIGH)
        GPIO.output(config["led_cool"], False)

def doOpen():
    #print("    Vent: Open")
    servo0.angle = openVal
    setDisplay_Vent("Open")
    
def doClose():
    #print("    Vent: Closed")
    servo0.angle = closedVal
    setDisplay_Vent("Closed")

def doLoop():
    current_state = config["off"]
    lcd_state = config["lcd_state"]
    gate_state_last = ""
    gate_state_this = ""    
    gate_sensor = config["sensor_gate"]
    gate_led_open = config["gate_led_open"]
    gate_led_closed = config["gate_led_closed"]
    
    while True:
        #if 1 == 1:
        try:
            sensor_state = GPIO.input(gate_sensor)
            if sensor_state == False:
                GPIO.output(gate_led_open, False)
                GPIO.output(gate_led_closed, True)
                gate_state_this = "Closed"
            else:
                GPIO.output(gate_led_open, True)
                GPIO.output(gate_led_closed, False)
                gate_state_this = "Opened"   
            
            if gate_state_last != gate_state_this:
                #print("Gate state changed to", gate_state_this)
                if (gate_state_this == "Open"):
                    GPIO.output(config["gate_led_open"], True)
                    GPIO.output(config["gate_led_closed"], False)
                    setGateFile("open")
                else:
                    GPIO.output(config["gate_led_open"], False)
                    GPIO.output(config["gate_led_closed"], True)
                    setGateFile("closed")

                setDisplay_Gate(gate_state_this)
            
            gate_state_last = gate_state_this
            
            data = bus.read_i2c_block_data(0x18, 0x05, 2)
            celsius = ((data[0] & 0x1F) * 256) + data[1]
            if celsius > 4095:
                    celsius -= 8192
            celsius = celsius * 0.0625
            fahrenheit = (celsius * 1.8) + 32
            
            #2022-07-23 celsius, relative_humidity = sht.measurements
            #2022-07-23 fahrenheit = (celsius * 1.8) + 32
            #print("%0.1f F" % fahrenheit)
            text = "%0.0f" % fahrenheit
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
    if state == "Off":
        state = "Off "
    lcd.write_string(state)

def setDisplay_Triggers():
    lcd.cursor_pos = (1,6) # base zero
    lcd.write_string(str(config["start_heat"]))
    lcd.cursor_pos = (1,16) # base zero
    lcd.write_string(str(config["start_cool"]))

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
        GPIO.output(config["led_power"], True)
        doLoop()
        doCleanup()
        #print("End")

    except KeyboardInterrupt:
        #print("KeyboardInterrupt")
        doCleanup()