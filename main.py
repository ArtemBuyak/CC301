import GPRS_connection
import Protocol

conn = GPRS_connection.Connection('178.163.135.51', 10001)
pr = Protocol.StrumenTS_05_07Protocol()
conn.connect()
#conn.send_data(bytes(pr.create_data_request(0x00, 0x00, 0x00, 0x00, 0x00)))
#conn.send_data(bytes(pr.create_archive_request(0x00, 0xC1, 0x01, 0x12, 0x00, 0x02)))
conn.send_data(bytes(pr.create_archive_request(0x00, 0xC5, 0x00, 0x07, 0x00, 0x02)))
data = conn.receive_data()
pr.processing_data(data)
conn.close()