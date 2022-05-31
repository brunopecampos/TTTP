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
            self.socket.connect(self.addr)

    def disconnect(self):
        self.socket.close()

    def listen(self, port):
        host = ''
        self.socket.bind((host, port))
        self.socket.listen()
        self.listening = True

    def accept_connection(self):
        self.current_conn, self.curr_addr = self.socket.accept()

    def send_message_to_client(self, message):
        data = message.encode()
        self.current_conn.sendall(data)

    def receive_message_from_client(self):
        data = self.current_conn.recv(BUFFER_SIZE)
        return data.decode()

    def send_message(self, message):
        data = message.encode()
        if self.protocol == TCP:
            self.socket.send(data)
        elif self.protocol == UDP:
            self.socket.sendto(data, self.addr)

    def receive_message(self):
        if self.protocol == TCP:
            data = self.socket.recv(BUFFER_SIZE)
            return data.decode()
        elif self.protocol == UDP:
            data, addr = self.socket.recvfrom(BUFFER_SIZE)
            msg = data.decode()
            return msg, addr

    def get_socket(self):
        return self.socket

    def close(self):
        self.socket.close()
