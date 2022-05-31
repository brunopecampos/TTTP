from http import server
from NetworkHandler import NetworkHandler
from NetworkInputInterpreter import NetworkInputInterpreter


TCP = "tcp"
UDP = "udp"
SERVER = "server"
OPPONNET = "opponent"
HOST = "host"
CLIENT = "client"

class NetworkObject:
  def __init__(self, role, protocol, receiver):
    self.last_response = ""
    self.network_input_interpreter = NetworkInputInterpreter(is_server=role==SERVER)
    self.network_handler = NetworkHandler(protocol)
    self.role = role
    self.protocol = protocol
    self.receiver = receiver
    self.socket = None
    self.address = None

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