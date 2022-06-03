import select
from NetworkHandler import NetworkHandler, TCP, UDP

from sys import argv

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
        sockets = [self.tcp_socket]
        while True:
            readable, writable, errorable = select.select(sockets, [], [])
            for s in readable:
                if s is self.tcp_socket:
                    client_socket, address = s.accept()
                    print(f"got new connectiom from {address}")
                    sockets.append(client_socket)
                else:
                    data = s.recv(100)
                    if data:
                        msg = data.decode('utf-8')
                        print(msg)
                        resp = msg[0:4] + " 200"
                        if msg[0:4] == "GTIP":
                            resp = msg[0:4] + " 200\n127.0.0.1 5004"
                        s.send(resp.encode())
                    else:
                        s.close()
                        sockets.remove(s)

if len(argv) != 2:
    print("invalid number of arguments")
    exit(1)
server = Server(int(argv[1]))
server.start()
server.run()