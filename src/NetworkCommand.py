from distutils.cmd import Command
from http import server
import json
from Client import Client

SERVER = "server"
OPPONENT = "opponnent"
NO_STATUS = " "
SAME_STATE = "same"

class NetworkCommand(Command):
  def __init__(self, label, status, data, sender, previous_state):
    self.status = status
    self.data = data
    self.sender = sender
    f = open("../data/user_commands.json")
    self.jsonData = json.load(f)
    f.close()
    next_state = self.get_next_state(label, previous_state)
    super().__init__(label, next_state) 

  def get_next_state(self, label, previous_state):
    next_state = self.jsonData[label][self.sender][self.status]
    if next_state == SAME_STATE:
      return previous_state
    return next_state 

  def is_expected_command(self, label, sender, status):
    if not ((label == self.label)):
      return True
    return False

  def execute(self, client: Client):
    if self.label == "HELO":
      client.handle_hello(self)
    elif self.label == "NUSR":
      client.handle_new_user(self)
    elif self.label == "LOGN":
      client.handle_login(self)
    elif self.label == "CPWD":
      client.handle_change_password(self)
    elif self.label == "LOUT":
      client.handle_logout(self)
    elif self.label == "USRL":
      client.handle_user_list(self)
    elif self.label == "UHOP":
      client.handle_user_hall(self)
    elif self.label == "MEND":
      client.handle_match_end(self)
    elif self.label == "CALL":
      client.handle_match_call
    elif self.label == "PLAY":
      client.handle_play
    else:
      raise Exception("Unknown received packet")
