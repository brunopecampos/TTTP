from Client import Client
import threading

class NetworkReadingThread(threading.Thread):
  def __init__(self, network_handler, client: Client, is_server):
    self.network_handler = network_handler
    self.client = client
    self.is_server = is_server

  def run(self):
    while True:
      new_message = self.server_network_handler.receive_message()
      if self.is_server:
        self.client.update_server_last_response(new_message)
      else:
        self.client.update_opponent_last_response(new_message)