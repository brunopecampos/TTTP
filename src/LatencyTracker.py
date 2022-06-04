from datetime import datetime, timedelta
import time
import threading
from unittest import makeSuite

class LatencyTracker(threading.Thread):
  def __init__(self, network_object):
    threading.Thread.__init__(self)
    self.last_mesuraments = []
    self.stop = False
    self.network_object = network_object
  
  def stop_tracker(self):
    self.stop = True

  def run(self):
    endTime = datetime.now() + timedelta(seconds=1)
    while True:
      if self.network_object.end_thread or self.stop or self.network_object.socket == None: 
        print("Tracker stopped")
        return
      if datetime.now() >= endTime:
        print("SENDED PINL")
        initial_time = datetime.now().timestamp()
        self.network_object.send_message(f"PINL {initial_time}")
        self.last_initial_time = initial_time
        endTime = datetime.now() + timedelta(seconds=30)
      

  def send_latency_response(self, latency_packet):
    arrival_time = datetime.now().timestamp()
    self.network_object.send_message(f"PINL {arrival_time}")
    initial_time = latency_packet.split()[1]
    new_mesurament = self.Latency(float(initial_time), arrival_time)
    print("MANDOU LATENCY RESOPNSE")
    self.last_mesuraments.append(new_mesurament)


  def store_mesurament(self, latency_packet):
    arrival_time = latency_packet.split()[1]
    new_mesurament = self.Latency(self.last_initial_time, float(arrival_time))
    self.last_mesuraments.append(new_mesurament)

  def __str__(self):
    mesuraments = len(self.last_mesuraments)
    if mesuraments == 0:
      return "No latency mesurament done yet."
    final_srt = ""
    for mesurament in self.last_mesuraments:
      final_srt = final_srt + str(mesurament)
    return final_srt

  class Latency:
    def __init__(self, initial_time, arrival_time):
      self.initial_time = initial_time
      self.arrival_time = arrival_time
      self.interval = round((arrival_time - initial_time) * 1000, 2)
      print("Entrou no latency?")

    def __str__(self):
      datetime_obj = datetime.utcfromtimestamp(int(self.initial_time))
      datetime_str = datetime_obj.strftime("%H:%M:%S - %d/%m/%y")
      return f"Latency(ms): {self.interval}\nTime of Mesurament: {datetime_str}\n"
