import GPRS_connection
import Protocol

conn = GPRS_connection.Connection('178.163.135.51', 10001)
pr = Protocol.StrumenTS_05_07Protocol()
conn.connect()
#conn.send_data(bytes(pr.create_data_request(0x00, 0x00, 0x00, 0x00, 0x00)))
#conn.send_data(bytes(pr.create_archive_request(0x00, 0xC0, 0x01, 0x12, 0x0A, 0x01)))
conn.send_data(bytes(pr.create_archive_request(0x00, 0xC4, 0x01, 0x01, 0x00, 0x01)))
data = conn.receive_data()
print("Answer:")
for i in range(len(data)):
    print("[" + str(i) + "] --- " + str(hex(data[i])), end=", ")
print()
pr.processing_data(data)
conn.close()