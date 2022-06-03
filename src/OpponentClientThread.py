import threading
import socket

from LatencyTracker import LatencyTracker

class OpponentClientThread(threading.Thread):
  def __init__(self, network_object, host, port):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.host = host
    self.port = port
    self.kill = False

  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((self.host, self.port))
    self.network_object.set_socket(s)
    self.network_object.set_address((self.host, self.port))
    while True:
      try:
        message = self.network_object.receive_message()
        if message == "": continue
        self.network_object.set_new_message(message)
        print(f"MESSAGE IN OPPONENT CLIENT: {message}")
        if message == "MEND 200" or message == "CALL 409":
          print("FINALIZED THREAD")
          break
      except:
        continue