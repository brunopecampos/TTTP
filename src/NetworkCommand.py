from Client import Client
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

  def execute(self, client: Client):
    if self.label == "HELO":
      client.handle_simple_responses(self)
      client.handle_hello(self)
    # Only server-wise
    elif self.label == "NUSR":
      client.handle_auth(self, success_msg="User created.", error_msg="Couldn't create user. Username already taken.")
    elif self.label == "LOGN":
      if self.status != "200": client.delete_current_user()
      client.handle_auth(self, success_msg="Logged in.", error_msg="Couldn't log in. Try another username or password.")
    elif self.label == "CPWD":
      client.handle_auth(self, success_msg="Changed password.", error_msg="Couldn't change password. Try another username or password.")
    elif self.label == "LOUT":
      if self.status == "200": client.delete_current_user()
      client.handle_simple_responses()
    elif self.label == "USRL":
      client.handle_lists(self, "User List:")
    elif self.label == "UHOP":
      client.handle_lists(self, "Hall Of Fame:")
    elif self.label == "GTIP":
      client.handle_match_invite(self)
    # Only client-wise
    elif self.label == "CALL":
      client.handle_match_call(self)
    elif self.label == "MSTR":
      client.handle_match_start(self)
    elif self.label == "PLAY":
      client.handle_play(self)
    elif self.label == "MEND":
      client.handle_match_end(self)
    else:
      raise Exception("Unknown received packet")
