from email import message
import threading

from LatencyTracker import LatencyTracker
from NetworkHandler import NetworkHandler, BUFFER_SIZE

class NetworkHostingThread(threading.Thread):
  def __init__(self, network_handler, client):
    threading.Thread.__init__(self)
    self.network_handler = network_handler
    self.client = client
    self.latencyTracker = LatencyTracker(self.network_handler)
  
  def is_match_call(message):
    if message.split(" ")[0] == "CALL": return True
    return False

  def run(self):
    while True:
      conn, addr = self.network_handler.accept_connection()
      with self.network_handler.current_conn:
        print(f"Connected by {self.network_handler.current_addr}")
        while True:
          new_message = self.network_handler.receive_message_from_client()
          if self.latencyTracker.is_latency_packet(new_message):
            self.latencyTracker.send_latency_response(conn)
            continue
          if self.is_match_call(new_message):
            self.client.new_match_call = True
            inviter = new_message.split(" ")[1]
            print("You have just received a match invitation from {inviter}. Do you want to accept it (y or n): ")
          self.client.update_host_last_response(new_message)
          