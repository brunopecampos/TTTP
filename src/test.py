from sys import argv
from Server import Server

port = int(argv[1])
s = Server(port)
print(f"server is running on port {port}")
s.start()
