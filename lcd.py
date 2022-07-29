from RPLCD import i2c
from time import sleep

lcdmode = 'i2c'
cols = 20
rows = 4
charmap = 'A00'
i2c_expander = 'PCF8574'

address = 0x27
port = 1


Locked = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b11111,
  0b11111,
  0b11011,
  0b11111   
)

Test = (
  0b11111,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b11111   
)

sp_01 = (
  0b00000,
  0b00110,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)
sp_02 = (
  0b00000,
  0b01010,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)
sp_03 = (
  0b00000,
  0b01100,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)

sp_04 = (
  0b00000,
  0b01110,
  0b10000,
  0b10001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)

sp_05 = (
  0b00000,
  0b01110,
  0b10001,
  0b10000,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)
sp_06 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10000,
  0b10001,
  0b01110,
  0b00000
)
sp_07 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10001,
  0b10000,
  0b01110,
  0b00000
)
sp_08 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b01100,
  0b00000
)
sp_09 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b01010,
  0b00000
)
sp_10 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10001,
  0b10001,
  0b00110,
  0b00000
)
sp_11 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b10001,
  0b00001,
  0b01110,
  0b00000
)
sp_12 = (
  0b00000,
  0b01110,
  0b10001,
  0b10001,
  0b00001,
  0b10001,
  0b01110,
  0b00000
)
sp_13 = (
  0b00000,
  0b01110,
  0b10001,
  0b00001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)
sp_14 = (
  0b00000,
  0b01110,
  0b00001,
  0b10001,
  0b10001,
  0b10001,
  0b01110,
  0b00000
)




lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap, cols=cols, rows=rows)

lcd.create_char(0, sp_01)
#lcd.create_char(2, sp_02)
lcd.create_char(1, sp_03)
#lcd.create_char(4, sp_04)
lcd.create_char(2, sp_05)
#lcd.create_char(6, sp_06)
lcd.create_char(3, sp_07)
#lcd.create_char(8, sp_08)
lcd.create_char(4, sp_09)
#lcd.create_char(10, sp_10)
lcd.create_char(5, sp_11)
#lcd.create_char(12, sp_12)
lcd.create_char(6, sp_13)
#lcd.create_char(14, sp_14)

lcd.write_string('1. Hello World!')
lcd.crlf()
lcd.write_string('2. Hello World!')
lcd.crlf()
lcd.write_string('3. Hello World!')
lcd.crlf()
lcd.write_string('4. Hello World!')
sleep(1)

lcd.clear()
lcd.cursor_pos = (0,0)
lcd.write(0)
#lcd.cursor_pos = (0,1)

sleep(10)

lcd.backlight_enabled = False
lcd.close(clear=True)
