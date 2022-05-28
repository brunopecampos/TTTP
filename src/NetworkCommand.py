from Command import Command

SERVER = "server"
OPPONENT = "opponnent"
NO_STATUS = " "

class NetworkCommand(Command):
  def __init__(self, label, status, data, sender, next_state):
    super().__init__(label, next_state) 
    self.status = status
    self.data = data
    self.sender = sender

  def is_expected_command(self, label):
    if label == self.label:
      return True
    return False

  def execute(self, client):
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
