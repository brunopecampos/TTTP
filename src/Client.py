from Game import Game

class Client():

    def __init__(self) -> None:
        """
        initalize internal object data structures
        """

        self.game = Game()

    def main(self):
        """
        run forever, reading user input and executing proper commands
        """

        while True:
            user_input = input()
            cmd = UserInputInterpreter.get_command(user_input)
            self.handle_command(cmd)

    def handle_command(self, cmd):
        """
        decides what to do regarding the requested command
        """

        if self.check_if_can_execute(cmd):
            cmd.execute(self)
        else:
            self.print_error("can't execute command")

    def play(self, move):
        """"
        play a game turn
        """

        if not self.game.is_valid_move(move):
            self.print_error("Movimento inválido")
            pass

        # record the move locally
        self.game.record_move(move)

        # send move to opponent
        self.send_move(move)

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
