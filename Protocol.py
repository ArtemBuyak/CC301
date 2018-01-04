from CRC import CRC
import struct


class CC301Protocol:

    def __init__(self):
        self.__buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__crc = CRC()
        self.__checkParam = 0
        self.__checkAddr = 0
        self.__strResult = ""
        self.__data = Data()
        self.__time = Time()
        self.__Ke = 0  # weight coefficient


    @property
    def buff(self):
        return self.__buff
    @buff.setter
    def buff(self, mass):
        self.__buff = mass

    @property
    def crc(self):
        return self.__crc
    @crc.setter
    def crc(self, crc):
        self.__crc = crc

    @property
    def checkParam(self):
        return self.__checkParam
    @checkParam.setter
    def checkParam(self, checkparam):
        self.__checkParam = checkparam

    @property
    def checkAddr(self):
        return self.__checkAddr
    @checkAddr.setter
    def checkAddr(self, checkaddr):
        self.__checkAddr = checkaddr

    @property
    def strResult(self):
        return self.__strResult
    @strResult.setter
    def strResult(self, strResult):
        self.__strResult = strResult

    @property
    def data(self):
        return self.__data
    @data.setter
    def data(self, data):
        self.__data = data

    @property
    def time(self):
        return self.__time
    @time.setter
    def time(self, time):
        self.__time = time

    @property
    def Ke(self):
        return self.__Ke
    @Ke.setter
    def Ke(self, Ke):
        self.__Ke = Ke

    # method create a message to meter
    def create_data_request(self, addr, parametr, offset, tariff):
        self.buff[0] = addr # байт сетевого адреса, на байты 0x00 и 0xFF отвечают все счетчики
        self.buff[1] = 0x03 # функция, для чтения нужно 3(4), на выбор, но в описании рекомендуют 3
        self.buff[2] = parametr
        self.buff[3] = offset
        self.buff[4] = tariff # 0 - бестарифное значение, 1...8 - соответсвенные тарифы
        self.buff[5] = 0x00   # уточнение, пока что в первом приближении будет равно 0
        self.checkAddr = addr
        self.checkParam = parametr
        self.data.tariff = tariff
        self.crc.CRC8(self.buff, 6)

    def process_cc301_data(self, inbuf):
        if self.checkAnswer(inbuf):
            # date current/ release date
            if inbuf[2] == 32 or inbuf[2] == 19:
                self.time.year = 2000 + inbuf[9]
                self.time.month = inbuf[8]
                self.time.day = inbuf[7]
                self.time.hour = inbuf[6]
                self.time.minute = inbuf[5]
                self.time.sec = inbuf[4]
                print("Year = %d, month = %d, day = %d, HH:MM:SS = %d:%d:%d" % (self.time.year, self.time.month, self.time.day, self.time.hour, self.time.minute, self.time.sec))

            # by the beginning of the day/month/year
            elif inbuf[2] == 42 or inbuf[2] == 43 or inbuf[2] == 44:
                self.processingReadAnswer(inbuf)

            # for the day/month/year
            elif inbuf[2] == 2 or inbuf[2] == 3 or inbuf == 4:
                self.processingReadAnswer(inbuf)

            # for the sum value, average 3-min/15-min
            elif inbuf[2] == 1 or inbuf[2] == 5 or inbuf[2] == 6:
                self.processingReadAnswer(inbuf)

            # identification device number
            elif inbuf[2] == 0:
                print(inbuf[4])     # - group
                print(inbuf[5])     # - code in group

            # network address
            elif inbuf[2] == 21:
                print(inbuf[4])

            # device type
            elif inbuf[2] == 17:
                print(self.fromBytesToStr(inbuf, 4, 4+17))

            # factor number
            elif inbuf[2] == 18:
                print(self.fromBytesToStr(inbuf, 4, 4+10))

            # version and CRCprogramming
            elif inbuf[2] == 20:
                print(self.fromBytesToStr(inbuf, 4, 4+4))

            # User ID
            elif inbuf[2] == 22:
                print(self.fromBytesToStr(inbuf, 4, 4+8))

            # weight coefficient
            elif inbuf[2] == 24:
                byte_arr = bytearray(b'')
                byte_arr.append(inbuf[8])
                byte_arr.append(inbuf[9])
                self.Ke = int.from_bytes(byte_arr, byteorder='big')
                self.Ke = self.Ke/1000000.0

            # sres
            elif inbuf[2] == 36:
                list = self.processingBytes(inbuf)



    def fromBytesToStr(self, inbuf, start, end):
        byte_arr = bytearray(b'')
        for i in range(start, end):
            byte_arr.append(inbuf[i])
        return bytes.decode(bytes(byte_arr), "ascii")

    #processing answer and save in struct Data()
    def processingReadAnswer(self, inbuf):
        byte_arr = bytearray(b'')
        byte_arr.append(inbuf[4])
        byte_arr.append(inbuf[5])
        byte_arr.append(inbuf[6])
        byte_arr.append(inbuf[7])
        self.data.a_plus = struct.unpack('f', byte_arr)
        byte_arr[0] = inbuf[8]
        byte_arr[1] = inbuf[9]
        byte_arr[2] = inbuf[10]
        byte_arr[3] = inbuf[11]
        self.data.a_minus = struct.unpack('f', byte_arr)
        byte_arr[0] = inbuf[12]
        byte_arr[1] = inbuf[13]
        byte_arr[2] = inbuf[14]
        byte_arr[3] = inbuf[15]
        self.data.r_plus = struct.unpack('f', byte_arr)
        byte_arr[0] = inbuf[12]
        byte_arr[1] = inbuf[13]
        byte_arr[2] = inbuf[14]
        byte_arr[3] = inbuf[15]
        self.data.r_minus = struct.unpack('f', byte_arr)

    # for sres
    def processingBytes(self, inbuf):
        list = [self.data.a_plus, self.data.a_minus, self.data.r_plus, self.data.r_minus]
        byte_arr = bytearray(b'')
        for i in range(4):
            byte_arr.append(inbuf[4 + i*2])
            byte_arr.append(inbuf[5 + i*2])
            list[i] = int.from_bytes(byte_arr, byteorder='big')
        return list

    # method check correct answer or not, return bool
    def checkAnswer(self, inbuf):
        if not self.crc.CRC8(inbuf, (len(inbuf) - 2)):
            return False

        if inbuf[3] == 0:
            self.strResult = "OK"
        elif inbuf[3] == 1:
            self.strResult = "Неизвестная ошибка."
            return False
        elif inbuf[3] == 2:
            self.strResult = "Неизвестный параметр."
            return False
        elif inbuf[3] == 3:
            self.strResult = "Ошибочный аргумент."
            return False
        elif inbuf[3] == 4:
            self.strResult = "Несанкционированный доступ."
            return False
        elif inbuf[3] == 5:
            self.strResult = "Блок поврежден."
            return False
        elif inbuf[3] == 6:
            self.strResult = "Ошибка памяти."
            return False
        elif inbuf[3] == 7:
            self.strResult = "Счетчик занят."
            return False


        if inbuf[0] != self.checkAddr:
            self.strResult = "Адрес в ответной посылке не соответствует адресу в запросе"
            return False
        if inbuf[1] != 0x03 or inbuf[1] != 0x04:
            self.strResult = "Номер команды в ответной посылке не соответствует номеру команды в запросе."
            return False
        if inbuf[2] != self.checkParam:
            self.strResult = "Номер параметра в ответной посылке не соответствует номеру параметра в запросе."
            return False

        return True

