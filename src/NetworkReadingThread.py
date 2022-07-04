import threading

from LatencyTracker import LatencyTracker
from NetworkHandler import NetworkHandler

class NetworkReadingThread(threading.Thread):
  def __init__(self, network_handler, client, is_server):
    threading.Thread.__init__(self)
    self.network_handler = network_handler
    self.client = client
    self.is_server = is_server
    if not is_server:
      self.latencyTracker = LatencyTracker(self.network_handler)

  def run(self):
    if not self.is_server:
      LatencyTracker.start_tracking()
    while True:
      new_message = self.network_handler.receive_message()
      if (not self.is_server) and self.latencyTracker.is_latency_packet(new_message):
        self.latencyTracker.store_mesurament(new_message)
        continue
      if self.is_server:
        self.client.update_server_last_response(new_message)
      else:
        self.client.update_opponent_last_response(new_message)