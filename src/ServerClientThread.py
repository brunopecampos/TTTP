import threading
import socket
import time

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
    while True:
      s = None
      try:
        if self.protocol == TCP:
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s.connect((self.host, self.port))
        else:
          s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.network_object.reconnect = False
      except:
        continue
      self.network_object.set_address((self.host, self.port))
      self.network_object.set_socket(s)
      while True:
        self.network_object.socket.settimeout(5)
        if self.network_object.reconnect:
          break 
        if self.network_object.end_thread: 
          return
        try:
          message = self.network_object.receive_message()
          if message == "": 
            self.network_object.socket = None
            self.network_object.reconnect = True
            break
          if message[0:4] == "PING": continue
          self.network_object.set_new_message(message)
        except socket.timeout:
          continue
        except:
          break

      if not self.network_object.reconnect:
        break