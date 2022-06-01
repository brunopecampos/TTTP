from http import server
from NetworkHandler import NetworkHandler
from NetworkInputInterpreter import NetworkInputInterpreter

TCP = "tcp"
UDP = "udp"
SERVER = "server"
OPPONNET = "opponent"
HOST = "host"
CLIENT = "client"
BUFFER_SIZE = 1024

class NetworkObject:
  def __init__(self, role, protocol, receiver):
    self.last_message = ""
    self.network_input_interpreter = NetworkInputInterpreter()
    self.network_handler = NetworkHandler(protocol)
    self.role = role
    self.protocol = protocol
    self.receiver = receiver
    self.socket = None
    self.address = None

  def set_last_message(self, message):
    self.last_message = message

  def set_socket(self, socket):
    self.socket = socket

  def set_address(self, address):
    self.address = address

  def send_message(self, message):
    encoded_message = message.encode()
    if self.protocol == TCP:
      self.socket.sendall(encoded_message)
    else:
      self.sendto(encoded_message, self.address)

  def receive_message(self):
    data = ""
    if self.protocol == TCP:
      data = self.socket.recv(BUFFER_SIZE)
    else: 
      data, address = self.socket.recvfrom(BUFFER_SIZE)
      self.set_address(address)
    
    return data.decode()
