import GPRS_connection
import Protocol

conn = GPRS_connection.Connection('178.163.135.151', 10001)
pr = Protocol.StrumenTS_05_07Protocol()
conn.connect()
conn.send_data(bytes(pr.create_data_request(0x00, 0x2e, 0x00, 0x00, 0x00)))
data = conn.receive_data()
pr.processing_data(data)
conn.close()
