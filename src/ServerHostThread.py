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
    s.settimeout(5)

    while True:
      try:
        s.bind((LOOPBACK, self.port))
        break
      except OSError:
        self.port = self.port+1

    self.network_object.set_socket(s)
    self.network_object.set_address((LOOPBACK, self.port))
    while True:
      if self.network_object.end_thread: 
        print("ENDED SERVER HOST THREAD")
        break
      try:
        message = self.network_object.receive_message()
        self.network_object.set_new_message(message)
      except socket.timeout:
        continue
      except:
        break
