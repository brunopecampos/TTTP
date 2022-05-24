from cmd import Cmd
import json

from Commands.Command import Command

class UserInputInterpreter:

  def __init__(self):
    f = open("../data/commands.json")
    self.jsonData = json.load(f)
    f.close()

  def get_command_object(self, words):
    command_valid = False
    for cmd in self.jsonData:
      if words[0] == cmd.label:
        command_valid = True
        break
    if not command_valid:
      raise Exception()
    return cmd


  def get_command(self, user_input):
    words = user_input.split()
    # TODO get exception type

    if(len(words) <= 0):
      raise Exception()
    cmd_object = self.get_command_object(words)
    if(len(words) != cmd_object.args + 1):
        raise Exception()
    return  Command(cmd_object.label, words[1:])

