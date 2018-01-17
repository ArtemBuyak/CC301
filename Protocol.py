from CRC import CRC
import struct


class CC301Protocol:

    def __init__(self):
        self.__buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__crc = CRC()
        self.__checkParam = 0
        self.__checkAddr = 0
        self.__strResult = ""
        self.__data = EnergyData()
        self.__time = Time()
        self.__Ke = 0  # weight coefficient
        self.__port = Port()


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

    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, port):
        self.__port = port

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
        self.crc.CRC16(self.buff, 6)

    def processing_data(self, inbuf):
        if self.checkAnswer(inbuf):
            # date current
            if inbuf[2] == 32:  # 0x20
                self.time.year = 2000 + inbuf[9]
                self.time.month = inbuf[8]
                self.time.day = inbuf[7]
                self.time.hour = inbuf[6]
                self.time.minute = inbuf[5]
                self.time.sec = inbuf[4]
                print("Year = %d, month = %d, day = %d, HH:MM:SS = %d:%d:%d" % (self.time.year, self.time.month, self.time.day, self.time.hour, self.time.minute, self.time.sec))

            # by the beginning of the day/month/year
            elif inbuf[2] == 42 or inbuf[2] == 43 or inbuf[2] == 44:  # 0x2A, 0x2B, 0x2C
                self.processingReadAnswer(inbuf)

            # for the day/month/year
            elif inbuf[2] == 2 or inbuf[2] == 3 or inbuf == 4:
                self.processingReadAnswer(inbuf)

            # for the sum value, average 3-min/15-min
            elif inbuf[2] == 1 or inbuf[2] == 5 or inbuf[2] == 6:
                self.processingReadAnswer(inbuf)

            # sres
            elif inbuf[2] == 36:  # 0x24
                list = self.processingBytes(inbuf)


            #GROUP CONST----------------------------------

            # identification device number
            elif inbuf[2] == 0:
                print(inbuf[4])  # - group
                print(inbuf[5])  # - code in group

            # device type
            elif inbuf[2] == 17: # 0x11
                print(self.fromBytesToStr(inbuf, 4, 4+17))

            # factor number
            elif inbuf[2] == 18:  # 0x12
                print(self.fromBytesToStr(inbuf, 4, 4+10))

            # release date
            elif inbuf[2] == 19:  # 0x13
                self.time.year = 2000 + inbuf[9]
                self.time.month = inbuf[8]
                self.time.day = inbuf[7]
                self.time.hour = inbuf[6]
                self.time.minute = inbuf[5]
                self.time.sec = inbuf[4]
                print("Year = %d, month = %d, day = %d, HH:MM:SS = %d:%d:%d" % (
                self.time.year, self.time.month, self.time.day, self.time.hour, self.time.minute, self.time.sec))

            # version and CRCprogramming
            elif inbuf[2] == 20:  # 0x14
                print(self.fromBytesToStr(inbuf, 4, 4+4))

            # network address
            elif inbuf[2] == 21:  # 0x15
                print(inbuf[4])

            # User ID
            elif inbuf[2] == 22:  # 0x16
                print(self.fromBytesToStr(inbuf, 4, 4+8))

            # port settings
            elif inbuf[2] == 23:  # 0x17
                byte_arr = bytearray(b'')
                byte_arr.append(inbuf[4])
                byte_arr.append(inbuf[5])
                self.port.baudrate = int.from_bytes(byte_arr, byteorder='big')
                self.port.type = inbuf[6]
                self.port.count = inbuf[7]
                self.port.parity = inbuf[8]
                self.port.stop = inbuf[9]

            # weight coefficient
            elif inbuf[2] == 24:  # 0x18
                byte_arr = bytearray(b'')
                byte_arr.append(inbuf[8])
                byte_arr.append(inbuf[9])
                self.Ke = int.from_bytes(byte_arr, byteorder='big')
                self.Ke = self.Ke/1000000.0

            #END GROUP CONST-----------------------------



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
        if not self.crc.CRC16(inbuf, (len(inbuf) - 2)):
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






