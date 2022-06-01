import threading
import socket
from typing import Protocol

from LatencyTracker import LatencyTracker
from NetworkObject import TCP, UDP

class ServerClientThread(threading.Thread):
  def __init__(self, network_object, host, port, protocol):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.host = host
    self.port = port
    self.protocol = protocol

  def run(self):
    s = None
    if self.protocol == TCP:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((self.host, self.port))
    else:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.network_object.set_socket(s)
    while True:
      message = self.network_object.receive_message()
      self.network_object.set_last_message(message)