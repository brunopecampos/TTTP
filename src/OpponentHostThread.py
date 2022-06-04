import threading
import socket

LOOPBACK = "127.0.0.1"

class OpponentHostThread(threading.Thread):
  def __init__(self, network_object, port, client, latency_tracker):
    threading.Thread.__init__(self)
    self.network_object = network_object
    self.port = port
    self.client = client
    self.latency_traker = latency_tracker

  def is_match_call(self, message):
    if message[0:4] == "CALL": return True
    return False
  
  def run(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.bind((LOOPBACK, self.port))
    print(f"HOSTING PORT: {self.port}")
    s.listen(1)
    while True:
      try:
        conn, addr = s.accept()
      except socket.timeout:
        if self.network_object.end_thread:
          print("ENDED OPPONENT HOST THREAD")
          break
        continue
      conn.settimeout(3)
      print("CONEXAO OPPONENT HOST")
      self.network_object.set_socket(conn)
      self.network_object.set_address(addr)
      while True:
        if self.network_object.socket == None: break
        try:
          #print("LENDO MENSAGEM")
          message = self.network_object.receive_message()
          if message == "": break
          print(f"OPPONENT HOST RECEIVED: {message}")
          if message[0:4] == "PINL": 
            self.latency_traker.send_latency_response(message)
            print("Deu continue")
            continue
          if self.is_match_call(message):
              self.client.new_match_call = True
              print("You have just received a match invitation. Do you want to accept it (y or n):", end=" ")
          else:
            self.network_object.set_new_message(message)
        except socket.timeout:
          continue
        except:
          break
    
          