class StrumenTS_05_07Protocol():


    def __init__(self):
        self.__buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__arch_buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__crc = CRC()
        self.__checkParam = 0
        self.__checkAddr = 0
        self.__strResult = ""
        self.__dataList = [WarmData(), WarmData(), WarmData(), WarmData()]
        self.__time = Time()
        self.__Ke = 0  # weight coefficient
        self.__port = Port()
        self.__counter = 0
        self.__contour = 0

    @property
    def contour(self):
        return self.__contour
    @contour.setter
    def contour(self, contour):
        self.__contour = contour

    @property
    def counter(self):
        return self.__counter
    @counter.setter
    def counter(self, counter):
        self.__counter = counter

    @property
    def buff(self):
        return self.__buff
    @buff.setter
    def buff(self, mass):
        self.__buff = mass

    @property
    def arch_buff(self):
        return self.__arch_buff
    @arch_buff.setter
    def arch_buff(self, arch_buff):
        self.__arch_buff = arch_buff

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
    def dataList(self):
        return self.__dataList
    @dataList.setter
    def dataList(self, dataList):
        self.__dataList = dataList

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

    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, port):
        self.__port = port

    # method create a message to meter for parametrs : 0 - 192
    def create_data_request(self, addr, parametr, offset, tariff, contour):
        self.buff[0] = addr  # байт сетевого адреса, на байты 0x00 и 0xFF отвечают все счетчики
        self.buff[1] = 0x03  # функция, для чтения нужно 3(4), на выбор, но в описании рекомендуют 3
        self.buff[2] = parametr
        self.buff[3] = offset
        self.buff[4] = tariff  # 0 - бестарифное значение, 1...8 - соответсвенные тарифы
        self.buff[5] = contour  # уточнение, пока что в первом приближении будет равно 0
        self.checkAddr = addr
        self.checkParam = parametr
        self.contour = contour
        self.crc.CRC16(self.buff, 6)
        return self.buff

    # for parametrs : 192 - 200
    def create_archive_request(self, addr,  parametr, P1, P2, P3, P4):
        self.arch_buff[0] = addr
        self.arch_buff[1] = 0x03
        self.arch_buff[2] = parametr
        self.arch_buff[3] = P1  # for hour archive : 1 - month, 2 - day, 3 - hour, 4 - contour
        self.arch_buff[4] = P2  # for day archive:   1 - month, 2 - day, 3 - reserve, 4 - contour
        self.arch_buff[5] = P3  # for month archive: 1 - year, 2 - month, 3 - reserve, 4 - contour
        self.arch_buff[6] = P4  # for year archive : 1 - year, 2 - reserve, 3 - reserve, 4 - contour
        self.checkAddr = addr
        self.checkParam = parametr
        self.contour = P4
        self.crc.CRC16(self.arch_buff, 7)
        return self.arch_buff

    def checkAnswer(self, inbuf):
        if not self.crc.CRC16(inbuf, (len(inbuf) - 2)):
            print("Not correct CRC")
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
        elif inbuf[3] == 8:
            self.strResult = "Несуществующая запись архива."
            return False
        elif inbuf[3] == 9:
            self.strResult = "Нет ответа от счетчика."
            return False


        if inbuf[0] != self.checkAddr:
            self.strResult = "Адрес в ответной посылке не соответствует адресу в запросе"
            return False
        if inbuf[1] == 0x03 or inbuf[1] == 0x04:
            pass
        else:
            self.strResult = "Номер команды в ответной посылке не соответствует номеру команды в запросе."
            return False
        if inbuf[2] != self.checkParam:
            self.strResult = "Номер параметра в ответной посылке не соответствует номеру параметра в запросе."
            return False
        return True

    def processing_data(self, inbuf):
        if self.checkAnswer(bytearray(inbuf)):
            # GROUP CONST -------------------------------------------

            # identification device number
            if inbuf[2] == 0:
                print(inbuf[4])     # - group
                print(inbuf[5])     # - code in group

            # device type
            elif inbuf[2] == 17:  # 0x11
                print(self.fromBytesToStr(inbuf, 4, 4 + 32))

            # factor number
            elif inbuf[2] == 18:  # 0x12
                print(self.fromBytesToStr(inbuf, 4, 4 + 8))

            # release date/ current time
            elif inbuf[2] == 19 or inbuf[2] == 32:  # 0x13 0x20
                self.time.year = 2000 + inbuf[9]
                self.time.month = inbuf[8]
                self.time.day = inbuf[7]
                self.time.hour = inbuf[6]
                self.time.minute = inbuf[5]
                self.time.sec = inbuf[4]
                print("Year = %d, month = %d, day = %d, HH:MM:SS = %d:%d:%d" % (self.time.year, self.time.month, self.time.day, self.time.hour, self.time.minute, self.time.sec))

            # program version
            elif inbuf[2] == 20:  # 0x14
                print(self.fromBytesToStr(inbuf, 4, 4 + 4))

            # network address
            elif inbuf[2] == 21:  # 0x15
                print(inbuf[4])

            # User ID
            elif inbuf[2] == 22:  # 0x16
                print(self.fromBytesToStr(inbuf, 4, 4 + 8))

            # port settings
            elif inbuf[2] == 23:  # 0x17
                byte_arr = bytearray(b'')
                byte_arr.append(inbuf[4])
                byte_arr.append(inbuf[5])
                self.port.baudrate = int.from_bytes(byte_arr, byteorder='big')
                self.port.type = inbuf[6]
                self.port.count = inbuf[7]
                self.port.parity = inbuf[8]
                self.port.stop = inbuf[9]
                print(self.port)

            # END GROUP CONST----------------------------------------

            # DATA ARCHIVE*******************************************

            # hour
            elif inbuf[2] == 192:  # 0xC0
                self.counter = 6
                test = self.contour_definition(inbuf)

                for i in sorted(test.keys()):
                    if (int(i) + 1) != self.contour and self.contour != 0:
                        continue
                    # Count of parameters depends on the type of contour
                    self.dataList[int(i)].type = test[i]
                    self.dataList[int(i)].number_of_contour = int(i)
                    if test[i] == 1:
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    elif test[i] == 2 or test[i] == 3 or test[i] == 4:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    elif test[i] == 5:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Q2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t3 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p3 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    print(self.dataList[int(i)])

            # day/month/year
            elif inbuf[2] == 193 or inbuf[2] == 194 or inbuf[2] == 195: # 0xC1, 0xC2, 0xC3
                self.counter = 6
                test = self.contour_definition(inbuf)

                for i in sorted(test.keys()):
                    if (int(i) + 1) != self.contour and self.contour != 0:
                        continue
                    # Count of parameters depends on the type of contour
                    self.dataList[int(i)].type = test[i]
                    self.dataList[int(i)].number_of_contour = int(i)
                    if test[i] == 1:
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    elif test[i] == 2 or test[i] == 3 or test[i] == 4:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    elif test[i] == 5:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Q2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                    print(self.dataList[int(i)])

            # END DATA ARCHIVE***************************************

            # CURRENT DATA-------------------------------------------

            elif inbuf[2] == 46: # 0x2E
                self.counter = 6
                test = self.contour_definition(inbuf)
                for i in sorted(test.keys()):
                    if (int(i) + 1) != self.contour and self.contour != 0:
                        continue
                    self.dataList[int(i)].number_of_contour = int(i)
                    self.dataList[int(i)].type = test[i]
                    if test[i] == 1:
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                        self.dataList[int(i)].Gv1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]

                    elif test[i] == 2 or test[i] == 3 or test[i] == 4:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t1 = struct. unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                        self.dataList[int(i)].Gv1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Gm1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].P1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]

                    elif test[i] == 5:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Q2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].V2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].M2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].t3 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].p3 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Tn = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Terr1 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr2 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr3 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Terr4 = int.from_bytes(self.automation_bytearray(inbuf, count=1), byteorder='big')
                        self.dataList[int(i)].Err = int.from_bytes(self.automation_bytearray(inbuf), byteorder='big')
                        self.dataList[int(i)].Act = int.from_bytes(self.automation_bytearray(inbuf, count=2), byteorder='big')
                        self.dataList[int(i)].Gv1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Gv2 =struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Gm1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].Gm2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].P1 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                        self.dataList[int(i)].P2 = struct.unpack('f', self.automation_bytearray(inbuf))[0]
                    print(self.dataList[int(i)])

            # END CURRENT DATA---------------------------------------

            # GROUP THERMAL ENERGY

            # sum/to the beginning of the day
            elif inbuf[2] == 1 or inbuf[2] == 42 or inbuf[2] == 43 or inbuf[2] == 44:  # 0x01, 0x0A, 0x0B, 0x0C
                test = self.contour_definition(inbuf)

                for i in test.keys():
                    self.dataList[int(i)].number_of_contour = int(i)
                    self.dataList[int(i)].type = test[i]
                    if test[i] == 1:
                        pass
                    elif test[i] == 2 or i == 3 or i == 4:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))
                    elif test[i] == 5:
                        self.dataList[int(i)].Q1 = struct.unpack('f', self.automation_bytearray(inbuf))
                        self.dataList[int(i)].Q2 = struct.unpack('f', self.automation_bytearray(inbuf))

            # END GROUP THERMAL ENERGY

            # CONFIGERATION

            elif inbuf[2] == 41:
                config = self.contour_definition(inbuf)
                for i in sorted(config.keys()):
                    print("Contour: %i, type: %i" % ((int(i)+1), config[i]))
            # END CONFIGERATION
            return self.dataList
        else:
            print(self.strResult)

    def contour_definition(self, inbuf):
        test = {}
        if inbuf[4] >> 4:
            test["1"] = inbuf[4] >> 4
        if inbuf[4] & 0x0f:
            test["0"] = inbuf[4] & 0x0f
        if inbuf[5] >> 4:
            test["3"] = inbuf[4] >> 4
        if inbuf[5] & 0x0f:
            test["2"] = inbuf[4] & 0x0f
        return test

    def automation_bytearray(self, inbuf, count=4):
        byte_arr = bytearray(b'')
        for i in range(count):
            byte_arr.append(inbuf[self.counter])  # 4
            self.counter += 1  # 5
        return byte_arr


    def fromBytesToStr(self, inbuf, start, end):
        byte_arr = bytearray(b'')
        for i in range(start, end):
            byte_arr.append(inbuf[i])
        return bytes.decode(bytes(byte_arr), "ascii")