class Time:
    def __init__(self, year=0 , month=0, day=0, hour=0, minute=0, sec=0):
        self.__year = year
        self.__month = month
        self.__day = day
        self.__hour = hour
        self.__minute = minute
        self.__sec = sec

    @property
    def year(self):
        return self.__year
    @year.setter
    def year(self, year):
        self.__year = year

    @property
    def month(self):
        return self.__month
    @month.setter
    def month(self, month):
        self.__month = month

    @property
    def day(self):
        return self.__day
    @day.setter
    def day(self, day):
        self.__day = day

    @property
    def hour(self):
        return self.__hour
    @hour.setter
    def hour(self, hour):
        self.hour = hour

    @property
    def minute(self):
        return self.__minute
    @minute.setter
    def minute(self, minute):
        self.__minute = minute

    @property
    def sec(self):
        return self.__sec
    @sec.setter
    def sec(self, sec):
        self.__sec = sec

class Data:
    def __init__(self, a_plus=0, a_minus=0, r_plus=0, r_minus=0, tariff = 0):
        self.__a_plus = a_plus
        self.__a_minus = a_minus
        self.__r_plus = r_plus
        self.__r_minus = r_minus
        self.__tariff = tariff

    @property
    def tariff(self):
        return self.tariff
    @tariff.setter
    def tariff(self, tariff):
        self.__tariff = tariff

    @property
    def a_plus(self):
        return self.__a_plus
    @a_plus.setter
    def a_plus(self, a_plus):
        self.__a_plus = a_plus

    @property
    def a_minus(self):
        return self.__a_minus
    @a_minus.setter
    def a_minus(self, a_minus):
        self.__a_minus = a_minus

    @property
    def r_plus(self):
        return self.__r_plus
    @r_plus.setter
    def r_plus(self, r_plus):
        self.__r_plus = r_plus

    @property
    def r_minus(self):
        return self.__r_minus
    @r_minus.setter
    def r_minus(self, r_minus):
        self.__r_minus = r_minus
