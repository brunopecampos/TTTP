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
        self.listening = False

    def connect(self, host, port):
        self.addr = (host, port)
        if self.protocol == TCP:
            self.socket.connect((host, port))

    def accept_connection(self, port):
        if not self.listening:
            self._listen(port)
        return self.socket.accept()

    def send_message(self, message):
        if self.protocol == TCP:
            self.socket.send(message)
        elif self.protocol == UDP:
            self.socket.sendto(message, self.addr)

    def receive_message(self):
        if self.protocol == TCP:
            return self.socket.recv(BUFFER_SIZE)
        elif self.protocol == UDP:
            return self.socket.recvfrom(BUFFER_SIZE)

    def close(self):
        self.socket.close()

    ############################################################################
    # private methods

    def _listen(self, port):
        host = socket.gethostname()
        self.socket.bind((host, port))
        self.listening = True