class Port:
    def __init__(self, baudrate = 0, type = 0, count = 0, parity = 0, stop = 0):
        self.__baudrate = baudrate
        self.__type = type
        self.__count = count
        self.__parity = parity
        self.__stop = stop

    @property
    def baudrate(self):
        return self.__baudrate
    @baudrate.setter
    def baudrate(self, baudrate):
        self.__baudrate = baudrate

    @property
    def type(self):
        return self.__type
    @type.setter
    def type(self, type):
        self.__type = type

    @property
    def count(self):
        return self.__count
    @count.setter
    def count(self, count):
        self.___count = count

    @property
    def parity(self):
        return self.__parity
    @parity.setter
    def parity(self, parity):
        self.__parity = parity

    @property
    def stop(self):
        return self.__stop
    @stop.setter
    def stop(self, stop):
        self.__stop = stop

    def __str__(self):
        return "Baudrate = %i, type = %i, count = %i, parity = %i, stop = %i." % (self.baudrate, self.type, self.count, self.parity, self.stop)

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
        self.__hour = hour

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



class EnergyData:
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

    def __str__(self):
        return "A+ = %f, A- = %f, R+ = %f, R- = %f" % (self.a_plus, self.a_minus, self.r_plus, self.r_minus)

class WarmData:
    def __init__(self,number_of_contour=-1, type=-1, Q1=-1, Q2=-1, V1=-1, V2=-1, M1=-1, M2=-1, t1=-1, t2=-1, t3=-1, p1=-1, p2=-1, p3=-1, Tn=-1, Terr=-1,Terr1=-1, Terr2=-1, Terr3=-1, Terr4=-1, Err=-1, Act=-1, Gv1 =-1, Gv2=-1, Gm1=-1, Gm2=-1, P1=-1, P2=-1):
        self.__number_of_contour = number_of_contour
        self.__type = type
        self.__Q1 = Q1  # Накопленная тепловая энергия в прямом трубопроводе
        self.__Q2 = Q2  # Накопленная тепловая энергия в обратном трубопроводе
        self.__V1 = V1  # Накопленный объём теплоносителя в прямом трубопроводе
        self.__V2 = V2  # Накопленный объём теплоносителя в обратном трубопроводе
        self.__M1 = M1  # Масса теплоносителя в прямом трубопроводе
        self.__M2 = M2  # Масса теплоносителя в обратном трубопроводе
        self.__t1 = t1  # Температура в прямом трубопроводе
        self.__t2 = t2  # Температура в обратном трубопроводе
        self.__t3 = t3  # Температура холодной воды
        self.__p1 = p1  # Давление в прямом трубопроводе
        self.__p2 = p2  # Давление в обратном трубопроводе
        self.__p3 = p3  # Давление в трубопроводе холодной воды
        self.__Tn = Tn  # Общее время наработки прибора
        self.__Terr = Terr  # Время работы контура с ошибкой
        self.__Terr1 = Terr1  # Время ошибки при G < Gmin
        self.__Terr2 = Terr2  # Время ошибки при G > Gmax
        self.__Terr3 = Terr3  # Время ошибки при dt < dtmin
        self.__Terr4 = Terr4  # Время техниеской неисправности
        self.__Err = Err  # Текущие неисправности
        self.__Act = Act  # Воздействия на прибор и предупреждения
        self.__Gv1 = Gv1  # Объёмный расход теплоносителя в прямом трубопроводе
        self.__Gv2 = Gv2  # Объёмный расход теплоносителя в обратном трубопроводе
        self.__Gm1 = Gm1  # Массовый расход теплоносителя в прямом трубопроводе
        self.__Gm2 = Gm2  # Массовый расход теплоносителя в обратном трубопровоед
        self.__P1 = P1  # Тепловая мощность в прямом трубопроводе
        self.__P2 = P2  # Тепловая мощность в обратном трубопроводе

    @property
    def number_of_contour(self):
        return self.__number_of_contour
    @number_of_contour.setter
    def number_of_contour(self, number_of_contour):
        self.__number_of_contour = number_of_contour

    @property
    def type(self):
        return self.__type
    @type.setter
    def type(self, type):
        self.__type = type

    @property
    def Q1(self):
        return self.__Q1
    @Q1.setter
    def Q1(self, Q1):
        self.__Q1 = Q1

    @property
    def Q2(self):
        return self.__Q2
    @Q2.setter
    def Q2(self, Q2):
        self.__Q2 = Q2

    @property
    def M1(self):
        return self.__M1
    @M1.setter
    def M1(self, M1):
        self.__M1 = M1

    @property
    def M2(self):
        return self.__M2
    @M2.setter
    def M2(self, M2):
        self.__M2 = M2

    @property
    def V1(self):
        return self.__V1

    @V1.setter
    def V1(self, V1):
        self.__V1 = V1

    @property
    def V2(self):
        return self.__V2
    @V2.setter
    def V2(self, V2):
        self.__V2 = V2

    @property
    def t1(self):
        return self.__t1
    @t1.setter
    def t1(self, t1):
        self.__t1 = t1

    @property
    def t2(self):
        return self.__t2
    @t2.setter
    def t2(self, t2):
        self.__t2 = t2

    @property
    def t3(self):
        return self.__t3
    @t3.setter
    def t3(self, t3):
        self.__t3 = t3

    @property
    def p1(self):
        return self.__p1
    @p1.setter
    def p1(self, p1):
        self.__p1 = p1

    @property
    def p2(self):
        return self.__p2
    @p2.setter
    def p2(self, p2):
        self.__p2 = p2

    @property
    def p3(self):
        return self.__p3
    @p3.setter
    def p3(self, p3):
        self.__p3 = p3

    @property
    def Tn(self):
        return self.__Tn
    @Tn.setter
    def Tn(self, Tn):
        self.__Tn = Tn

    @property
    def Terr(self):
        return self.__Terr
    @Terr.setter
    def Terr(self, Terr):
        self.__Terr = Terr

    @property
    def Terr1(self):
        return self.__Terr1
    @Terr1.setter
    def Terr1(self, Terr1):
        self.__Terr1 = Terr1

    @property
    def Terr2(self):
        return self.__Terr2
    @Terr2.setter
    def Terr2(self, Terr2):
        self.__Terr2 = Terr2

    @property
    def Terr3(self):
        return self.__Terr3
    @Terr3.setter
    def Terr3(self, Terr3):
        self.__Terr3 = Terr3

    @property
    def Terr4(self):
        return self.__Terr4
    @Terr4.setter
    def Terr4(self, Terr4):
        self.__Terr4 = Terr4

    @property
    def Err(self):
        return self.__Err
    @Err.setter
    def Err(self, Err):
        self.__Err = Err

    @property
    def Act(self):
        return self.__Act
    @Act.setter
    def Act(self, Act):
        self.__Act = Act

    @property
    def Gv1(self):
        return self.__Gv1
    @Gv1.setter
    def Gv1(self, Gv1):
        self.__Gv1 = Gv1

    @property
    def Gv2(self):
        return self.__Gv2
    @Gv2.setter
    def Gv2(self, Gv2):
        self.__Gv2 = Gv2

    @property
    def Gm1(self):
        return self.__Gm1
    @Gm1.setter
    def Gm1(self, Gm1):
        self.__Gm1 = Gm1

    @property
    def Gm2(self):
        return self.__Gm2
    @Gm2.setter
    def Gm2(self, Gm2):
        self.__Gm2 = Gm2

    @property
    def P1(self):
        return self.__P1
    @P1.setter
    def P1(self, P1):
        self.__P1 = P1

    @property
    def P2(self):
        return self.__P2
    @P2.setter
    def P2(self, P2):
        self.__P2 = P2

    def __str__(self):
        return "Type of system %i  Q1 = %.3f, Q2 = %.3f, V1 = %.3f, V2 = %.3f, M1 = %.3f, M2 = %.3f, t1 = %.3f, t2 = %.3f, t3 = %.3f, p1 = %.3f, p2 = %.3f, p3 = %.3f." \
               % (self.type, self.Q1, self.Q2, self.V1, self.V2, self.M1, self.M2, self.t1, self.t2, self.t3, self.p1, self.p2, self.p3)