import socket

TCP = 'tcp'
UDP = 'udp'
BUFFER_SIZE = 250

class NetworkHandler():
    def __init__(self, protocol):
        if protocol == TCP:
            socket_type = socket.SOCK_STREAM
        elif protocol == UDP:
            socket_type = socket.SOCK_DGRAM
        else:
            raise Exception("invalid protocol")

        self.socket = socket.socket(socket.AF_INET, socket_type)
        self.protocol = protocol
        self.addr = ('', '')

    def fileno(self):
        return self.socket.fileno()

    def bind(self, addr):
        self.socket.bind(addr)

    def listen(self):
        if self.protocol == TCP:
            self.socket.listen()

    def set_addr(self, addr):
        self.addr = addr

    def accept(self):
        return self.socket.accept()

    def send(self, message):
        data = message.encode()
        if self.protocol == TCP:
            self.socket.send(data)
        elif self.protocol == UDP:
            self.socket.sendto(data, self.addr)

    def recv(self):
        if self.protocol == TCP:
            data = self.socket.recv(BUFFER_SIZE)
        elif self.protocol == UDP:
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            self.addr = addr
        else:
            raise Exception("Protocol error")
        return data.decode()

    def close(self):
        if self.protocol == TCP:
            self.socket.close()
