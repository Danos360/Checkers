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

    def get_piece(self, row, col):
        return self.board[row][col]

    def check_valid_move(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def move_piece(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        if not piece:
            return

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        if abs(old_row - new_row) == 2:
            self.remove_captured_piece(old_row, old_col, new_row, new_col)

        self.check_make_king(new_row, new_col)
        self.turn = "black" if self.turn == "white" else "white"

    def get_moves(self, row, col, board=None, color=None):
        if board is None:
            board = self.board
        piece = board[row][col]

        if not piece:
            return []

        if color is None:
            color = piece["color"]

        enemy_color = "black" if color == "white" else "white"

        if piece["king"]:
            directions = (-1, 1)
        else:
            directions = (-1,) if color == "white" else (1,)

        moves = []
        captures = []

        for directr in directions:
            for directc in (-1, 1):
                newr, newc = row + directr, col + directc
                if self.check_valid_move(newr, newc) and board[newr][newc] is None:
                    moves.append((newr, newc))

                jumpr, jumpc = row + 2 * directr, col + 2 * directc
                if self.check_valid_move(jumpr, jumpc):
                    mid = board[row + directr][col + directc]
                    if mid and mid["color"] == enemy_color and board[jumpr][jumpc] is None:
                        captures.append((jumpr, jumpc))

        return captures if captures else moves

    def get_agent_move(self, color):
        best_score = -9999
        best_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col, board=self.board, color=color):
                        score = self.score_move(row, col, new_row, new_col, color)

                        if score > best_score:
                            best_score = score
                            best_moves = [(row, col, new_row, new_col)]
                        elif score == best_score:
                            best_moves.append((row, col, new_row, new_col))

        return rnd.choice(best_moves) if best_moves else None

    def score_move(self, old_r, old_c, new_r, new_c, color):
        score = 0
        piece = self.board[old_r][old_c]

        if abs(old_r - new_r) == 2:
            score += 15

        if not piece["king"]:
            if color == "white" and new_r == 0:
                score += 25
            if color == "black" and new_r == BOARD_SIZE - 1:
                score += 25

        simulated_board = self.simulate_move(old_r, old_c, new_r, new_c)

        if self.is_risky(simulated_board, new_r, new_c, color):
            score -= 30
        else:
            score += 5

        score += 1

        # print(f"{(old_row, old_col)} to {(new_row, new_col)} with score = {score}")
        return score

    def check_make_king(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return

        if piece["color"] == "black" and row == BOARD_SIZE - 1:
            piece["king"] = True

        if piece["color"] == "white" and row == 0:
            piece["king"] = True


    def simulate_move(self, old_r, old_c, new_r, new_c):
        new_board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col]:
                    new_board[row][col] = self.board[row][col].copy()

        piece = new_board[old_r][old_c]
        new_board[old_r][old_c] = None
        new_board[new_r][new_c] = piece

        if abs(old_r - new_r) == 2:
            mid_r = (old_r + new_r) // 2
            mid_c = (old_c + new_c) // 2
            new_board[mid_r][mid_c] = None

        return new_board

    def is_risky(self, board, new_r, new_c, color):
        enemy = "black" if color == "white" else "white"

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece and piece["color"] == enemy:
                    moves = self.get_moves(row, col, board, enemy)
                    for mover, movec in moves:
                        if abs(row - mover) == 2:
                            if (row + mover) // 2 == new_r and (col + movec) // 2 == new_c:
                                return True
        return False

    def remove_captured_piece(self,old_row,old_col,new_row,new_col):
        mid_row = (old_row + new_row) // 2
        mid_col = (old_col + new_col) // 2
        self.board[mid_row][mid_col] = None

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

