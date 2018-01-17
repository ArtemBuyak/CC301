import GPRS_connection
import Protocol

conn = GPRS_connection.Connection('178.163.135.51', 10001)
pr = Protocol.StrumenTS_05_07Protocol()
conn.connect()
conn.send_data(bytes(pr.create_data_request(0x00, 0x29, 0x00, 0x00, 0x00)))
data = conn.receive_data()
#for i in range(len(data)):
#    print("[" + str(i) + "] - " + str(hex(data[i])), end=", ")
pr.processing_data(data)
conn.close()
