
class Game:
    available_markers = ['O', 'X']
    empty_marker = '-'

    def __init__(self, match_id, send_throught_host):
        _ = Game.empty_marker
        self.board = [
            [_, _, _],
            [_, _, _],
            [_, _, _],
        ]
        self.winner = None
        self.match_id = match_id
        self.send_throught_host = send_throught_host

    def is_valid_move(self, m):
        i, j, marker = m.i, m.j, m.m
        if (i < 0 or 2 < i or j < 0 or 2 < j):
            return False
        return self.board[i][j] == Game.empty_marker

    def record_move(self, m):
        i, j, marker = m.i, m.j, m.m
        self.board[i][j] = marker

    def has_winner(self):
        if self.winner != None:
            return True

        board = self.board
        board_size = 3

        # check rows
        for i in range(board_size):
            row = [[i, j] for j in range(board_size)]
            if equal_markers(board,row):
                self.winner = board[i][0]
                return True

        # check columns
        for j in range(board_size):
            col = [[i, j] for i in range(board_size)]
            if equal_markers(board, col):
                self.winner = board[j][0]
                return True

        # check diagonals
        for i in [0, 1]:
            diag = [[d, (board_size-1) - d] for d in range(board_size)]
            if equal_markers(board, diag):
                self.winner = board[1][1]
                return True

        return False

    def get_winner(self):
        winner = self.winner
        if winner == None:
            raise Exception("")
        return winner

    def __str__(self):
        for i in range(0,3):
            line = self.board[i]
            print(f"{line[0]}|{line[1]}|{line[2]}")
            if i != 2: print("-----")

    def send_move_to_opponent(self, move, client):
        label = "PLAY"
        message = f"PLAY {move.i} {move.j}"
        if self.send_throught_host:
            pass
        else: 
            client.send_command_message(label, message, to_server=False)


################################################################################
# INTERNAL HELPERS

# compare if all positions have the same VALID marker
def equal_markers(board, positions):
    i0, j0 = positions[0][0], positions[0][1]
    first_marker = board[i0][j0]

    if first_marker == Game.empty_marker:
        return False

    for position in positions[1:]:
        i, j = position[0], position[1]
        marker = board[i][j]
        if marker != first_marker:
            return False

    return True
