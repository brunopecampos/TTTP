from NetworkCommand import NO_STATUS, NetworkCommand, SERVER, OPPONENT

import json

SAME_STATE = "same"
POSSIBLE_STATUS = ["200", "201", "400", "401", "403", "404", "409"]

class NetworkInputInterpreter:
  def __init__(self):
    f = open("../data/network_commands.json")
    self.jsonData = json.load(f)
    f.close()

  def get_command_next_state(self, label, sender, status, last_state):

    next_state = self.jsonData[label][sender][status]
    if next_state == SAME_STATE:
      return last_state 
    return next_state 

  def get_network_command(self, message, last_state, sender):
    lines = message.split('\n')
    header_words = lines[0].split(" ")
    label = header_words[0]
    status = NO_STATUS
    if header_words[1] in POSSIBLE_STATUS:
      status = header_words[1]
    data = ""
    if len(lines) > 1:
      data = message[message.index("\n")+1:]
    #Case in which a request is receive instead of a response, data 
    if len(lines) == 1 and status == NO_STATUS:
      data = lines[0][5:] #data ignores label
    next_state = self.get_command_next_state(label, sender, status, last_state)
    return NetworkCommand(label, status, data, sender, next_state)
    

