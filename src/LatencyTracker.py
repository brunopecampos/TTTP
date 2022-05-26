from datetime import datetime
import time

#TODO
class LatencyTracker:

  def __init__(self, network_handler):
    self.last_mesuraments = []
    self.network_handler = network_handler
  
  def check_network_output(self, output):
    splited_output = output.split("\n")
    if len(output) <= 1: return False
    header = output[0].split()
    if len(header) <= 1: return False
    if header[0] != "PINL" or header[0] != "200": return False
    return True

  def start_tracking(self):
    while True:
      self.network_handler.send_message("PINL")
      initial_time = datetime.now().timestamp()
      output = self.network_handler.receive_message()
      if self.check_network_output(output):
        arrival_time = output.split('\n')[1]
        new_mesurament = self.Latency(initial_time, arrival_time)
        self.last_mesuraments.append(new_mesurament)
        time.sleep(20)
      else:
        print("Invalid network response.")

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
