from Game import Game
from NetworkHandler import NetworkHandler, TCP, UDP
from NetworkInputInterpreter import NetworkInputInterpreter
from NetworkReadingThread import NetworkReadingThread
from State import State
from UserInputInterpreter import UserInputInterpreter

from sys import argv
import datetime

#TODO

class Client():
    def __init__(self, server_ip, server_port, connection_type):
        """
        initalize internal object data structures
        """

        self.game = Game()
        self.state = State()
        self.user_input_interpreter = UserInputInterpreter()
        self.server_network_input_interpreter = NetworkInputInterpreter()
        self.opponent_network_input_interpreter = NetworkInputInterpreter(is_server=False)
        self.server_last_response = ""
        self.opponent_last_response = ""
        self.server_network_handler = NetworkHandler(TCP)
        self.opponent_network_handler = NetworkHandler(TCP)
        self.init_connection(server_ip, server_port, self.server_network_handler)

    def init_connection(self, host, port, network_handler, is_server=True):
        network_handler.connect(host, port)
        thread = NetworkReadingThread(network_handler, self, is_server)
        thread.start()
        network_handler.send_message("HELO")
    
    def update_server_last_response(self, new_response):
        self.server_last_response = new_response

    def update_opponent_last_response(self, new_response):
        self.opponent_last_response = new_response

    def main(self):
        """
        run forever, reading user input and executing proper commands
        """
        while True:
            user_input = input("JogoDaVelha> ")
            if self.user_input_interpreter.is_valid_cmd(user_input):
                cmd = self.user_input_interpreter.get_command(user_input)
                self.handle_command(cmd)
            else: 
                self.print_error("Invalid Command")

    def check_new_response(self, is_server):
        if is_server:
            current_response = self.server_last_response
        else:
            current_response = self.opponent_last_response
        timedout = False
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while True:
            if is_server:
              if self.server_last_response != current_response:
                break
            else:
              if self.opponent_last_response != current_response:
                break
            if datetime.datetime.now() >= endTime:
                timedout = True
                break
        return not timedout

    def handle_command(self, cmd):
        """
        decides what to do regarding the requested command
        """
        
        if self.state.check_cmd_state(cmd):
            cmd.execute(self)
            self.state.update_state(cmd)
        else:
            self.print_error("Can't execute at this time")

    def play(self, i, j):
        """"
        play a game turn
        """
        new_move = Move(i, j, user.marker)
        if not self.game.is_valid_move(new_move):
            self.print_error("Movimento inválido")
            pass

        # record the move locally
        self.game.record_move(new_move)

        # send move to opponent
        self.send_move(new_move)

        # wait for his response
        self.receive_message()

    def send_move(move):
        """
        send the performed move to the opponent
        """

        command = PlayCommand(move)
        message = command.to_string()
        network_handler.send_message(message)

    def receive_move(move):
        """
        receive move from the opponent
        """

        game = self.game
        network_handler = self.network_handler

        if not game.is_valid_move(move):
            # opponent sent invalid move, meaning his client is malfunctioning,
            # maybe we are out of sync. In any case, we must end the connection.
            self.end_match()
            pass

        # record the move locally
        game.record_move(move)
    
    def print_error(self, msg = 'Erro :('):
        """
        prints a error message to the user
        """

        print(msg)

    #User command handlers
    def send_command_message(self, message, label):
        self.server_network_handler.send_message(message)
        if self.check_new_response(True):
            new_response = self.server_last_response
            network_cmd = self.server_network_input_interpreter.get_network_command(new_response, self.state.current_state)
            if network_cmd.is_expected_command(label):
                network_cmd.execute(self)
        else:
            print("Timeout.")
        pass

    #Network receiving handlers
    def handle_hello(self, cmd):
        pass

    def handle_new_user(self, cmd):
        print("New User!")
        pass
    
    def handle_login(self,cmd):
        pass

    def handle_change_password(self, cmd):
        pass

    def handle_logout(self, cmd):
        pass

    def handle_user_list(self, cmd):
        pass

    def handle_user_hall(self, cmd):
        pass

    def handle_match_end(self, cmd):
        pass
    
    def handle_match_call(self, cmd):
        pass

    def handle_play(self, cmd):
        pass 



if len(argv) != 3:
    print("invalid number of arguments")
    exit(1)

client = Client(argv[1], int(argv[2]), TCP)

client.main()