from CRC import CRC


class CC301Protocol:

    def __init__(self):
        self.__buff = []
        self.__crc = CRC
        self.__checkParam = 0
        self.__checkAddr = 0

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


    # method create a message to meter
    def create_data_request(self, addr, parametr, offset, tariff, refinement):
        self.buff[0] = addr # байт сетевого адреса, на байты 0x00 и 0xFF отвечают все счетчики
        self.buff[1] = 0x03 # функция, для чтения нужно 3(4), на выбор, но в описании рекомендуют 3
        self.buff[2] = parametr
        self.buff[3] = offset
        self.buff[4] = tariff # 0 - бестарифное значение, 1...8 - соответсвенные тарифы
        self.buff[5] = 0x00   # уточнение, пока что в первом приближении будет равно 0
        self.crc.CRC8(self.buff, 6)

    def process_cc301_data(self, inbuf):
        # проверка адреса, результата, комманды и номера
        if (inbuf[0] != self.checkAddr) or (inbuf[3] != 0) or (inbuf[1] != 0x03) or (inbuf[2] != self.checkParam):
            print("Not correct answer")
            return None

        if inbuf[2] == 0x32:
            time = Time()
            time.year = 2000 + inbuf[9]
            time.month = inbuf[8]
            time.day = inbuf[7]
            time.hour = inbuf[6]
            time.minute = inbuf[5]
            time.sec = inbuf[4]
            print("Year = %d, month = %d, day = %d, HH:MM:SS = %d:%d:%d" % (time.year, time.month, time.day, time.hour, time.minute, time.sec))

        if inbuf[2] == 0x43:





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
    def __init__(self, year=0 , month=0, day=0, hour=0, min=0, sec=0):
        self.



