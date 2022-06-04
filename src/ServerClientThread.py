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
      if self.protocol == TCP:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
      else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.settimeout(5)
      self.network_object.set_address((self.host, self.port))
      self.network_object.set_socket(s)
      while True:
        if self.network_object.end_thread: 
          print("ENDED SERVER CLIENT THREAD")
          return
        try:
          message = self.network_object.receive_message()
          self.network_object.reconnect = False
          if message == "": break
          print(f"MESSAGE IN SERVER CLIENT: {message}")
          if message == "PING 200": continue
          self.network_object.set_new_message(message)
        except socket.timeout:
          if self.network_object.reconnect:
            break 
          continue
        except:
          break

        if not self.network_object.reconnect:
          break
        print("Reconectou")
        time.sleep(20)