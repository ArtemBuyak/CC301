import logging
from COM_work import COM_worker


class GSM():

    def __init__(self, serial_object):
        logging.basicConfig(level=logging.DEBUG,
                            format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)s [%(asctime)s]   %(message)s')
        if type(serial_object) == COM_worker:  #проверка на тип СОМ-объекта
            self.__serial_object = serial_object  # COM-объект, через который будет идти работа с COM-портом
        else:
            logging.INFO("В качестве параметра передан не объект класса Serial")
        self.__buff = b'' #помежуточный буфер для хранения данных

        #Блок констант для сравнения ответов с ними
        self.AT = b'\x41\x54\x0d\x0d' #байтовая строка AT-комманды AT(для проверки соединения с модемом)
        self.OK = b'\x0d\x0a\x4f\x4b\x0d\x0a' #AT-комманда OK
        self.ATE0 = b'\x41\x54\x45\x30\x0d\x0d' #комманда отключения эхо
        self.ATD = b'\x41\x54\x44' #комманда набора намера, дальше должен идти телефон в формате ATD80445972049, последний байт 0x0d
        self.CONNECTION_9600 = b'\x0d\x0a\x43\x4f\x4e\x4e\x45\x43\x54\x20\x39\x36\x30\x30\x0d\x0a' # строка CONNECTION 9600, сообщение об успешном соединении
        self.NO_CARRIER = b'\x0d\x0a\x4e\x4f\x20\x43\x41\x52\x52\x49\x45\x52\x0d\x0a' #строка NO CARRIER, ошибка СИМ-карты
        self.BUSY = b'\x0d\x0a\x42\x55\x53\x59\x0d\x0a' #строка BUSY, номер занят
        self.NO_DIALTONE = b'\x4e\x4f\x20\x44\x49\x41\x4c\x54\x4f\x4e\x45\x0d\x0a' #строка NO DIALTONE, нет сигнала
        self.NO_ANSWER = b'\x4e\x4f\x20\x41\x4e\x53\x57\x45\x52\x0d\x0a' #строка NO ANSWER, нет ответа
        self.STOP_SEND = b'\x2b\x2b\x2b' # закончить передачу данных в текущем сеансе(+++), после этого сообщения модем будет снова отвечать, на AT-комманды
        self.DISCONNECTION = b'\x41\x54\x48\x30\x0d\x0a' #строка ATH0, разорвать соединение
        self.ERROR = b'\x0d\x0a\x45\x52\x52\x4f\x52\x0d\x0a' # строка ERROR, ошибка


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

    # Метод для проверки соединения
    def check_connection(self):
        self.serial_object.write(self.AT)
        self.buff = self.serial_object.read_answer(0.5)
        if(self.check_answer(self.OK, self.AT + self.OK)):
            logging.INFO("Связь с модемом есть")
        else:
            logging.ERROR("Нет связи")

    # Метод, который убирает эхо в модеме
    def eho_off(self):
        self.serial_object.write(self.ATE0)
        self.buff = self.serial_object.read_answer(0.5)
        if (self.check_answer(self.OK, self.ATE0 + self.OK)):
            logging.INFO("Эхо успешно убрано")
        else:
            logging.ERROR("Не убрано эхо")

    # Метод GSM-подключения
    def connection(self, number):
        self.serial_object.write(self.ATD + number.encode() + b'\x0d')
        self.buff = self.serial_object.read_answer(30)
        if self.check_answer(self.CONNECTION_9600, self.ATD + number.encode() + b'\x0d' + self.CONNECTION_9600):
            logging.INFO("Связь с удаленным модемом установлена")
            return 0
        elif self.check_answer(self.NO_CARRIER, self.ATD + number.encode() + b'\x0d' + self.NO_CARRIER):
            logging.ERROR("ошибка сим-карты, проверьте правильность установки, тариф и т.д.")
            return 1
        elif self.check_answer(self.BUSY, self.ATD + number.encode() + b'\x0d' + self.BUSY):
            logging.ERROR("Вызов отклонен, номер занят ")
            return 1
        elif self.check_answer(self.NO_DIALTONE, self.ATD + number.encode() + b'\x0d' + self.NO_DIALTONE):
            logging.ERROR("Нет сигнала")
            return 1
        elif self.check_answer(self.NO_ANSWER, self.ATD + number.encode() + b'\x0d' + self.NO_ANSWER):
            logging.ERROR("Нет ответа")
            return 1
        elif self.check_answer(self.ERROR, self.ATD + number.encode() + b'\x0d' + self.ERROR):
            logging.ERROR("Пришло сообщение об ошибке")
            return 1
        else:
            logging.ERROR("Незарегестрированная ситуация")
            return 1

    def gsm_connection(self, number):
        self.check_connection()
        self.eho_off()
        return self.connection(number)

    def gsm_disconnection(self):
        self.serial_object.write(self.STOP_SEND)
        self.buff = self.serial_object.read_answer(8)
        if self.check_answer(self.OK, self.OK):
            logging.INFO("Прервана передача данных.")
        else:
            logging.ERROR("Нет ответа от модема")
        self.serial_object.write(self.DISCONNECTION)
        self.buff = self.serial_object.read_answer(0.5)
        if self.check_answer(self.OK, self.DISCONNECTION + self.OK):
            logging.INFO("Модем положил все трубки.")
        else:
            logging.ERROR("Есть проблема с отключением.")

    # Сверка ответа с ожидаемым
    def check_answer(self, const_with_eho, const):
        if self.buff == const or self.buff == const_with_eho:
            return 1
        else:
            return 0

