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
    
  def set_latency_tracker(self, latency_tracker):
    self.latency_tracker = latency_tracker

  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((self.host, self.port))
    self.network_object.set_socket(s)
    self.network_object.set_address((self.host, self.port))
    while True:
      if self.network_object.end_thread or self.network_object.socket == None: break
      try:
        message = self.network_object.receive_message()
        if message == "": continue
        if message == "PINL": 
          self.latency_tracker.send_latency_response()
          continue
        elif message.split("\n")[0].split(" ")[0] == "PINL":
          self.latency_tracker.store_mesurament(message)
          continue
        self.network_object.set_new_message(message)
        if message == "MEND 200" or message == "CALL 409":
          break
      except:
        continue