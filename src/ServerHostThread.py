import threading
import socket

LOOPBACK = "127.0.0.1"

class ServerHostThread(threading.Thread):
  def __init__(self, network_object, port):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.port = port
  
  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOOPBACK, self.port))
    self.network_object.set_socket(s)
    self.network_object.set_address((LOOPBACK, self.port))
    while True:
      message = self.network_object.receive_message()
      self.network_object.set_last_message(message)
 