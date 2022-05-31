from NetworkCommand import NO_STATUS, NetworkCommand, SERVER, OPPONENT
import json

SAME_STATE = "same"
POSSIBLE_STATUS = ["200", "400", "401", "403"]

class NetworkInputInterpreter:
  def __init__(self, is_server=True):
    f = open("../data/network_commands.json")
    self.jsonData = json.load(f)
    f.close()
    self.is_server = is_server

  def get_command_next_state(self, label, sender, status, current_state):
    next_state = self.jsonData[label][sender][status]
    if next_state == SAME_STATE:
      return current_state
    return next_state 

  def get_network_command(self, message, current_state):
    lines = message.split('\n')
    header_words = lines[0].split(" ")
    label = header_words[0]
    status = NO_STATUS
    if header_words[1] in POSSIBLE_STATUS:
      status = header_words[1]
    data = ""
    if len(lines) > 1:
      data = lines[1]
    #Case in which a request is receive instead of a response, data 
    if len(lines) == 1 and status == NO_STATUS:
      data = lines[0][5:] #data ignores label
    sender = OPPONENT
    if self.is_server: sender = SERVER
    next_state = self.get_command_next_state(label, sender, status, current_state)
    return NetworkCommand(label, status, data, sender, next_state)
    

