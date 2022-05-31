import threading
import socket

from LatencyTracker import LatencyTracker

class OpponentClientThread(threading.Thread):
  def __init__(self, network_object, host, port):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.host = host
    self.port = port

  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(self.host, self.port)
    while True:
      message = self.network_object.receive_message()
      self.network_object.set_last_message(message)