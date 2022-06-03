from datetime import datetime
import time
import threading

from NetworkObject import NetworkObject

class LatencyTracker:
  def __init__(self, network_handler):
    self.last_mesuraments = []
    self.network_handler = network_handler
  
  def start_tracking(self):
    thread = threading.Thread(self.send_latency_packets)
    thread.start()

  def send_latency_packets(self, network_object):
    while True:
      network_object.send_message("PINL")
      initial_time = datetime.now().timestamp()
      self.last_initial_time = initial_time
      time.sleep(20)

  def send_latency_response(self, network_object):
    arrival_time = datetime.now().timestamp()
    network_object.send_message(f"PINL 200\n{arrival_time}")

  def store_mesurament(self, latency_packet):
    arrival_time = latency_packet.split('\n')[1]
    new_mesurament = self.Latency(self.last_initial_time, arrival_time)
    self.last_mesuraments.append(new_mesurament)

  def __str__(self):
    mesuraments = len(self.last_mesuraments)
    if mesuraments == 0:
      return "No latency mesurament done yet."
    final_srt = ""
    for mesurament in self.last_mesuraments:
      final_srt = final_srt + str(mesurament)

  class Latency:
    def __init__(self, initial_time, arrival_time):
      self.initial_time = initial_time
      self.arrival_time = arrival_time
      self.interval = round((arrival_time - initial_time) * 1000, 2)

    def __str__(self):
      datetime_obj = datetime.utcfromtimestamp(int(self.initial_time))
      datetime_str = datetime_obj.strftime("%H:%M:%S - %d:%m:%y")
      return f"Latency(ms): {self.interval}\nTime of Mesurament: {datetime_str}\n"
