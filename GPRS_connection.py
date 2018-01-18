import socket
class Connection:

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @property
    def host(self):
        return self.__host
    @host.setter
    def host(self, host):
        self.__host = host

    @property
    def port(self):
        return self.__port
    @port.setter
    def port(self, port_number):
        self.__port = port_number

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            self.sock.timeout = 5
        except AttributeError:
            return 1
        except TimeoutError:
            return 2
        except Exception:
            return 3
        else:
            return 0

    def send_data(self, data):
        try:
            self.sock.send(data)
        except AttributeError:
            return 1
        except Exception:
            return 2
        else:
            return 0

    def receive_data(self):
        try:
            self.sock.settimeout(10.0)
            data = self.sock.recv(1024)
        except TimeoutError:
            return 1
        except Exception:
            return 2
        else:
            return data

    def close(self):
        try:
            self.sock.close()
        except AttributeError:
            return 1
        else:
            return 0
