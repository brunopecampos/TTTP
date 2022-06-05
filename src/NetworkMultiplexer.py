from NetworkObject import NetworkObject, TCP, UDP, SERVER, OPPONNET, HOST, CLIENT
OPPONENT_HOST = "opponent_host"
SERVER_CLIENT = "server_client"
OPPONENT_CLIENT = "opponent_client"

class NetworkMultiplexer:
  def __init__(self, server_connection_protocol):
    self.opponent_host = NetworkObject(role=HOST, protocol=TCP, receiver=OPPONNET)
    self.server_client= NetworkObject(role=CLIENT, protocol=server_connection_protocol, receiver=SERVER)
    self.opponent_client= NetworkObject(role=CLIENT, protocol=TCP, receiver=OPPONNET)

  def get_network_object(self, object_name):
    if object_name == OPPONENT_HOST:
      return self.opponent_host
    elif object_name == SERVER_CLIENT:
      return self.server_client
    else:
      return self.opponent_client
  