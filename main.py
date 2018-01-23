import GPRS_connection
import Protocol
import time
import sys


def main():
    conn = GPRS_connection.Connection('178.163.135.151', 10001)
    conn.connect()

    pr = Protocol.StrumenTS_05_07Protocol()
    conn.send_data(pr.pack(0x00, pr.CURRENT_DATA_VALUE, 0x00, 0x00, 0x00, 0x00))
    data = conn.receive_data()
    print("Response: ")
    #try:
    #    for i in range(len(data)):
    #        print("[" + str(i) + "] - " + str(hex(data[i])), end=", ")
    #except Exception:
    #    pass
    #print()
    pr.unpack(data)
    time.sleep(10)

    conn.close()

if __name__ == "__main__":
    main()


