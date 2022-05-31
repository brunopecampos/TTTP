import threading
import socket

LOOPBACK = "127.0.0.1"
from LatencyTracker import LatencyTracker

class OpponentHostThread(threading.Thread):
  def __init__(self, network_object, port):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.port = port
  
  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((LOOPBACK, self.port))
    s.listen(1)
    while True:
      conn, addr = self.network_handler.accept_connection()
      self.network_object.set_socket = conn
      self.network_object.set_address = addr
      with conn:
        while True:
          message = self.network_object.receive_message()
          self.network_object.set_last_message(message)
          