from meter.connectors import RS232Connector, BaseConnector, GSMConnector, IPConnector
from meter.proto.StrumenTS_05_07 import StrumenTS_05_07
from meter.crc import CRC16_C0C1

# rs232_obj = RS232Connector(
#      port='/dev/ttyUSB0',
#      baudrate=9600,
#      bytesize=RS232Connector.EIGHTBITS,
#      parity=RS232Connector.PARITY_NONE,
#      stopbits=1
# )

# rs232_obj = GSMConnector()

conn_obj = IPConnector(
    host='178.163.135.51',
    port=10001
)

conn_obj.connect()

proto_obj = StrumenTS_05_07()

conn_obj.write(proto_obj.pack(0x00, proto_obj.ARCHIVE_ALL_VALUE_HOUR, 0x01, 0x18, 0x0D, proto_obj.ARCHIVE_ALL_CONTOUR_1))

recv_data = conn_obj.read()

print("Response: ")

try:
    for i in range(len(recv_data)):
        print("[" + str(i) + "] - " + str(hex(recv_data[i])), end=", ")
except Exception:
    pass

print()

p = proto_obj.unpack(recv_data)

print(proto_obj.strResult)

# time.sleep(10)
for i in sorted(p.keys()):
    for j in p[i].keys():
        print("\"" + j + "\" : ", end="")
        print(str(p[i][j]), end=", ")
    print()

conn_obj.disconnect()
