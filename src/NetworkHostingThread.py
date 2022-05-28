import threading

from LatencyTracker import LatencyTracker
from NetworkHandler import NetworkHandler, BUFFER_SIZE

class NetworkHostingThread(threading.Thread):
  def __init__(self, network_handler, client):
    threading.Thread.__init__(self)
    self.network_handler = network_handler
    self.client = client
    self.latencyTracker = LatencyTracker(self.network_handler)

  def run(self):
    while True:
      conn, addr = self.network_handler.accept_connection()
      with conn:
        print(f"Connected by {addr}")
        while True:
          new_message = conn.recv(BUFFER_SIZE)
          if self.latencyTracker.is_latency_packet(new_message):
            self.latencyTracker.send_latency_response(conn)
            continue
          self.client.update_host_last_response(new_message)
          