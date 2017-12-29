import serial
import logging


class COM_worker():

    def __init__(self, number_com, baud_rate, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE):
        logging.basicConfig(level=logging.DEBUG,
                            format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)s [%(asctime)s]   %(message)s')
        self.__serial_object = serial.Serial(number_com, baud_rate, bytesize=bytesize, parity=parity, stopbits=stopbits)
        self.buff = b''

    @property
    def serial_object(self):
        return self.__serial_object

    @serial_object.setter
    def serial_object(self, serial_object):
        self.__serial_object = serial_object

    @property
    def buff(self):
        return self.__buff

    @buff.setter
    def buff(self, buff):
        self.__buff = buff

    def write(self, string_byte):
        if self.serial_object.is_open:
            self.serial_object.write(bytes(string_byte))
        else:
            self.serial_object.open()
            self.serial_object.write(bytes(string_byte))

    def read_answer(self, timeout):
        self.serial_object.timeout = timeout
        self.buff = b''
        call = 1
        while call != 0:
            data = self.serial_object.read()  # пытается считать 1 байт, если это удалось, то дальше этот байт сумируется с результатом метода readLine()
            if data != b'':
                self.buff += data + self.serial_object.readline()
                self.serial_object.timeout = 2
            else:
                call = 0  # Если вышел таймаут ожидания одного байта, то цикл прекращается
        self.serial_object.close()
        logging.INFO("Чтение COM-порта завершено")
        return self.buff
