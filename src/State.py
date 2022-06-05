import json

SAME = "same"

class State:
    def __init__(self):
      self.last_state = "NOT_CONNECTED_TO_SERVER"
      self.current_state = "NOT_CONNECTED_TO_SERVER"
      f = open("../data/states.json")
      self.states_data = json.load(f)
      f.close()

    def check_state(self, next_state):
      if self.current_state in self.states_data[next_state]:
        return True
      return False
    
    def update_state(self, next_state): 
      self.last_state = self.current_state
      self.current_state = next_state
      
    