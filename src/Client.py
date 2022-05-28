
from Game import Game
from NetworkCommand import NetworkCommand
from NetworkHandler import NetworkHandler, TCP, UDP
from NetworkHostingThread import NetworkHostingThread
from NetworkInputInterpreter import NetworkInputInterpreter, SERVER, OPPONENT
from NetworkReadingThread import NetworkReadingThread
from State import State
from UserInputInterpreter import UserInputInterpreter

from sys import argv
import datetime

#TODO

RESERVED_PORT = 5000

class Client():
    def __init__(self, server_ip, server_port, connection_type):
        """
        initalize internal object data structures
        """
        self.state = State()
        self.user_input_interpreter = UserInputInterpreter()
        self.server_network_input_interpreter = NetworkInputInterpreter()
        self.opponent_network_input_interpreter = NetworkInputInterpreter(is_server=False)
        self.server_last_response = ""
        self.opponent_last_response = ""
        self.host_last_response = ""
        self.server_network_handler = NetworkHandler(TCP)
        self.opponent_network_handler = NetworkHandler(TCP)
        self.host_network_handler = NetworkHandler(TCP)
        self.init_connection(server_ip, server_port, self.server_network_handler)
        self.init_host()

    def init_connection(self, host, port, network_handler, is_server=True):
        network_handler.connect(host, port)
        thread = NetworkReadingThread(network_handler, self, is_server)
        thread.start()
        if is_server:
            network_handler.send_message("HELO")
        
    def init_host(self):
        self.host_network_handler.listen()
        thread = NetworkHostingThread(self.host_network_handler, self)
        thread.start()
    
    def update_server_last_response(self, new_response):
        self.server_last_response = new_response

    def update_opponent_last_response(self, new_response):
        self.opponent_last_response = new_response

    def update_host_last_response(self, new_response):
        self.host_last_response = new_response

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

    def check_new_response(self, from_server):
        if from_server:
            current_response = self.server_last_response
        else:
            current_response = self.opponent_last_response
        timedout = False
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while True:
            if from_server:
              if self.server_last_response != current_response:
                break
            else:
              if self.opponent_last_response != current_response:
                break
            if datetime.datetime.now() >= endTime:
                timedout = True
                break
        return not timedout

    def check_and_update_state(self, next_state):
        if self.state.check_state(next_state):
            self.state.update_state(next_state)
        else:
            # debug
            print("Não pode mudar de estado agora")

    def handle_command(self, cmd):
        """
        decides what to do regarding the requested command
        """
        
        if self.state.check_state(cmd.next_state):
            cmd.execute(self)
            self.state.update_state(cmd.next_state)
        else:
            self.print_error("Can't execute at this time")

    

    #User command handlers
    def send_command_message(self, message, label, to_server=True):
        if to_server:
            self.server_network_handler.send_message(message)
        else:
            self.opponent_network_handler.send_message(message)
        if self.check_new_response(True, from_server=to_server):
            new_response = ""
            network_cmd = ""
            if to_server:
                new_response = self.server_last_response
                network_cmd = self.server_network_input_interpreter.get_network_command(new_response, self.state.current_state)
            else:
                new_response = self.opponent_last_response
                network_cmd = self.opponent_network_input_interpreter.get_network_command(new_response, self.state.current_state)
            if network_cmd.is_expected_command(label):
                network_cmd.execute(self)
        else:
            print("Timeout.")

    #Network receiving handlers
    def handle_simple_responses(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)

    def handle_auth(self, cmd: NetworkCommand, success_msg, error_msg):
        if cmd.status == "200":
            print(success_msg)
        else:
            print(error_msg)
        self.check_and_update_state(cmd.next_state)

    def handle_lists(self, cmd: NetworkCommand, list_label):
        print(list_label)
        #TODO deserializa data
        data = cmd.data
        print(data)
        self.check_and_update_state(cmd.next_state)

    def handle_match_invite(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)
        opponnet_ip = cmd.data
        # start connection with opponent
        self.init_connection(opponnet_ip, RESERVED_PORT, self.opponent_network_handler, is_server=False)
        self.send_command_message(f"CALL X", "CALL", to_server=False)
        self.check_and_update_state("WAIT_INVITE_OPPONENT")
        
    def handle_match_call(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)
        if cmd.status == 200:
            self.send_command_message(f"MSTR")
            self.check_and_update_state("WAIT_START_MATCH")
        else:
            print("Your call was not accepted by the other player.")
            self.disconnect()

    def handle_match_start(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)
        self.game = Game(cmd.data)

    def handle_play(self, cmd: NetworkCommand):
        pass 

    def handle_match_end(self, cmd: NetworkCommand):
        pass

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


if len(argv) != 3:
    print("invalid number of arguments")
    exit(1)

client = Client(argv[1], int(argv[2]), TCP)

client.main()