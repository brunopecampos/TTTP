from pickle import TRUE
from User import User
from Command import Command
from NetworkObject import SERVER, OPPONNET
from NetworkMultiplexer import SERVER_CLIENT, OPPONENT_CLIENT, OPPONENT_HOST

class UserCommand(Command):
    def __init__(self, label, next_state, args, send_to):
        super().__init__(label, next_state) 
        self.send_to = send_to
        self.args = args 

    def execute(self, client):
        client.check_and_update_state(self.next_state)

        if self.label == "in":
            new_user = User(self.args[0])
            client.set_current_user(new_user)

        if self.send_to == SERVER:
            label, message = client.user_input_interpreter.get_command_label_and_message(self)
            client.send_command_message(message, label, SERVER_CLIENT)
        elif self.send_to == OPPONNET:
            label, message = client.user_input_interpreter.get_command_label_and_message(self)
            ## change to send via OPPONENT_SERVER too
            print(f"COMMAND LABEL: {self.label}")
            if not label == "PLAY":
                if label == "MEND":
                    if client.is_game_host:
                        print("Ended match.")
                        client.network_multiplexer.get_network_object(OPPONENT_HOST).send_message("MEND 400")
                        client.network_multiplexer.get_network_object(OPPONENT_HOST).socket = None
                        client.check_and_update_state("LOGGED")
                    else:
                        print("Ended match.")
                        client.client_latency_tracker.stop_tracker()
                        client.network_multiplexer.get_network_object(OPPONENT_CLIENT).send_message("MEND 400")
                        client.check_and_update_state("WAIT_END_PLAYING")
                        client.send_command_message(f"MEND {client.game.match_id} -","MEND",SERVER_CLIENT, reconnect=True)
                else:
                    client.send_command_message(message, label, OPPONENT_CLIENT)
            else:
                if not client.game.has_result():
                    client.print_board()
                    print("Waiting for opponent's move...")
                if client.is_game_host:
                    client.send_command_message(message, label, OPPONENT_HOST, endless_wait=True, aditional_label="MEND")
                else: 
                    client.send_command_message(message, label, OPPONENT_CLIENT, endless_wait=True, aditional_label="MEND")
        else:
            if client.is_game_host:
                print("Last 3 mesuraments: ")
                print(client.host_latency_tracker)
            else: 
                print("Last 3 mesuraments: ")
                print(client.client_latency_tracker)