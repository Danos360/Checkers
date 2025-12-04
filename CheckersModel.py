import random as rnd

BOARD_SIZE = 8

class CheckersModel:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_pieces()
        self.selected = None
        self.turn = "white"

    def setup_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = "black"
                    elif row > 4:
                        self.board[row][col] = "white"



    def get_piece(self, row, col):
        return self.board[row][col]

    def get_moves(self, row, col):
        color = self.get_piece(row, col)
        if not color:
            return []

        direction = -1 if color == "white" else 1
        moves = []
        captures = []

        enemy = "black" if color == "white" else "white"

        for coloums in (-1, 1):
            new_row = row + direction
            new_col = col + coloums
            if 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                if self.board[new_row][new_col] is None:
                    moves.append((new_row, new_col))

        for coloums in (-1, 1):
            mid_row = row + direction
            mid_col = col + coloums
            jump_row = row + 2 * direction
            jump_col = col + 2 * coloums

            if (0 <= mid_row < BOARD_SIZE and 0 <= mid_col < BOARD_SIZE and
                    0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE):

                if (self.board[mid_row][mid_col] == enemy and
                        self.board[jump_row][jump_col] is None):
                    captures.append((jump_row, jump_col))

        if captures:
            return captures
        return moves

    def move_piece(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        if abs(old_row - new_row) == 2:
            self.remove_captured_piece(old_row,old_col,new_row,new_col)
        self.turn = "black" if self.turn == "white" else "white"

    def get_agent_move(self, color):
        pieces = [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] == color]
        all_moves = []

        for row, col in pieces:
            moves = self.get_moves(row, col)
            for new_row, new_col in moves:
                all_moves.append((row, col, new_row, new_col))

        if not all_moves:
            return None

        capture_moves = [m for m in all_moves if abs(m[0] - m[2]) == 2]
        if capture_moves:
            return rnd.choice(capture_moves)

        return rnd.choice(all_moves)

    def remove_captured_piece(self,old_row,old_col,new_row,new_col):
        mid_row = (old_row + new_row) // 2
        mid_col = (old_col + new_col) // 2
        self.board[mid_row][mid_col] = None


