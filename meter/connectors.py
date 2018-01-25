import serial
import socket


class BaseConnector:
    """Абстрактный класс соединения со счетчиками"""

    connection_params = None

    # Константы
    CONNECTION_TYPE = ''

    # коды возврата
    CONNECTION_SUCCESS = 0
    CONNECTION_WRONG_PARAMS_ERR = 1
    CONNECTION_TIMEOUT_ERR = 2
    CONNECTION_GENERIC_ERR = 3

    def __str__(self):
        """Строковое представление объекта соединения"""
        return '{}'.format(self.CONNECTION_TYPE)

    def connect(self):
        """Метод реализует процесс установления соединения"""
        raise NotImplementedError

    def disconnect(self):
        """Метод реализует процесс завершения соединения"""
        raise NotImplementedError

    def read(self, timeout=5):
        """Читаем ответ"""
        raise NotImplementedError

    def write(self, byte_str):
        """Передаем запрос"""
        raise NotImplementedError


class RS232Connector(BaseConnector):
    """Класс реализует соединение со счетчиком по последовательному порту RS232"""

    # константы
    CONNECTION_TYPE = 'RS232'

    #   parity
    PARITY_NONE = serial.PARITY_NONE
    PARITY_EVEN = serial.PARITY_EVEN
    PARITY_ODD = serial.PARITY_ODD
    PARITY_MARK = serial.PARITY_MARK
    PARITY_SPACE = serial.PARITY_SPACE

    #   bytesize
    FIVEBITS = serial.FIVEBITS
    SIXBITS = serial.SIXBITS
    SEVENBITS = serial.SEVENBITS
    EIGHTBITS = serial.EIGHTBITS

    #   escape char
    CR = serial.CR
    LF = serial.LF


    # параметры
    __rs232_port = None
    __rs232_baud_rate = None
    __rs232_bytesize = None
    __rs232_parity = None
    __rs232_stopbits = None

    # Глабальные переменные
    __buffer = b''
    __serial_object = None

    def __init__(self, **kwargs):
        """Инициализация объекта класса параметрами соединения"""

        # port
        port = kwargs.get('port')

        if port is None:
            raise ValueError     # todo: custom exceptions
        self.__rs232_port = port

        # baudrate
        baudrate = kwargs.get('baudrate')

        if baudrate not in (4800, 9600, 14400, 19200, 38400, 56000):
            raise ValueError    # todo: custom exceptions
        self.__rs232_baud_rate = baudrate

        # bytesize
        self.__rs232_bytesize = kwargs.get('bytesize', 1)

        # parity
        parity = kwargs.get('parity')

        if parity not in (self.PARITY_NONE, self.PARITY_EVEN):
            raise ValueError    # todo: custom exceptions

        self.__rs232_parity = parity

        # stopbits
        self.__rs232_stopbits = kwargs.get('stopbits')


    def connect(self):
        """Устанавливаем соединение"""
        self.__serial_object = serial.Serial(
            port=self.__rs232_port,
            baudrate=self.__rs232_baud_rate,
            bytesize=self.__rs232_bytesize,
            parity=self.__rs232_parity,
            stopbits=self.__rs232_stopbits,
        )

    def disconnect(self):
        """Закрываем соединение"""
        try:
            self.__serial_object.close()
        except:
            return self.CONNECTION_GENERIC_ERR

    def read(self, timeout = 4):
        """Получаем ответ"""

        self.__serial_object.timeout = timeout
        self.__buff = b''

        call = 1

        while call != 0:
            data = self.__serial_object.read()  # пытается считать 1 байт, если это удалось, то дальше этот байт сумируется с результатом метода readLine()

            if data != b'':
                self.__buff += data + self.__serial_object.read()
                self.__serial_object.timeout = 1
            else:
                call = 0  # Если вышел таймаут ожидания одного байта, то цикл прекращается

        return self.__buff

    def write(self, byte_str):
        """Отправляем запрос"""

        if self.__serial_object.is_open:
            self.__serial_object.write(bytes(byte_str))
        else:
            self.__serial_object.open()
            self.__serial_object.write(bytes(byte_str))


