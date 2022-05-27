from Game import Game
from UserInputInterpreter import UserInputInterpreter

class Client():

    def __init__(self) -> None:
        """
        initalize internal object data structures
        """

        self.game = Game()
        self.userInputInterpreter = UserInputInterpreter()

    def main(self):
        """
        run forever, reading user input and executing proper commands
        """

        while True:
            user_input = input("JogoDaVelha> ")
            cmd = self.userInputInterpreter.get_command(user_input)
            self.handle_command(cmd)

    def handle_command(self, cmd):
        """
        decides what to do regarding the requested command
        """

        if self.check_if_can_execute(cmd):
            cmd.execute(self)
        else:
            self.print_error("can't execute command")

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

    def receive_message(self):
        """
        receives a message from the network.
        the message is transformed into a command and then handled properly.
        """

        msg = network_handler.receive_message()
        cmd = NetworkMessageInterpreter.get_command(msg)
        self.handle_command(cmd)
    
    def print_error(self, msg = 'Erro :('):
        """
        prints a error message to the user
        """

        print(msg)

    def new_user(self, username, password):
        pass

    def change_password(self, username, oldpass, newpass):
        pass

    def log_in_user(self, username, password):
        pass

    def get_hall_of_ame(self):
        pass

    def list_connected_users(self):
        pass

    def invite_opponent(self, username):
        pass

    def inform_latency(self):
        pass
    def end_running_game(self):
        pass
    def log_out(self):
        pass
    def end_client_connection(self):
        pass