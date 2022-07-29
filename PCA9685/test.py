#sudo pip3 install adafruit-circuitpython-pca9685
#sudo pip3 install adafruit-circuitpython-motorkit
import time
import RPi.GPIO as GPIO
#import board
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
servo1 = servo.Servo(pca.channels[1], min_pulse=600, max_pulse=2600)

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

def doOpen():
    print("-- Open")
    servo0.angle = openVal
    servo1.angle = openVal
    
def doClose():
    print("-- Closed")
    servo0.angle = closedVal
    servo1.angle = closedVal
    
    
if __name__ == '__main__':
    print("start")
    
    doOpen()
    time.sleep(2)
    doClose()
    time.sleep(2)
    doOpen()
    time.sleep(2)
    doClose()
    time.sleep(2)
    pca.deinit()
    