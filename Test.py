from datetime import datetime
import struct

time = datetime.now()
#print(time.year-2000)
#print(time.month)
#print(time.day)
#print(time.hour)
#print(time.minute)
#print(time.second)
str = bytearray(b'')
str.append(0x00)
str.append(0x00)
str.append(0xdd)
str.append(0xcc)
str2 = []
str2.append(0x15)
print(str[3])


str2.append(str[3])
print(type(str))

print(str)
print(struct.unpack('f', str))

str[0] = 0xcc
str[1] = 0xdd
str[2] = 0x00
str[3] = 0x00

print(struct.unpack('f', str))
byte_arr = bytearray(b'')
byte_arr.append(0x15)
print(byte_arr)