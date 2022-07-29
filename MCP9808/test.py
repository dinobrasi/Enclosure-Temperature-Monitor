import smbus
import time
bus = smbus.SMBus(1)
config = [0x00, 0x00]
bus.write_i2c_block_data(0x18, 0x01, config)
bus.write_byte_data(0x18, 0x08, 0x03)
time.sleep(0.5)
data = bus.read_i2c_block_data(0x18, 0x05, 2)
celsius = ((data[0] & 0x1F) * 256) + data[1]
if celsius > 4095:
        celsius -= 8192
celsius = celsius * 0.0625
fahrenheit = (celsius * 1.8) + 32

print("%.2f C" % celsius)
print("%.2f F" % fahrenheit)