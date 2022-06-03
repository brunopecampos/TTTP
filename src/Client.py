from Game import Game
from Move import Move
from NetworkCommand import NetworkCommand
from NetworkHandler import NetworkHandler, TCP, UDP
from NetworkHostingThread import NetworkHostingThread
from NetworkInputInterpreter import NetworkInputInterpreter, SERVER, OPPONENT
from NetworkReadingThread import NetworkReadingThread
from OpponentClientThread import OpponentClientThread
from OpponentHostThread import OpponentHostThread
from ServerClientThread import ServerClientThread
from ServerHostThread import ServerHostThread
from State import SAME, State
from UserInputInterpreter import UserInputInterpreter
from NetworkMultiplexer import NetworkMultiplexer, SERVER_CLIENT, SERVER_HOST, OPPONENT_CLIENT, OPPONENT_HOST
from NetworkObject import SERVER, OPPONNET

from sys import argv
import datetime
import time

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
        self.is_game_host = False
        self.opponent_player = ""
        self.opponentClientThread = None
        self.host_latency_tracker

    def init_threads(self, host, port, protocol, server_host_port, opponent_host_port):
        server_client_thread = ServerClientThread(self.network_multiplexer.get_network_object(SERVER_CLIENT), host, port, protocol) 
        server_host_thread = ServerHostThread(self.network_multiplexer.get_network_object(SERVER_HOST), server_host_port)
        opponent_host_thread = OpponentHostThread(self.network_multiplexer.get_network_object(OPPONENT_HOST), opponent_host_port, self)
        server_client_thread.start()
        server_host_thread.start()
        opponent_host_thread.start()
        self.wait_for_socket_init(SERVER_CLIENT)
        self.send_hello()
    
    def wait_for_socket_init(self, network_label):
        while self.network_multiplexer.get_network_object(network_label).socket == None:
            pass

    def send_hello(self):
        self.state.update_state("WAIT_SERVER_HELLO")
        self.send_command_message("HELO", "HELO", SERVER_CLIENT)

    def set_current_user(self, new_user):
        self.current_user = new_user

    def delete_current_user(self):
        self.current_user = None

    def main(self):
        while True:
            if self.state.current_state == "PLAYING":
                self.print_board()
            user_input = input("JogoDaVelha> ")   
            self.handle_user_input(user_input)

    def print_match_result_and_get_result(self):
        if self.game.has_result():
            if self.game.winner == 'X':
                if self.is_game_host:
                    print("Unfortunately, you lost!")
                else:
                    print("Congratulations, you won!")
                return "X"
            elif self.game.winner == 'O':
                if self.is_game_host:
                    print("Congratulations, you won!")
                else:
                    print("Unfortunately, you lost!")
                return "O"
            else:
                print("That's a tie!")
                return "T"

    def print_board(self):
        print("Game Board: \n")
        print(str(self.game))
        print("")

    def handle_user_input(self, user_input):
        if self.new_match_call:
            self.handle_incoming_invite(user_input)
        else:
            if self.user_input_interpreter.is_valid_cmd(user_input):
                if user_input.split(" ")[0] == "play":
                    move = Move(int(user_input.split(" ")[1]) , int(user_input.split(" ")[2]), self.current_user.marker)
                    if not self.game.is_valid_move(move):
                        print("Invalid move. Try again")
                        return
                    else:
                        self.game.record_move(move)
                if user_input.split(" ")[0] == "call":
                    self.opponent_player = user_input.split(" ")[1]
                cmd = self.user_input_interpreter.get_command(user_input)
                self.handle_command(cmd)
            else: 
                self.print_error("Invalid Command")

    def handle_incoming_invite(self, user_response):
        self.new_match_call = False
        opponent_host = self.network_multiplexer.get_network_object(OPPONENT_HOST)
        if user_response == 'y':
            print("Waiting for opponent's move...")
            self.check_and_update_state("PLAYING")
            self.check_and_update_state("WAIT_SEND_MOVE")
            opponent_host.send_message("CALL 200")
            self.is_game_host = True
            self.game = Game("") #doesnt need to access matchid
            self.current_user.set_user_marker('O') # who invited will start
            if self.check_new_response(OPPONENT_HOST, endless=True):
                network_obj = self.network_multiplexer.get_network_object(OPPONENT_HOST)
                new_response = network_obj.message
                sender = OPPONENT
                network_cmd = self.network_input_interpreter.get_network_command(new_response, self.state.last_state, sender)
                if network_cmd.is_expected_command("PLAY") or network_cmd.is_expected_command("MEND"):
                    network_cmd.execute(self)   
        else :
            opponent_host.send_message("CALL 409")

    def check_new_response(self, network_label, endless=False):
        print(f"ENDLESS: {endless}")
        network_object = self.network_multiplexer.get_network_object(network_label)
        timedout = False
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=10)
        while not network_object.has_new_message:
            if datetime.datetime.now() >= endTime and not endless:
                timedout = True
                break
        network_object.has_new_message = False
        return not timedout

    def check_and_update_state(self, next_state):
        print(f"TRY TO CHANGE TO STATE: {next_state}")
        if self.state.check_state(next_state):
            self.state.update_state(next_state)
        else:
            # debug
            print("Não conseguiu mudar de estado.")

    def handle_command(self, cmd):
        if self.state.check_state(cmd.next_state):
            cmd.execute(self)
        else:
            self.print_error("Can't execute at this time")

    #User command handlers
    def send_command_message(self, message, label, network_label, endless_wait = False, aditional_label = ""):
        network_obj = self.network_multiplexer.get_network_object(network_label)
        while True:
            print("MANDANDO MENSAGEM")
            network_obj.send_message(message)
            if self.check_new_response(network_label):
                new_response = network_obj.message
                sender = SERVER if network_label == SERVER_CLIENT or network_label == SERVER_HOST else OPPONENT
                network_cmd = self.network_input_interpreter.get_network_command(new_response, self.state.last_state, sender)
                if network_cmd.is_expected_command(label):
                    network_cmd.execute(self)
                elif network_cmd.is_expected_command(aditional_label):
                    network_cmd.execute(self)
                break
            else:
                if endless_wait: continue
                print("Timeout.")
                break

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
        opponent_ip = cmd.data.split(" ")[0]
        opponent_port = cmd.data.split(" ")[1]
        # start connection with opponent
        print(f"OPPONENT CLENT IP: {opponent_ip} PORT: {opponent_port}")
        self.opponentClientThread = OpponentClientThread(self.network_multiplexer.get_network_object(OPPONENT_CLIENT), opponent_ip, int(opponent_port))
        self.opponentClientThread.start()
        self.wait_for_socket_init(OPPONENT_CLIENT)
        self.check_and_update_state("WAIT_INVITE_OPPONENT")
        self.send_command_message(f"CALL", "CALL", OPPONENT_CLIENT, endless_wait=True)
        
    def handle_match_call(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)
        if cmd.status == "200":
            self.check_and_update_state("WAIT_START_MATCH")
            self.send_command_message(f"MSTR {self.opponent_player}", "MSTR",SERVER_CLIENT)
        else:
            print("Your call was not accepted by the other player.")
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).disconnect()
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_socket(None)
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_address(None)
            #self.opponentClientThread.join()

    def end_itself(self):
        print("Ending client")
        self.network_multiplexer.get_network_object(SERVER_HOST).end_thread = True
        self.network_multiplexer.get_network_object(SERVER_CLIENT).end_thread = True
        self.network_multiplexer.get_network_object(OPPONENT_HOST).end_thread = True
        exit(0)

    def handle_match_start(self, cmd: NetworkCommand):
        self.game = Game(cmd.data)
        self.is_game_host = False
        self.current_user.set_user_marker('X') # who invited will start
        self.check_and_update_state(cmd.next_state)

    def handle_play(self, cmd: NetworkCommand):
        if cmd.status == "200":
            self.check_and_update_state(cmd.next_state)
        else:
            self.check_and_update_state(cmd.next_state)
            words = cmd.data.split(" ")
            i, j = int(words[0]) + 1, int(words[1]) + 1
            self.game.record_move(Move(i, j, 'X' if self.is_game_host else 'O'))
            print(f"Opponent played in: {i} {j}")
            if self.game.has_result():
                if self.is_game_host:
                    self.network_multiplexer.get_network_object(OPPONENT_HOST).send_message("MEND 200")
                    self.handle_host_match_end(cmd)
                else:
                    self.network_multiplexer.get_network_object(OPPONENT_CLIENT).send_message("MEND 200")
                    self.handle_client_match_end(cmd)
                    
            #TODO envia o mensagem pelo HOST
    
    def handle_match_end_response(self, cmd: NetworkCommand):
        if cmd.sender == SERVER:
            self.check_and_update_state(cmd.next_state)
        else:
            if self.is_game_host:
                self.handle_host_match_end(cmd)
            else: 
                self.handle_client_match_end(cmd)

    def print_match_end(self):
        result = self.print_match_result_and_get_result()
        print("Final board state: \n")
        print(str(self.game))
        print("Updated your score in the server.")
        return result

    def handle_host_match_end(self, cmd):
        if cmd.label == "PLAY" or cmd.status == "200":
            self.print_match_end()
        else:
            print("Your opponent canceled the match.")
        if self.state.current_state == "WAIT_SEND_MOVE":
            self.check_and_update_state("PLAYING")
        self.check_and_update_state("LOGGED")
        self.network_multiplexer.get_network_object(OPPONENT_HOST).socket = None


    def handle_client_match_end(self, cmd):
        print("CLIENT MATCH END")
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).disconnect()
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_socket(None)
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_address(None)
        if cmd.label == "PLAY" or cmd.status == "200":
            result = self.print_match_end() 
        else:
            print("Your opponent canceled the match.")
            result = 'E'
        self.check_and_update_state("WAIT_END_PLAYING")
        self.send_command_message(f"MEND {client.game.match_id} {result}","MEND",SERVER_CLIENT)

    def print_error(self, msg = 'Erro :('):
        print(msg)


if len(argv) != 3:
    print("invalid number of arguments")
    exit(1)

client = Client(argv[1], int(argv[2]), TCP)

client.main()