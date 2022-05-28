from User import User
from Command import Command

class UserCommand(Command):
    def __init__(self, label, next_state, args):
        super().__init__(label, next_state) 
        self.args = args 

    def execute(self, client):
        if self.label == "new":
            new_user = User(self.args[0])
            client.set_current_user(new_user)
        if self.label != "delay":
            label, message = client.user_input_interpreter.get_command_label_and_message(self)
            client.send_command_message(message, label)
        else:
            pass
            #TO-DO ler ultimos delays do LatencyChecker
        