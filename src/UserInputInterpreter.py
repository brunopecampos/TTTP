import json

from UserCommand import UserCommand

class UserInputInterpreter:

  def __init__(self):
    f = open("../data/user_commands.json")
    self.jsonData = json.load(f)
    f.close()

  def is_valid_cmd(self, user_input):
    words = user_input.split()
    if len(words) <= 0 :
      return False
    cmd_label = words[0]
    if not (cmd_label in self.jsonData):
      return False
    cmd_object = self.jsonData[words[0]]
    if len(words) != cmd_object['args'] + 1 :
      return False
    return True

  def get_command(self, user_input):
    words = user_input.split()
    cmd_object = self.jsonData[words[0]]
    return  UserCommand(words[0], cmd_object['next_state'], words[1:])

  