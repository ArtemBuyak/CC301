from meter.crc import CRC16_C0C1
import struct
from collections import OrderedDict

class CC301:

    """

    Реализация протокола электросчетчика "Гран-Электро СС-301"

    Блок констант
    -------------------------------------------------------------------------------
    Значений параметров для считывания:
    ID                - идентификационный номер устройства. Вызов (ADDR- адрес устр-ва, obj.ID, parametr - 0x00, offset - 0x00, tariff - 0x00).
    DEVICE_TYPE       - тип прибора. Вызов аналогично ID.
    FACTOR_NUMBER     - заводской номер. -//-.
    RELEASE_DATE      - дата выпуска прибора. -//-.
    CURRENT_DATE_TIME - текущее время и число. -//-.
    PROGRAM_VERSION   - версия программы. Вызов -//-.
    NETWORK_ADDRESS   - сетевой адрес прибора. -//-.
    USER_ID           - идентификатор пользователя. -//-.
    PORT_SETTINGS     - конфигурация порта связи. -//-.

    SUM_BEGIN_DAY     - накопленная энергия на начало суток. Вызов (ADDR - адрес устройства, obj.SUM_BEGIN_DAY, offset - (0...30), tariff - (0...8))
    SUM_BEGIN_MONTH   - накопленная энергия на начало месяца. Вызов (ADDR - адрес устройства, obj.SUM_BEGIN_MONTH, offset - (0...11), tariff - (0...8))
    SUM_BEGIN_YEAR    - накопленная энергия на начало года. Вызов (ADDR - адрес устройства, obj.SUM_BEGIN_YEAR, offset - (0...7), tariff - (0...8))
    INCREMENT_DAY     - приращение энергии за сутки. Вызов (ADDR - aдрес устройства, obj.INCREMENT_DAY, offset - (0...(len(month) - 1)), tariff - (0...8))
    INCREMENT_MONTH   - приращение энергии за месяц. Вызов (ADDR - aдрес устройства, obj.INCREMENT_DAY, offset - (0...23), tariff - (0...8))
    INCREMENT_YEAR    - приращение энергии за год. Вызов (ADDR - aдрес устройства, obj.INCREMENT_DAY, offset - (0...7), tariff - (0...8))
    AVERAGE_3_MIN     - среднее значение мощности за 3 минуты. Вызов (ADDR - адрес устройства, obj.AVERAGE_3_MIN, offset - (0...10), tariff - 0x00)
    AVERAGE_30_MIN    - среднее значение мощности за 30 минут. Вызов (ADDR - адрес устройства, obj.AVERAGE_30_MIN, offset - (0...1), tariff - 0x00)
    -------------------------------------------------------------------------------

    """

    def __init__(self):
        self.__buff = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self.__list_of_parametrs = ["a_plus", "a_minus", "r_plus", "r_minus"]
        self.__crc = CRC()
        self.__checkParam = 0
        self.__checkAddr = 0
        self.__strResult = ""
        self.__Ke = 0  # weight coefficient

    ID = 0
    DEVICE_TYPE = 17
    FACTOR_NUMBER = 18
    RELEASE_DATE = 19
    CURRENT_DATE_TIME = 32
    PROGRAM_VERSION = 20
    NETWORK_ADDRESS = 21
    USER_ID = 22
    PORT_SETTINGS = 23
    WEIGHT_COEFFICIENT = 24
    SUM_BEGIN_DAY = 42
    SUM_BEGIN_MONTH = 43
    SUM_BEGIN_YEAR = 44
    INCREMENT_DAY = 2
    INCREMENT_MONTH = 3
    INCREMENT_YEAR = 4
    ALL_SUM_ENERGY = 1
    AVERAGE_3_MIN = 5
    AVERAGE_30_MIN = 6
    SLICE_OF_ENERGY = 36

    # Ошибки:
    GENERAL_EXCEPTION  = 0
    INDEX_OUT_OF_RANGE = 1
    NOT_CORRECT_CRC    = 2

    @property
    def list_of_parametrs(self):
        return self.__list_of_parametrs
    @list_of_parametrs.setter
    def list_of_parametrs(self, list_of_paramets):
        self.__list_of_parametrs = list_of_paramets

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
    def pack(self, addr, parametr, offset, tariff):

        """
        Метод вернет 0, в случае возникновения ошибки при формировании посылки

        """
        # ошибка возврата, если переданы значения больше максимального значения для byte
        if addr > 255 or parametr > 255 or offset > 255 or tariff > 255:
            return 0

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
        return bytes(self.buff)

    def unpack(self, inbuf):


        """

        Метод обработки входящей от счетчика посылки. В зависимости от байта параметра вызывается определенный case обработки.
        Возвращает 1, в случае возникновения ошибки индекса, в случае других ошибок вернется 0.

        """
        dataDict = OrderedDict()
        if self.checkAnswer(inbuf):
            # date current/release date
            if inbuf[2] == self.RELEASE_DATE or inbuf[2] == self.CURRENT_DATE_TIME:  # 0x20, 0x13
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

            # by the beginning of the day/month/year
            elif inbuf[2] == self.SUM_BEGIN_DAY or inbuf[2] == self.SUM_BEGIN_MONTH or inbuf[2] == self.SUM_BEGIN_YEAR:  # 0x2A, 0x2B, 0x2C
                return self.processingReadAnswer(inbuf, dataDict)

            # for the day/month/year
            elif inbuf[2] == self.INCREMENT_DAY or inbuf[2] == self.INCREMENT_MONTH or inbuf == self.SUM_BEGIN_YEAR:
                return self.processingReadAnswer(inbuf, dataDict)

            # for the sum value, average 3-min/15-min
            elif inbuf[2] == self.ALL_SUM_ENERGY or inbuf[2] == self.AVERAGE_3_MIN or inbuf[2] == self.AVERAGE_30_MIN:
                return self.processingReadAnswer(inbuf, dataDict)

            # sres
            elif inbuf[2] == self.SLICE_OF_ENERGY:  # 0x24
                return self.processingBytes(inbuf, dataDict)


            #GROUP CONST----------------------------------

            # identification device number
            elif inbuf[2] == self.ID:
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
            elif inbuf[2] == self.DEVICE_TYPE: # 0x11
                return self.fromBytesToStr(inbuf, 4, 4+17)

            # factor number
            elif inbuf[2] == self.FACTOR_NUMBER:  # 0x12
                return self.fromBytesToStr(inbuf, 4, 4+10)

            # version and CRCprogramming
            elif inbuf[2] == self.PROGRAM_VERSION:  # 0x14
                return self.fromBytesToStr(inbuf, 4, 4+4)

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
                return self.fromBytesToStr(inbuf, 4, 4+8)

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

            # weight coefficient
            elif inbuf[2] == self.WEIGHT_COEFFICIENT:  # 0x18
                try:
                    byte_arr = bytearray(b'')
                    byte_arr.append(inbuf[8])
                    byte_arr.append(inbuf[9])
                    self.Ke = int.from_bytes(byte_arr, byteorder='big')
                    self.Ke = self.Ke/1000000.0
                    dataDict["Ke"] = self.Ke
                    return dataDict
                except IndexError:
                    return self.INDEX_OUT_OF_RANGE
                except Exception:
                    return self.GENERAL_EXCEPTION

            #END GROUP CONST-----------------------------
        else:
            return self.NOT_CORRECT_CRC



    def fromBytesToStr(self, inbuf, start, end):

        """ Метод формирует и возвращает строку из последовательности байт в кодировке ASCII"""
        try:
            byte_arr = bytearray(b'')
            for i in range(start, end):
                byte_arr.append(inbuf[i])
            return bytes.decode(bytes(byte_arr), "ascii")
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION


    #processing answer and save in struct Data()
    def processingReadAnswer(self, inbuf, dataDict, index=4):

        """ Метод формирует словарь(dict) с ключами из массива list_of_parametrs, значение - число float, сформированное из 4 байт данных """
        try:
            byte_arr = bytearray(b'')
            for i in self.list_of_parametrs:
                byte_arr.append(inbuf[index])
                byte_arr.append(inbuf[index + 1])
                byte_arr.append(inbuf[index + 2])
                byte_arr.append(inbuf[index + 3])
                dataDict[i] = struct.unpack('f', byte_arr)
            return dataDict
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION

    # for sres
    def processingBytes(self, inbuf, dataDict):

        """ Метод формирует словарь(dict) с ключами из массива list_of_parametrs, значение - срезы энергии"""
        try:
            byte_arr = bytearray(b'')
            for i in range(4):
                byte_arr.append(inbuf[4 + i*2])
                byte_arr.append(inbuf[5 + i*2])
                dataDict[self.list_of_parametrs[i]] = int.from_bytes(byte_arr, byteorder='big')
            return dataDict
        except IndexError:
            return self.INDEX_OUT_OF_RANGE
        except Exception:
            return self.GENERAL_EXCEPTION

    # method check correct answer or not, return bool
    def checkAnswer(self, inbuf):
        """

        Вернет True, если входящая посылка соответствует протоколу, в остальных случаях - False.
        В переменную strResult будет записано описание несоответсвия с протоколом.

        """
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