class GSMConnector(BaseConnector):
    """Класс реализует соединение со счетчиком по GSM"""

    # константы
    CONNECTION_TYPE = 'GSM'

    # комманды для модема
    COMMAND_AT = b'\x41\x54\x0d\x0d'  # байтовая строка AT-комманды AT(для проверки соединения с модемом)
    COMMAND_ATE0 = b'\x41\x54\x45\x30\x0d\x0d'  # комманда отключения эхо
    COMMAND_ATD = b'\x41\x54\x44'  # комманда набора намера, дальше должен идти телефон в формате ATD80445972049, последний байт 0x0d
    COMMAND_STOP_SEND = b'\x2b\x2b\x2b'  # закончить передачу данных в текущем сеансе(+++), после этого сообщения модем будет снова отвечать, на AT-комманды
    COMMAND_DISCONNECT = b'\x41\x54\x48\x30\x0d\x0a'  # строка ATH0, разорвать соединение

    # ответы модема
    RESPONSE_OK = b'\x0d\x0a\x4f\x4b\x0d\x0a'  # AT-комманда OK
    RESPONSE_CONNECTION_9600 = b'\x0d\x0a\x43\x4f\x4e\x4e\x45\x43\x54\x20\x39\x36\x30\x30\x0d\x0a'  # строка CONNECTION 9600, сообщение об успешном соединении
    RESPONSE_NO_CARRIER = b'\x0d\x0a\x4e\x4f\x20\x43\x41\x52\x52\x49\x45\x52\x0d\x0a'  # строка NO CARRIER, ошибка СИМ-карты
    RESPONSE_BUSY = b'\x0d\x0a\x42\x55\x53\x59\x0d\x0a'  # строка BUSY, номер занят
    RESPONSE_NO_DIALTONE = b'\x4e\x4f\x20\x44\x49\x41\x4c\x54\x4f\x4e\x45\x0d\x0a'  # строка NO DIALTONE, нет сигнала
    RESPONSE_NO_ANSWER = b'\x4e\x4f\x20\x41\x4e\x53\x57\x45\x52\x0d\x0a'  # строка NO ANSWER, нет ответа
    RESPONSE_ERROR = b'\x0d\x0a\x45\x52\x52\x4f\x52\x0d\x0a'  # строка ERROR, ошибка

    # Глобальные переменные
    __buff = b''  # помежуточный буфер для хранения данных
    __modem_obj = None  # Объект последовательного порта
    __number = None # Номер телефона

    def __init__(self, **kwargs):
        """Задание параметров"""

        self.__number = 411

        self.__modem_obj = RS232Connector(
            port='/dev/ttyUSB0',
            baudrate=9600,
            bytesize=RS232Connector.EIGHTBITS,
            parity=RS232Connector.PARITY_NONE,
            stopbits=1
        )

    def __modem_check_connection(self):
        """Проверяем соединение"""

        self.__modem_obj.write(self.COMMAND_AT)
        self.buff = self.__modem_obj.read(0.5)

        if self.__modem_check_answer(self.RESPONSE_OK, self.COMMAND_AT + self.RESPONSE_OK):
            print("Связь с модемом есть")
            return True
        else:
            print("Нет связи")
            return False

    def __modem_echo_off(self):
        """ Метод, который отключает echo в модеме"""

        self.__modem_obj.write(self.COMMAND_ATE0)
        self.__buff = self.__modem_obj.read(0.5)

        if self.__modem_check_answer(self.RESPONSE_OK, self.COMMAND_ATE0 + self.RESPONSE_OK):
            print("Эхо успешно убрано")
        else:
            print("Не убрано эхо")

    def __modem_check_answer(self, response_with_echo, response):
        """Сверка ответа с ожидаемым"""

        if self.buff == response or self.buff == response_with_echo:
            return True
        else:
            return False

    def connect(self):
        """Метод GSM-подключения"""

        if not self.__modem_check_connection():
            return self.CONNECTION_GENERIC_ERR
        self.__modem_echo_off()

        self.__modem_obj.write(self.COMMAND_ATD + self.__number.encode() + b'\x0d')
        self.__buff = self.__modem_obj.read(30)

        if self.__modem_check_answer(self.RESPONSE_NO_CARRIER, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_NO_CARRIER):
            print("ошибка сим-карты, проверьте правильность установки, тариф и т.д.")
            return self.CONNECTION_GENERIC_ERR

        elif self.__modem_check_answer(self.RESPONSE_BUSY, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_BUSY):
            print("Вызов отклонен, номер занят ")
            return self.CONNECTION_GENERIC_ERR

        elif self.__modem_check_answer(self.RESPONSE_NO_DIALTONE, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_NO_DIALTONE):
            print("Нет сигнала")
            return self.CONNECTION_GENERIC_ERR

        elif self.__modem_check_answer(self.RESPONSE_NO_ANSWER, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_NO_ANSWER):
            print("Нет ответа")
            return self.CONNECTION_GENERIC_ERR

        elif self.__modem_check_answer(self.RESPONSE_ERROR, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_ERROR):
            print("Пришло сообщение об ошибке")
            return self.CONNECTION_GENERIC_ERR

        elif self.__modem_check_answer(self.RESPONSE_CONNECTION_9600, self.COMMAND_ATD + self.__number.encode() + b'\x0d' + self.RESPONSE_CONNECTION_9600):
            print("Связь с удаленным модемом установлена")
            return self.CONNECTION_SUCCESS

        else:
            print("Неизвестная ошибка")
            return self.CONNECTION_GENERIC_ERR

    def disconnect(self):
        """Разрываем соединение"""

        self.__modem_obj.write(self.COMMAND_STOP_SEND)
        self.__buff = self.__modem_obj.read(8)

        if self.__modem_check_answer(self.RESPONSE_OK, self.RESPONSE_OK):
            print("Прервана передача данных.")
        else:
            print("Нет ответа от модема")

        self.__modem_obj.write(self.COMMAND_DISCONNECT)
        self.__buff = self.__modem_obj.read(0.5)

        if self.__modem_check_answer(self.RESPONSE_OK, self.COMMAND_DISCONNECT + self.RESPONSE_OK):
            print("Модем положил все трубки.")
        else:
            print("Есть проблема с отключением.")

        self.__modem_obj.disconnect()


