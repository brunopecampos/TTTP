class Game:
    available_markers = ['O', 'X']
    empty_marker = '-'

    def __init__(self) -> None:
        _ = Game.empty_marker

        self.board = [
            [_, _, _],
            [_, _, _],
            [_, _, _],
        ]
        self.winner = None

    def is_valid_move(self, m) -> bool:
        i, j, marker = m.i, m.j, m.m

        # ensure indexes are not out of bound
        if (i < 1 or 3 < i or j < 1 or 3 < j):
            raise Exception()

        # ensure marker is correct
        if marker not in Game.available_markers:
            raise Exception()

        # correct indexes for boards access
        i = i-1
        j = j-1

        return self.board[i][j] == Game.empty_marker

    def record_move(self, m) -> None:
        if not self.is_valid_move(m):
            raise Exception("")

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

################################################################################
# INTERNAL HELPERS

def equal_markers(board, pairs):
    i0, j0 = pairs[0][0], pairs[1][0]
    first_item = board[i0][j0]
    for pair in pairs[1:]:
        i, j = pair[0], pair[1]
        item = board[i][j]
        if item != first_item:
            return False
    return True
