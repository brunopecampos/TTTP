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
    s.settimeout(5)
    self.network_object.set_socket(s)
    while True:
      if self.network_object.end_thread: 
        break
      try:
        message = self.network_object.receive_message()
        print(f"MESSAGE IN SERVER CLIENT: {message}")
        self.network_object.set_new_message(message)
      except socket.timeout:
        continue
      except:
        break