class IPConnector(BaseConnector):
    """Класс реализует соединение со счетчиком по GPRS"""

    # константы
    CONNECTION_TYPE = 'GPRS'

    # Параметры
    __host = None
    __port = None

    # Глобальные переменные
    __sock = None

    def __init__(self, **kwargs):
        """Задаём параметры"""
        self.__host = kwargs.get('host')
        self.__port = kwargs.get('port')

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, timeout=5):
        """ Устанавливаем соединение """

        try:
            self.__sock.connect((self.__host, self.__port))
            self.__sock.timeout = timeout

        except AttributeError:
            return self.CONNECTION_WRONG_PARAMS_ERR
        except TimeoutError:
            return self.CONNECTION_TIMEOUT_ERR
        except Exception:
            return self.CONNECTION_GENERIC_ERR
        else:
            return self.CONNECTION_SUCCESS

    def write(self, data):
        """ Отправлем данные """

        #try:
        self.__sock.send(data)

        # except AttributeError:
        #     return self.CONNECTION_WRONG_PARAMS_ERR
        # except Exception:
        #     return self.CONNECTION_GENERIC_ERR
        # else:
        #     return self.CONNECTION_SUCCESS

    def read(self, timeout=20):
        """Читаем данные"""

        try:
            self.__sock.settimeout(timeout)
            data = self.__sock.recv(1024)

        except TimeoutError:
            return self.CONNECTION_TIMEOUT_ERR
        except Exception:
            return self.CONNECTION_GENERIC_ERR
        else:
            return data

    def disconnect(self):
        """Закрываем соединение"""

        try:
            self.__sock.close()

        except AttributeError:
            return 1
        else:
            return self.CONNECTION_SUCCESS
