from Game import Game
from Move import Move
from NetworkCommand import NetworkCommand
from NetworkHandler import NetworkHandler, TCP, UDP
from NetworkHostingThread import NetworkHostingThread
from NetworkInputInterpreter import NetworkInputInterpreter, SERVER, OPPONENT
from NetworkReadingThread import NetworkReadingThread
from OpponentHostThread import OpponentHostThread
from ServerClientThread import ServerClientThread
from ServerHostThread import ServerHostThread
from State import State
from UserInputInterpreter import UserInputInterpreter
from NetworkMultiplexer import NetworkMultiplexer, SERVER_CLIENT, SERVER_HOST, OPPONENT_CLIENT, OPPONENT_HOST
from NetworkObject import SERVER, OPPONNET

from sys import argv
import datetime

#TODO

RESERVED_PORT = 5002

class Client():
    def __init__(self, host, port, protocol):
        self.state = State()
        self.user_input_interpreter = UserInputInterpreter()
        self.network_input_interpreter = NetworkInputInterpreter()
        self.network_multiplexer = NetworkMultiplexer(protocol)

        #### get unused port
        server_host_port = 5003
        opponent_host_port = 5004

        self.init_threads(host, port, protocol, server_host_port, opponent_host_port)
        self.new_match_call = False
        self.current_user = None
        self.game = None

    def init_threads(self, host, port, protocol, server_host_port, opponent_host_port):
        server_client_thread = ServerClientThread(self.network_multiplexer.get_network_object(SERVER_CLIENT), host, port, protocol) 
        server_host_thread = ServerHostThread(self.network_multiplexer.get_network_object(SERVER_HOST), server_host_port)
        opponent_host_thread = OpponentHostThread(self.network_multiplexer.get_network_object(OPPONENT_HOST), opponent_host_port)
        server_client_thread.start()
        server_host_thread.start()
        opponent_host_thread.start()
        self.send_hello()

    def send_hello(self):
        self.network_multiplexer.get_network_object(SERVER_CLIENT).send_message("HELO") 

    def set_current_user(self, new_user):
        self.current_user = new_user

    def delete_current_user(self):
        self.current_user = None

    def main(self):
        while True:
            if self.state.current_state != "PLAYING":
                user_input = input("JogoDaVelha> ")   
                self.handle_user_input(user_input)
            else:
                print("Situação do jogo: ")
                print(str(self.game))
                move = self.get_move_from_input()
                self.game.record_move(move)
                self.game.send_move_to_opponent(move, self)

    def get_move_from_input(self):
        while True:
            i = input("Digite a linha da sua jogada:")
            j = input("Digite a coluna da sua jogada: ")
            move = Move(i, j, self.current_user.marker)
            if self.game.is_valid_move(move): return move

    def handle_user_input(self, user_input):
        if self.new_match_call:
            self.handle_incoming_invite(user_input)
        else:
            if self.user_input_interpreter.is_valid_cmd(user_input):
                cmd = self.user_input_interpreter.get_command(user_input)
                self.handle_command(cmd)
            else: 
                self.print_error("Invalid Command")

    def handle_incoming_invite(self, user_response):
        self.new_match_call = False
        if user_response == 'y':
            self.host_network_handler.send_message_to_client("CALL 200")
            self.check_and_update_state("PLAYING")
        else :
            self.host_network_handler.send_message_to_client("CALL 409")

    def check_new_response(self, network_label):
        network_object = self.network_multiplexer.get_network_object(network_label)
        current_response = network_object.last_message
        timedout = False
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while True:
            if current_response != network_object.last_message: break
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
        if self.state.check_state(cmd.next_state):
            cmd.execute(self)
            self.state.update_state(cmd.next_state)
        else:
            self.print_error("Can't execute at this time")

    #User command handlers
    def send_command_message(self, message, label, network_label):
        network_obj = self.network_multiplexer.get_network_object(network_label)
        network_obj.send_message(message)
        if self.check_new_response(True, network_label):
            new_response = network_obj.last_message
            sender = SERVER if network_label == SERVER_CLIENT or network_label == SERVER_HOST else OPPONENT
            network_cmd = self.server_network_input_interpreter.get_network_command(new_response, self.state.current_state, sender)
            if network_cmd.is_expected_command(label):
                network_cmd.execute(self)
        else:
            print("Timeout.")

    #Network receiving handlers
    def handle_simple_responses(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)

    def handle_auth(self, cmd: NetworkCommand, success_msg, error_msg, set_new_user=False):
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
        self.game = Game(cmd.data)
        self.current_user.set_user_marker('X') # who invited will start
        self.check_and_update_state(cmd.next_state)

    def handle_play(self, cmd: NetworkCommand):
        if cmd.status == "200":
            self.check_and_update_state(cmd.next_state)
        else:
            words = cmd.data.split(" ")
            i, j = words[0], words[1]
            self.game.record_move(i, j, 'O')
            #TODO envia o mensagem pelo HOST


    def handle_match_end(self, cmd: NetworkCommand):
        pass
    
    def print_error(self, msg = 'Erro :('):
        print(msg)


if len(argv) != 3:
    print("invalid number of arguments")
    exit(1)

client = Client(argv[1], int(argv[2]), TCP)

client.main()