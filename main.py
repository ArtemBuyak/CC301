import GPRS_connection
import Protocol
import time
import sys


def main():
    conn = GPRS_connection.Connection('178.163.135.51', 10001)
    conn.connect()

    pr = Protocol.StrumenTS_05_07Protocol()
    #conn.send_data(pr.pack(0x00, pr.ARCHIVE_ALL_VALUE_HOUR, 0x01, 0x01, 0x01, 0x00))
    conn.send_data(pr.pack(0x00, pr.ARCHIVE_ALL_VALUE_HOUR, 0x01, 0x18, 0x0D, pr.ARCHIVE_ALL_CONTOUR_1))
    data = conn.receive_data()

    print("Response: ")
    try:
        for i in range(len(data)):
            print("[" + str(i) + "] - " + str(hex(data[i])), end=", ")
    except Exception:
        pass
    print()
    p = pr.unpack(data)
    print(pr.strResult)
    #time.sleep(10)
    for i in sorted(p.keys()):
        for j in p[i].keys():
            print("\"" + j + "\" : ", end= "")
            print(str(p[i][j]), end=", ")
        print()
    conn.close()

if __name__ == "__main__":
    main()


