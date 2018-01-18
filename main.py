import GPRS_connection
import Protocol

conn = GPRS_connection.Connection('178.163.135.51', 10001)
pr = Protocol.StrumenTS_05_07Protocol()
conn.connect()
list = [0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09]
#for i in list:
#conn.send_data(bytes(pr.create_data_request(0x00, 0x00, 0x00, 0x00, 0x00)))
conn.send_data(bytes(pr.create_archive_request(0x00, 0xC0, 0x01, 0x12, 0x01, 0x00)))
#conn.send_data(bytes(pr.create_archive_request(0x00, 0xC4, 0x00, 0x01, 0x00, 0x01)))
data = conn.receive_data()
p = pr.processing_data(data)
for i in p:
    print(i)
conn.close()