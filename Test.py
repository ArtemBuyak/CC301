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
#print(str[3])


str2.append(str[3])
#print(type(str))

#print(str)
#print(struct.unpack('f', str))

str[0] = 0x00
str[1] = 0x00
str[2] = 0x00
str[3] = 0x00

str.reverse()
i = 6
i /= 2
a = 4
#print(struct.unpack('h', byte_arr))
byte_arr = bytearray(b'\x71\x5d\x09\x46')
print(struct.unpack("f", byte_arr)[0])


