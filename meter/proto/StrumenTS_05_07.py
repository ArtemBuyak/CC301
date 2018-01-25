import struct
from collections import OrderedDict

from meter import crc
from meter.crc import CRC16_C0C1


class StrumenTS_05_07():

    """

    Реализация протокола ТЕПЛОСЧЁТЧИКИ «СТРУМЕНЬ ТС-05», «СТРУМЕНЬ ТС-07»

    Блок констант:

    --------------------------------------------------------------------------------
    METER_CONTOUR_1   - первый контур
    METER_CONTOUR_2   - второй
    METER_CONTOUR_3   - третий
    METER_CONTOUR_4   - четвертый

    ARCHIVE_ALL_CONTOUR_1 - контур 1 для запроса всех параметров
    ARCHIVE_ALL_CONTOUR_2 = контур 2
    ARCHIVE_ALL_CONTOUR_3 = контур 3
    ARCHIVE_ALL_CONTOUR_4 = контур 4

    Значений параметров для считывания:
    ID                - идентификационный номер устройства. Вызов (ADDR- адрес устр-ва, obj.ID, P1 - 0x00, P2 - 0x00, P3 - 0x00, P4 - 0x00).
    DEVICE_TYPE       - тип прибора. Вызов аналогично ID.
    FACTOR_NUMBER     - заводской номер. -//-.
    RELEASE_DATE      - дата выпуска прибора. -//-.
    CURRENT_DATE_TIME - текущее время и число. -//-.
    PROGRAM_VERSION   - версия программы. Вызов -//-.
    NETWORK_ADDRESS   - сетевой адрес прибора. -//-.
    USER_ID           - идентификатор пользователя. -//-.
    PORT_SETTINGS     - конфигурация порта связи. -//-.
    CONFIGURATION     - конфигурация теплосчётчика. -//-

    ARCHIVE_ALL_VALUE_HOUR       - часовой архив(возвратит все значения данных).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_ALL_VALUE_HOUR, P1 - месяц, P2 - день, P3 - час, P4 - ARCHIVE_ALL_CONTOUR_1(для 1 контура и т.д.))

    ARCHIVE_ALL_VALUE_DAY        - суточный архив(все значения).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_ALL_VAlUE_DAY, P1 - месяц, P2 - день, P3 - 0x00, P4 - ARCHIVE_ALL_CONTOUR_1(для 1 контура и т.д.))

    ARCHIVE_ALL_VALUE_MONTH      - месячный архив(все значения).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_ALL_VAlUE_MONTH, P1 - год, P2 - месяц, P3- 0x00, P4 - ARCHIVE_ALL_CONTOUR_1(для 1 контура и т.д.))

    ARCHIVE_ALL_VALUE_YEAR       - годовой архив(все значения).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_ALL_VAlUE_YEAR, P1 - год, P2 - 0x00, P3 - 0x00, P4 - ARCHIVE_ALL_CONTOUR_1(для 1 контура и т.д.))

    ARCHIVE_SPECIFIC_VALUE_HOUR  - часовой архив(по маске).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_SPECIFIC_VALUE_HOUR, P1 - смещение(0...255), P2 - элумент записи(значение этого поля из таблицы Б4 в описании протокола), P4 - METER_CONTOUR_1(и т.д.))

    ARCHIVE_SPECIFIC_VALUE_DAY   - часовой архив(по маске).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_SPECIFIC_VALUE_DAY, P1 - смещение(0...63), P2 - аналогично часовому архиву(по маске), P4 - METER_CONTOUR_1(и т.д.))

    ARCHIVE_SPECIFIC_VALUE_MONTH - месячный архив(по маске).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_SPECIFIC_VALUE_MONTH, P1 - смещение(0...15), P2 - аналогично часовому архиву(по маске), P4 - METER_CONTOUR_1(и т.д.))

    ARCHIVE_SPECIFIC_VALUE_YEAR  - годовой архив(по маске).
                        Вызов obj.pack(ADDR, obj.ARCHIVE_SPECIFIC_VALUE_YEAR, P1 - смещение(0...15), P2 - аналогично часовому архиву(по маске), P4 - METER_CONTOUR_1(и т.д.))

    CURRENT_DATA_VALUE - все текущие значения.
                        Вызов obj.pack(ADDR, obj.CURRENT_DATA_VALUE, P1 - 0x00, P2 - 0x00, P3 - METER_CONTOUR_1(либо другой контур, в случае 0x00 - значение по всем контурам), P4 - 0x00)

    SUM_HEAT           - суммарная накопленная тепловая энергия
                        Вызов obj.pack(ADDR, obj.SUM_HEAT, P1 - 0x00, P2 - 0x00, P3 - аналогично CURRENT_DATA_VAlUE, P4 - 0x00)

    SUM_HEAT_DAY_BEGIN - накопленная энергия на начало суток
                        Вызов obj.pack(ADDR, obj.SUM_HEAT_DAY_BEGIN, P1 - смещение(0...63), P2 - 0x00, P3 - аналогично CURRENT_DATA_VAlUE, P4 - 0x00)

    SUM_HEAT_MONTH_BEGIN - накопленная энергия на начало месяца
                         Вызов obj.pack(ADDR, obj.SUM_HEAT_MONTH_BEGIN, P1 - (0...15), P2 - 0x00, P3 - аналогично CURRENT_DATA_VAlUE, P4 - 0x00)

    SUM_HEAT_YEAR_BEGIN  - накопленная энрегия на начало года
                        Bызов obj.pack(ADDR, obj.SUM_HEAT_YEAR_BEGIN, P1 - (0...15), P2 - 0x00, P3 - аналогично CURRENT_DATA_VAlUE, P4 - 0x00)
    --------------------------------------------------------------------------------


    Перечень параметров теплосчетчика:
        contour  # Номер контура данных(1...4)
        type  # Тип контура данных(1...5)
        Q1  # Накопленная тепловая энергия в прямом трубопроводе
        Q2  # Накопленная тепловая энергия в обратном трубопроводе
        V1  # Накопленный объём теплоносителя в прямом трубопроводе
        V2  # Накопленный объём теплоносителя в обратном трубопроводе
        M1  # Масса теплоносителя в прямом трубопроводе
        M2  # Масса теплоносителя в обратном трубопроводе
        t1  # Температура в прямом трубопроводе
        t2  # Температура в обратном трубопроводе
        t3  # Температура холодной воды
        p1  # Давление в прямом трубопроводе
        p2  # Давление в обратном трубопроводе
        p3  # Давление в трубопроводе холодной воды
        Tn  # Общее время наработки прибора
        Terr  # Время работы контура с ошибкой
        Terr1  # Время ошибки при G < Gmin
        Terr2  # Время ошибки при G > Gmax
        Terr3  # Время ошибки при dt < dtmin
        Terr4  # Время техниеской неисправности
        Err  # Текущие неисправности
        Act  # Воздействия на прибор и предупреждения
        Gv1  # Объёмный расход теплоносителя в прямом трубопроводе
        Gv2  # Объёмный расход теплоносителя в обратном трубопроводе
        Gm1  # Массовый расход теплоносителя в прямом трубопроводе
        Gm2  # Массовый расход теплоносителя в обратном трубопровоед
        P1  # Тепловая мощность в прямом трубопроводе
        P2  # Тепловая мощность в обратном трубопроводе

    """


    def __init__(self):
        self.__buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__arch_buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__crc = crc
        self.__checkParam = 0
        self.__checkAddr = 0
        self.__strResult = ""
        self.__Ke = 0  # weight coefficient
        self.__counter = 0
        self.__contour = 0

    val = CRC16_C0C1.check("")

    #  Констант блок
    METER_CONTOUR_1 = 1
    METER_CONTOUR_2 = 2
    METER_CONTOUR_3 = 3
    METER_CONTOUR_4 = 4
    ARCHIVE_ALL_CONTOUR_1 = 0x01
    ARCHIVE_ALL_CONTOUR_2 = 0x02
    ARCHIVE_ALL_CONTOUR_3 = 0x04
    ARCHIVE_ALL_CONTOUR_4 = 0x08
    ID = 0
    DEVICE_TYPE = 17
    FACTOR_NUMBER = 18
    RELEASE_DATE = 19
    CURRENT_DATE_TIME = 32
    PROGRAM_VERSION = 20
    NETWORK_ADDRESS = 21
    USER_ID = 22
    PORT_SETTINGS = 23
    ARCHIVE_ALL_VALUE_HOUR = 192
    ARCHIVE_ALL_VALUE_DAY = 193
    ARCHIVE_ALL_VALUE_MONTH = 194
    ARCHIVE_ALL_VALUE_YEAR = 195
    ARCHIVE_SPECIFIC_VALUE_HOUR = 196
    ARCHIVE_SPECIFIC_VALUE_DAY = 197
    ARCHIVE_SPECIFIC_VALUE_MONTH = 198
    ARCHIVE_SPECIFIC_VALUE_YEAR = 199
    CURRENT_DATA_VALUE = 46
    SUM_HEAT = 1
    SUM_HEAT_DAY_BEGIN = 42
    SUM_HEAT_MONTH_BEGIN = 43
    SUM_HEAT_YEAR_BEGIN = 44
    CONFIGURATION = 41

    # Ошибки
    GENERAL_EXCEPTION = 0
    INDEX_OUT_OF_RANGE = 1
    NOT_CORRECT_CRC = 2

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

    def pack(self, addr, parametr, P1, P2, P3, P4):

        if parametr > 191 and parametr < 200:
            return self.create_archive_request(addr, parametr, P1, P2, P3, P4)
        else:
            return self.create_data_request(addr, parametr, P1, P2, P3)


    # method create a message to meter for parametrs : 0 - 192
    def create_data_request(self, addr, parametr, offset, tariff, contour):

        """

        Метод вернет 0, в случае возникновения ошибки при формировании посылки

        """

        # ошибка возврата, если переданы значения больше максимального значения для byte
        if addr > 255 or parametr > 255 or offset > 255 or tariff > 255 or contour > 255:
            return 0

        self.buff[0] = addr  # байт сетевого адреса, на байты 0x00 и 0xFF отвечают все счетчики
        self.buff[1] = 0x03  # функция, для чтения нужно 3(4), на выбор, но в описании рекомендуют 3
        self.buff[2] = parametr
        self.buff[3] = offset
        self.buff[4] = tariff  # 0 - бестарифное значение, 1...8 - соответсвенные тарифы
        self.buff[5] = contour  # уточнение, пока что в первом приближении будет равно 0
        self.checkAddr = addr
        self.checkParam = parametr
        self.contour = contour
        self.crc.CRC16_C0C1.check(self.buff, 6)
        #print("Request: ")
        #for i in range(len(self.buff)):
        #    print(str(i) + " - " + str(hex(self.buff[i])), end=", ")
        #print()
        return bytes(self.buff)

    # for parametrs : 192 - 200
    def create_archive_request(self, addr,  parametr, P1, P2, P3, P4):

        """

        Метод вернет 0, в случае возникновения ошибки при формировании посылки

        """

        # ошибка возврата, если переданы значения больше максимального значения для byte
        if addr > 255 or parametr > 255 or P1 > 255 or P2 > 255 or P3 > 255 or P4 > 255:
            return 0

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
        self.crc.CRC16_C0C1.check(self.arch_buff, 7)
        #print("Request: ")
        #for i in range(len(self.arch_buff)):
        #    print("[" + str(i) + "] - " + str(hex(self.arch_buff[i])), end=", ")
        #print()
        return bytes(self.arch_buff)

    def checkAnswer(self, inbuf):

        """

        Вернет True, если входящая посылка соответствует протоколу, в остальных случаях - False.
        В переменную strResult будет записано описание несоответсвия с протоколом.

        """

        if not self.crc.CRC16_C0C1.check(inbuf, (len(inbuf) - 2)):
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

    def unpack(self, inbuf):

        """

        Метод обработки входящей от счетчика посылки. В зависимости от байта параметра вызывается определенный case обработки.
        Возвращает 1, в случае возникновения ошибки индекса, в случае других ошибок вернется 0.

        """

        dataDict = OrderedDict()
        if self.checkAnswer(bytearray(inbuf)):
            # GROUP CONST -------------------------------------------

            # identification device number
            if inbuf[2] == self.ID:
                result = "Идентификационный номер устройства: "
                if len(str(inbuf[5])) == 1:
                    result += "0" + str(inbuf[5])
                else:
                    result += str(inbuf[5])
                if len(str(inbuf[4])) == 1:
                    result += "0" + str(inbuf[4])
                else:
                    result += str(inbuf[4])
                return result

            # device type
            elif inbuf[2] == self.DEVICE_TYPE:  # 0x11
                return self._fromBytesToStr(inbuf, 4, 4 + 32)

            # factor number
            elif inbuf[2] == self.FACTOR_NUMBER:  # 0x12
                return self._fromBytesToStr(inbuf, 4, 4 + 8)

            # release date/ current time
            elif inbuf[2] == self.RELEASE_DATE or inbuf[2] == self.CURRENT_DATE_TIME:  # 0x13 0x20
                try:
                    dataDict["time"] = OrderedDict()
                    dataDict["time"]["year"] = 2000 + inbuf[9]
                    dataDict["time"]["month"] = inbuf[8]
                    dataDict["time"]["day"] = inbuf[7]
                    dataDict["time"]["hour"] = inbuf[6]
                    dataDict["time"]["minute"] = inbuf[5]
                    dataDict["time"]["sec"] = inbuf[4]
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # program version
            elif inbuf[2] == self.PROGRAM_VERSION:  # 0x14
                try:
                    return self._fromBytesToStr(inbuf, 4, 4 + 4)
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # network address
            elif inbuf[2] == self.NETWORK_ADDRESS:  # 0x15
                try:
                    return inbuf[4]
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # User ID
            elif inbuf[2] == self.USER_ID:  # 0x16
                return self._fromBytesToStr(inbuf, 4, 4 + 8)

            # port settings
            elif inbuf[2] == self.PORT_SETTINGS:  # 0x17
                try:
                    byte_arr = bytearray(b'')
                    byte_arr.append(inbuf[4])
                    byte_arr.append(inbuf[5])
                    dataDict["port"] = OrderedDict()
                    dataDict["port"]["baudrate"] = int.from_bytes(byte_arr, byteorder='big')
                    dataDict["port"]["type"] = inbuf[6]
                    dataDict["port"]["count"] = inbuf[7]
                    dataDict["port"]["parity"] = inbuf[8]
                    dataDict["port"]["stop"] = inbuf[9]
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION
            # END GROUP CONST----------------------------------------

            # DATA ARCHIVE*******************************************

            # hour
            elif inbuf[2] == self.ARCHIVE_ALL_VALUE_HOUR:  # 0xC0
                self.counter = 6
                try:
                    # Определяется, какие контуры есть в данном теплосчетчике, возвращает словарь, где ключ - это номер
                    # контура, а значение - тип контура
                    test = self._contour_definition(inbuf)
                    if test == 0 or test == 1:
                        return test

                    # Перебор по порядку всех контуров и расшифрока данных по ним
                    for i in sorted(test.keys()):
                        if (self.contour & (0x01 << i)) != 2**i and self.contour != 0:
                            continue
                        dataDict[i] = OrderedDict()
                        # Count of parameters depends on the type of contour

                        dataDict[i]["type"] = test[i]
                        dataDict[i]["contour"] = i + 1
                        if test[i] == self.METER_CONTOUR_1:
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == self.METER_CONTOUR_2 or test[i] == self.METER_CONTOUR_3 or test[i] == self.METER_CONTOUR_4:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == 5:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                    return dataDict

                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION
            # day/month/year
            elif inbuf[2] == self.ARCHIVE_ALL_VALUE_DAY or inbuf[2] == self.ARCHIVE_ALL_VALUE_MONTH or inbuf[2] == self.ARCHIVE_ALL_VALUE_YEAR: # 0xC1, 0xC2, 0xC3
                self.counter = 6
                try:

                    # Определяется, какие контуры есть в данном теплосчетчике, возвращает словарь, где ключ - это номер
                    # контура, а значение - тип контура
                    test = self._contour_definition(inbuf)
                    if test == 0 or test == 1:
                        return test

                    # Перебор по порядку всех контуров и расшифрока данных по ним
                    for i in sorted(test.keys()):
                        if (i + 1) != self.contour and self.contour != 0:
                            continue
                        dataDict[i] = OrderedDict()
                        # Count of parameters depends on the type of contour
                        dataDict[i]["type"] = test[i]
                        dataDict[i]["contour"] = i + 1
                        if test[i] == self.METER_CONTOUR_1:
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == self.METER_CONTOUR_2 or test[i] == self.METER_CONTOUR_3:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == 5:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION
            # On a specific parametr

            # hour
            elif inbuf[2] == self.ARCHIVE_SPECIFIC_VALUE_HOUR:  # C4
                self.counter = 5
                try:
                    test = dict()
                    # Определяет, какому контору принадлежит ответ и какой его тип, записывается в словарь.
                    # Словарь выбран, чтобы сохранить схожесть с чтением других параметров,
                    # где возможны запросы по нескольким контурам.
                    test[(inbuf[4] & 0x0f) - 1] = inbuf[4] >> 4

                    # Перебор по порядку всех контуров и расшифрока данных по ним
                    for i in test.keys():
                        dataDict[i] = OrderedDict()
                        dataDict[i]["contour"] = i + 1
                        dataDict[i]["type"] = test[i]
                        if test[i] == self.METER_CONTOUR_1:
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x80:
                                dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == self.METER_CONTOUR_2 or test[i] == self.METER_CONTOUR_3 or test[i] == self.METER_CONTOUR_4:
                            if self.arch_buff[4] & 0x01:
                                dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x04:
                                dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x08:
                                dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x10:
                                dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x80:
                                dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == 5:
                            if self.arch_buff[4] & 0x01:
                                dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["V2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x04:
                                dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["M2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x08:
                                dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["t3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x10:
                                dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["p3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x80:
                                dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                                dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # day/month/year

            elif inbuf[2] == self.ARCHIVE_SPECIFIC_VALUE_HOUR or inbuf[2] == self.ARCHIVE_SPECIFIC_VALUE_MONTH or inbuf[2] == self.ARCHIVE_SPECIFIC_VALUE_YEAR:  # 0xC5, 0xC6, 0xC7
                self.counter = 5
                try:
                    test = dict()
                    # определяет, какому контору принадлежит ответ и какой его тип
                    test[(inbuf[4] & 0x0f) - 1] = inbuf[4] >> 4

                    # Перебор по порядку всех контуров и расшифрока данных по ним
                    for i in test.keys():
                        dataDict[i] = OrderedDict()
                        dataDict[i]["contour"] = i + 1
                        dataDict[i]["type"] = test[i]
                        if test[i] == self.METER_CONTOUR_1:
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == self.METER_CONTOUR_2 or test[i] == self.METER_CONTOUR_3 or test[i] == self.METER_CONTOUR_4:
                            if self.arch_buff[4] & 0x01:
                                dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x04:
                                dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')

                        elif test[i] == 5:
                            if self.arch_buff[4] & 0x01:
                                dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x02:
                                dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["V2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x04:
                                dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                                dataDict[i]["M2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            if self.arch_buff[4] & 0x20:
                                dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[4] & 0x40:
                                dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x01:
                                dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            if self.arch_buff[5] & 0x02:
                                dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # END DATA ARCHIVE***************************************

            # CURRENT DATA-------------------------------------------

            elif inbuf[2] == self.CURRENT_DATA_VALUE: # 0x2E
                self.counter = 6
                try:

                    # Определяется, какие контуры есть в данном теплосчетчике, возвращает словарь, где ключ - это номер
                    # контура, а значение - тип контура
                    test = self._contour_definition(inbuf)
                    if test == 0 or test == 1:
                        return test

                    # Перебор по порядку всех контуров и расшифрока данных по ним
                    for i in sorted(test.keys()):
                        if (i + 1) != self.contour and self.contour != 0:
                            continue
                        dataDict[i] = OrderedDict()
                        dataDict[i]["contour"] = i + 1
                        dataDict[i]["type"] = test[i]
                        if test[i] == self.METER_CONTOUR_1:
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                            dataDict[i]["Gv1"] = struct.unpack('f', self._automation_bytearray(inbuf))[0]

                        elif test[i] == self.METER_CONTOUR_2 or test[i] == self.METER_CONTOUR_3  or test[i] == self.METER_CONTOUR_4:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                            dataDict[i]["Gv1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Gm1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["P1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))

                        elif test[i] == 5:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["V2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["M2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["t3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["p3"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Tn"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Terr1"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr2"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr3"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Terr4"] = int.from_bytes(self._automation_bytearray(inbuf, count=1), byteorder='big')
                            dataDict[i]["Err"] = int.from_bytes(self._automation_bytearray(inbuf), byteorder='big')
                            dataDict[i]["Act"] = int.from_bytes(self._automation_bytearray(inbuf, count=2), byteorder='big')
                            dataDict[i]["Gv1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Gv2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Gm1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Gm2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["P1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["P2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # END CURRENT DATA---------------------------------------

            # GROUP THERMAL ENERGY

            # sum/to the beginning of the day
            elif inbuf[2] == self.SUM_HEAT or inbuf[2] == self.SUM_HEAT_DAY_BEGIN or inbuf[2] == self.SUM_HEAT_MONTH_BEGIN or inbuf[2] == self.SUM_HEAT_YEAR_BEGIN:  # 0x01, 0x0A, 0x0B, 0x0C
                self.counter = 6
                try:
                    test = self._contour_definition(inbuf)
                    if test == 0 or test == 1:
                        return test

                    for i in sorted(test.keys()):
                        if (i + 1) != self.contour and self.contour != 0:
                            continue
                        dataDict[i] = OrderedDict()

                        dataDict[i]["contour"] = i + 1
                        dataDict[i]["type"] = test[i]
                        if test[i] == 1:
                            pass
                        elif test[i] == 2 or test[i] == 3 or test[i] == 4:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                        elif test[i] == 5:
                            dataDict[i]["Q1"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                            dataDict[i]["Q2"] = float("{0:.2f}".format(struct.unpack('f', self._automation_bytearray(inbuf))[0]))
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.INDEX_OUT_OF_RANGE
            # END GROUP THERMAL ENERGY

            # CONFIGERATION

            elif inbuf[2] == self.CONFIGURATION:
                try:
                    config = self._contour_definition(inbuf)
                    if config == 0 or config == 1:
                        return config

                    result = ""
                    for i in sorted(config.keys()):
                        result += "Contour: %i, type: %i" % ((int(i)+1), config[i])
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            # END CONFIGERATION
        else:
            return self.NOT_CORRECT_CRC


    def _contour_definition(self, inbuf):

        """

        Метод определяет какие контура задействованы в данном теплосчетчике и каких они типов.

        """
        try:
            test = {}
            if inbuf[4] >> 4:
                test[1] = inbuf[4] >> 4
            if inbuf[4] & 0x0f:
                test[0] = inbuf[4] & 0x0f
            if inbuf[5] >> 4:
                test[3] = inbuf[4] >> 4
            if inbuf[5] & 0x0f:
                test[2] = inbuf[4] & 0x0f
            return test
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION

    def _automation_bytearray(self, inbuf, count=4):

        """

        Метод возвращает строку байт(измен.) из произвольного числа байт(по умалчанию 4),
        начиная со значения счетчика counter.

        """

        try:
            byte_arr = bytearray(b'')
            for i in range(count):
                byte_arr.append(inbuf[self.counter])  # 4
                self.counter += 1  # 5
            return byte_arr
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION


    def _fromBytesToStr(self, inbuf, start, end):

        """

        Метод из последовательности байт, начиная со значения start и заканчивая значением end,
        формирует строку в кодировке ASCII.

        """
        try:
            byte_arr = bytearray(b'')
            for i in range(start, end):
                byte_arr.append(inbuf[i])
            return bytes.decode(bytes(byte_arr), "ascii")
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION
