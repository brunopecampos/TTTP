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
    return  UserCommand(words[0], cmd_object['next_state'], words[1:], cmd_object['send_to'])

  def get_command_label_and_message(self, cmd):
    cmd_label = cmd.label
    args = cmd.args
    if cmd_label in self.jsonData:
      label = self.jsonData[cmd_label]["network_command"]
      argc = self.jsonData[cmd_label]["args"]
      message = f"{label}"
      for i in range(0, argc):
        arg = args[i]
        if label == "PLAY":
          arg = str(int(arg)-1)
          message = f"{message} {arg}"
        else:
          message = f"{message} {arg}"
      return label, message
    else:
      raise Exception("Unknown user command.")