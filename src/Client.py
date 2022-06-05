#!/usr/bin/python3

from Game import Game
from HeartbeatThread import HeartbeatThread
from LatencyTracker import LatencyTracker
from Move import Move
from NetworkCommand import NetworkCommand
from NetworkHandler import NetworkHandler, TCP, UDP
from NetworkInputInterpreter import NetworkInputInterpreter, SERVER, OPPONENT
from OpponentClientThread import OpponentClientThread
from OpponentHostThread import OpponentHostThread
from ServerClientThread import ServerClientThread
from State import SAME, State
from UserInputInterpreter import UserInputInterpreter
from NetworkMultiplexer import NetworkMultiplexer, SERVER_CLIENT, OPPONENT_CLIENT, OPPONENT_HOST
from NetworkObject import SERVER, OPPONNET

from sys import argv
import datetime
import time

#TODO

RESERVED_PORT = 5002


class Client():
    def __init__(self, host, port, protocol, match_hosting_port):
        self.state = State()
        self.user_input_interpreter = UserInputInterpreter()
        self.network_input_interpreter = NetworkInputInterpreter()
        self.network_multiplexer = NetworkMultiplexer(protocol)

        server_host_port = 5003

        self.host_latency_tracker = LatencyTracker(self.network_multiplexer.get_network_object(OPPONENT_HOST))
        self.init_threads(host, port, protocol, server_host_port, match_hosting_port)
        self.new_match_call = False
        self.current_user = None
        self.game = None
        self.is_game_host = False
        self.opponent_player = ""
        self.opponentClientThread = None

    def init_threads(self, host, port, protocol, server_host_port, opponent_host_port):
        server_client_thread = ServerClientThread(self.network_multiplexer.get_network_object(SERVER_CLIENT), host, port, protocol) 
        opponent_host_thread = OpponentHostThread(self.network_multiplexer.get_network_object(OPPONENT_HOST), opponent_host_port, self, self.host_latency_tracker)
        heartbeat_thread = HeartbeatThread(self.network_multiplexer.get_network_object(SERVER_CLIENT))
        server_client_thread.start()
        opponent_host_thread.start()
        self.wait_for_socket_init(SERVER_CLIENT)
        heartbeat_thread.start()
        self.send_hello(opponent_host_port)
    
    def wait_for_socket_init(self, network_label):
        while self.network_multiplexer.get_network_object(network_label).socket == None:
            pass

    def send_hello(self, opponent_host_port):
        self.state.update_state("WAIT_SERVER_HELLO")
        self.send_command_message("HELO", "HELO", SERVER_CLIENT)
        self.send_command_message(f"SADR {opponent_host_port}", "SADR", SERVER_CLIENT)

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
                return "-"

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
            #self.host_latency_tracker.start()
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
        network_object = self.network_multiplexer.get_network_object(network_label)
        timedout = False
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=20)
        while not network_object.has_new_message:
            if datetime.datetime.now() >= endTime and not endless:
                timedout = True
                break
        network_object.has_new_message = False
        return not timedout

    def check_and_update_state(self, next_state):
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
    def send_command_message(self, message, label, network_label, endless_wait = False, aditional_label = "", reconnect=False):
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=180)
        network_obj = self.network_multiplexer.get_network_object(network_label)
        while True:
            if network_obj.socket != None:
                network_obj.send_message(message)
            elif reconnect and datetime.datetime.now() < endTime:
                print("Server not available, trying again in 15 seconds")
                time.sleep(15)
                continue
            if self.check_new_response(network_label, endless=endless_wait):
                new_response = network_obj.message
                sender = SERVER if network_label == SERVER_CLIENT else OPPONENT
                network_cmd = self.network_input_interpreter.get_network_command(new_response, self.state.last_state, sender)
                if network_cmd.is_expected_command(label):
                    network_cmd.execute(self)
                elif network_cmd.is_expected_command(aditional_label):
                    network_cmd.execute(self)
                break
            else:
                print("Timeout. Couldn't reach server")
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
        if cmd.status == "404":
            print("User not found.")
        else:
            opponent_ip = cmd.data.split(" ")[0]
            opponent_port = cmd.data.split(" ")[1]
            # start connection with opponent
            self.opponentClientThread = OpponentClientThread(self.network_multiplexer.get_network_object(OPPONENT_CLIENT), opponent_ip, int(opponent_port)) 
            self.opponentClientThread.start()
            self.wait_for_socket_init(OPPONENT_CLIENT)
            self.check_and_update_state("WAIT_INVITE_OPPONENT")
            self.send_command_message(f"CALL", "CALL", OPPONENT_CLIENT)
        
    def handle_match_call(self, cmd: NetworkCommand):
        self.check_and_update_state(cmd.next_state)
        if cmd.status == "200":
            self.check_and_update_state("WAIT_START_MATCH")
            self.send_command_message(f"MSTR {self.opponent_player}", "MSTR",SERVER_CLIENT)
            self.client_latency_tracker = LatencyTracker(self.network_multiplexer.get_network_object(OPPONENT_CLIENT))
            self.opponentClientThread.set_latency_tracker(self.client_latency_tracker)
            self.client_latency_tracker.start()
        else:
            print("Your call was not accepted by the other player.")
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).disconnect()
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_socket(None)
            self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_address(None)

    def end_itself(self):
        print("Ending client")
        self.network_multiplexer.get_network_object(SERVER_CLIENT).end_thread = True
        self.network_multiplexer.get_network_object(OPPONENT_HOST).end_thread = True
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).end_thread = True
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
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).disconnect()
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_socket(None)
        self.network_multiplexer.get_network_object(OPPONENT_CLIENT).set_address(None)
        if cmd.label == "PLAY" or cmd.status == "200":
            result = self.print_match_end() 
        else:
            print("Your opponent canceled the match.")
            result = '-'
        self.check_and_update_state("WAIT_END_PLAYING")
        self.send_command_message(f"MEND {client.game.match_id} {result}","MEND",SERVER_CLIENT, reconnect=True)

    def print_error(self, msg = 'Erro :('):
        print(msg)


if len(argv) != 4:
    print("invalid number of arguments")
    exit(1)

if argv[4] != "-t" or argv[4] != "-":
    print("Try adding type of connection 'tcp' or 'usp")
    client = Client(argv[1], int(argv[2]), TCP, int(argv[3]))

client.main()