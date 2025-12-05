import random as rnd
from CheckersView import BOARD_SIZE

class CheckersModel:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.setup_pieces()
        self.turn = "white"
        self.selected = None

    def setup_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = {"color": "black", "king": False}
                    elif row > 4:
                        self.board[row][col] = {"color": "white", "king": False}

    def move_piece(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        if piece is None:
            return

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        if abs(old_row - new_row) == 2:
            self.remove_captured_piece(old_row, old_col, new_row, new_col)

        self.check_make_king(new_row, new_col)

        self.turn = "black" if self.turn == "white" else "white"

    def remove_captured_piece(self,old_row,old_col,new_row,new_col):
        mid_row = (old_row + new_row) // 2
        mid_col = (old_col + new_col) // 2
        self.board[mid_row][mid_col] = None

    def check_make_king(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return

        if piece["color"] == "black" and row == BOARD_SIZE - 1:
            piece["king"] = True

        if piece["color"] == "white" and row == 0:
            piece["king"] = True

    def get_moves(self, row, col):
        piece = self.get_piece(row, col)

        if not piece or piece["color"] != self.turn:
            return []

        color = piece["color"]
        enemy_color = "black" if color == "white" else "white"

        if piece["king"]:
            directions = (-1, 1)
        else:
            directions = (-1,) if color == "white" else (1,)

        moves = []
        captures = []

        for row_direction in directions:
            for col_direction in (-1, 1):
                new_row = row + row_direction
                new_col = col + col_direction

                if self.check_valid_move(new_row, new_col):
                    if self.board[new_row][new_col] is None:
                        moves.append((new_row, new_col))

        for row_direction in directions:
            for col_direction in (-1, 1):
                mid_row = row + row_direction
                mid_col = col + col_direction
                jump_row = row + 2 * row_direction
                jump_col = col + 2 * col_direction

                if self.check_valid_move(mid_row, mid_col) and self.check_valid_move(jump_row, jump_col):
                    mid_piece = self.board[mid_row][mid_col]
                    if mid_piece and mid_piece["color"] == enemy_color:
                        if self.board[jump_row][jump_col] is None:
                            captures.append((jump_row, jump_col))

        if captures:
            return captures
        return moves

    def get_agent_move(self, color):
        all_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col):
                        all_moves.append((row, col, new_row, new_col))

        if not all_moves:
            return None

        capture_moves = [move for move in all_moves if abs(move[0] - move[2]) == 2]
        if capture_moves:
            return rnd.choice(capture_moves)

        return rnd.choice(all_moves)

    def check_winner(self):
        white = 0
        black = 0
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    if piece["color"] == "white":
                        white += 1
                    else:
                        black += 1

        if white == 0:
            return "black"
        if black == 0:
            return "white"
        return None

    def check_valid_move(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get_piece(self, row, col):
        return self.board[row][col]


