import select
from NetworkHandler import NetworkHandler, TCP, UDP

class Server():
    def __init__(self, port):
        self.port = port
        self.tcp_socket = None
        self.udp_socket = None

    def start(self):
        nw_tcp = NetworkHandler(TCP)
        nw_udp = NetworkHandler(UDP)
        nw_tcp.listen(self.port) # start tcp listener
        self.tcp_socket = nw_tcp.get_socket()
        self.udp_socket = nw_udp.get_socket()
        self.run()

    def run(self):
        sockets = [self.tcp_socket, self.udp_socket]
        while True:
            readable, writable, errorable = select.select(sockets, [], [])
            for s in readable:
                if s is self.tcp_socket:
                    client_socket, address = s.accept()
                    sockets.append(client_socket)
                else:
                    data = s.recv(30)
                    if data:
                        s.send("i got " + data)
                    else:
                        s.close()
                        readable.remove(s)

