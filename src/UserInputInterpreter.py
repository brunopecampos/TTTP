import json

from Commands.Command import Command

class UserInputInterpreter:

  def __init__(self):
    f = open("../data/commands.json")
    self.jsonData = json.load(f)
    f.close()

  def get_command(self, user_input):
    words = user_input.split()
    # TODO get exception type

    if(len(words) <= 0):
      raise Exception()
    cmd_object = self.jsonData[words[0]]
    if(len(words) != cmd_object.args + 1):
        raise Exception()
    return  Command(words[0], words[1:], cmd_object.state)
