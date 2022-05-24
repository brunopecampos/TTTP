from ast import match_case
from pydoc import cli


class Command():
    def __init__(self, label, args):
        self.label = label
        self.args = args

    def execute(self, client):
        if self.label == "new" :
            client.new_user(self.args[0], self.args[1])
        elif self.label == "pass":
            client.change_password(self.args[0], self.args[1])
        elif self.label == "in":
            client.log_in_user(self.args[0], self.args[1])
        elif self.label == "hallofame":
            client.get_hall_of_fame()
        elif self.label == "l":
            client.list_connected_users
        elif self.label == "call":
            client.invite_opponent(self.args[0])
        elif self.label == "play":
            client.play(self.args[0], self.args[1])
        elif self.label == "delay":
            client.inform_latency()
        elif self.label == "over":
            client.end_running_game()
        elif self.label == "out":
            client.log_out()
        elif self.label == "delay":
            client.end_client_connection()
        else:
            # To-do categorize exception
            raise Exception()