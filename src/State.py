import json

class State:
    def __init__(self):
      self.current_state = "NOT_LOGGED"
      f = open("../data/states.json")
      self.statesData = json.load(f)
      f.close()

    def check_cmd_state(self, cmd):
      next_state = cmd.next_state
      if self.current_state in self.states[next_state]:
        return True
      return False
    
    def update_state(self, cmd): 
      if(self.check_cmd_state(cmd)):
        self.current_state = cmd.next_state
      else:
        raise Exception()
      
    