import time

class LatencyTracker:

  def __init__(self, network_handler):
    self.last_mesuraments = [-1.0, -1.0, -1.0]
    self.network_handler = network_handler

  
  def start_tracking(self):
    while True:
      #TODO send packet with netowrk handler
      #self.network_handler.send_message_to_client("PINL")
      #time = self.network_handler.get_receive_message()
      #time = time.split('\n')[1]
      self.last_mesuraments.insert(0, Latency())
      time.sleep(5)



  class Latency:
    def __init__(self, initial_time, last_time):
      self.initial_time = initial_time
      self.last_time = last_time
