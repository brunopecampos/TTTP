from NetworkHandler import NetworkHandler
import time
import socket
import signal
from NetworkInputInterpreter import NetworkInputInterpreter

TCP = "tcp"
UDP = "udp"
SERVER = "server"
OPPONNET = "opponent"
HOST = "host"
CLIENT = "client"
BUFFER_SIZE = 1024

class TimeoutException(Exception):
  pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise Exception()

signal.signal(signal.SIGALRM, timeout_handler)

class NetworkObject:
  def __init__(self, role, protocol, receiver):
    self.has_new_message = False
    self.message = ""
    self.network_input_interpreter = NetworkInputInterpreter()
    self.network_handler = NetworkHandler(protocol)
    self.role = role
    self.protocol = protocol
    self.receiver = receiver
    self.socket = None
    self.address = None
    self.end_thread = False
    self.reconnect = False

  def set_new_message(self, message):
    self.has_new_message = True
    self.message = message

  def set_socket(self, socket):
    self.socket = socket

  def set_address(self, address):
    self.address = address

  def send_message(self, message):
    encoded_message = message.encode()
    if self.protocol == TCP:
      self.socket.sendall(encoded_message)
    else:
      self.socket.sendto(encoded_message, self.address)

  def receive_message(self):
    signal.alarm(8) 
    data = ""
    try:
      if self.protocol == TCP:
        data = self.socket.recv(BUFFER_SIZE)
      else: 
        data, address = self.socket.recvfrom(BUFFER_SIZE)
        self.set_address(address)
    except TimeoutException:
      raise TimeoutException
    
    signal.alarm(8) 
    return data.decode()


  def disconnect(self):
    self.socket.close()
  
  def end_socket(self):
    self.socket.shutdown(socket.SHUT_WR)