import random as rnd
import os
import json
import copy

from CheckersView import BOARD_SIZE

class CheckersModel:
    def __init__(self, epsilon=0.95, gamma=0.95, memory_file="checkers_scores.json"):
        self.gamma = gamma
        self.epsilon = epsilon
        self.memory_file = memory_file

        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"
        self.selected = None
        self.history = []

        self.gamemodes = {
            "RANDOM": self.get_random_move,
            "AGENT": self.get_agent_move,
            "GREEDY": self.get_greedy_move
        }

        self.values = self.load_memory()

        self.setup_pieces()

    def setup_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = {"color": "black", "king": False}
                    elif row > 4:
                        self.board[row][col] = {"color": "white", "king": False}

    def print(self):
        symbols = {
            ("white", False): "w",
            ("white", True): "W",
            ("black", False): "b",
            ("black", True): "B",
            None: "."
        }
        for row in self.board:
            print(" ".join(symbols[p["color"], p["king"]] if p else "." for p in row))
        print()

    def board_to_key(self, board):
        key = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece is None:
                    key.append(".")
                else:
                    if piece["color"] == "white":
                        key.append("W" if piece["king"] else "w")
                    else:
                        key.append("B" if piece["king"] else "b")
        return "".join(key)

    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.turn = "white"
        self.history = []
        self.setup_pieces()

        self.history.append(copy.deepcopy(self.board))

    def get_piece(self, row, col):
        return self.board[row][col]

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

        self.history.append(copy.deepcopy(self.board))

    def remove_captured_piece(self,old_row,old_col,new_row,new_col):
        mid_row = (old_row + new_row) // 2
        mid_col = (old_col + new_col) // 2
        self.board[mid_row][mid_col] = None

    def check_valid_move(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

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
                    for new_row, new_col in self.get_moves(row, col):
                        score = self.score_move(row, col, new_row, new_col, color)
                        if score > best_score:
                            best_score = score
                            best_moves = [(row, col, new_row, new_col)]
                        elif score == best_score:
                            best_moves.append((row, col, new_row, new_col))

        return rnd.choice(best_moves) if best_moves else None

    def get_random_move(self, color):
        all_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col):
                        all_moves.append((row, col, new_row, new_col))

        return rnd.choice(all_moves) if all_moves else None

    def get_greedy_move(self, color):
        if rnd.random() < self.epsilon:
            return self.get_random_move(color)

        best_score = -9999
        best_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col):
                        simulated = self.simulate_move(row, col, new_row, new_col)
                        score = self.evaluate_board(simulated)
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
            score += 20

        if not piece["king"]:
            if color == "white" and new_r == 0:
                score += 30
            if color == "black" and new_r == BOARD_SIZE - 1:
                score += 30

        center = BOARD_SIZE // 2
        score += max(0, 4 - abs(new_c - center))

        simulated_board = self.simulate_move(old_r, old_c, new_r, new_c)

        if self.is_risky(simulated_board, new_r, new_c, color):
            score -= 15
        else:
            score += 10
        return score

    def evaluate_board(self, board):
        key = self.board_to_key(board)
        if key in self.values:
            return self.values[key][0]
        return 0.0

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
                    for mover, movec in self.get_moves(row, col, board, enemy):
                        if abs(row - mover) == 2:
                            if (row + mover) // 2 == new_r and (col + movec) // 2 == new_c:
                                return True
        return False

    def has_any_moves(self, color):
        captures = False

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    moves = self.get_moves(row, col)
                    if moves:
                        for move_r, move_c in moves:
                            if abs(row - move_r) == 2:
                                return True
                        captures = True

        return captures

    def check_winner(self):
        white_pieces = 0
        black_pieces = 0

        for row in self.board:
            for piece in row:
                if piece:
                    if piece["color"] == "white":
                        white_pieces += 1
                    else:
                        black_pieces += 1

        if white_pieces == 0:
            return "black"
        if black_pieces == 0:
            return "white"

        white_can_move = self.has_any_moves("white")
        black_can_move = self.has_any_moves("black")

        if black_can_move and not white_can_move:
            return "black"
        if white_can_move and not black_can_move:
            return "white"
        if not white_can_move and not black_can_move:
            return "lock"

        return None

    def score_game(self, winner):
        if winner == "white":
            reward = 1.0
        elif winner == "black":
            reward = -1.0
        else:
            reward = 0.5

        N = len(self.history)

        for i, board in enumerate(self.history):
            discounted = reward * (self.gamma ** (N - i - 1))
            key = self.board_to_key(board)

            if key not in self.values:
                self.values[key] = [discounted, 1]
            else:
                old, count = self.values[key]
                new = (old * count + discounted) / (count + 1)
                self.values[key] = [new, count + 1]

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.values, f, indent=2)

    def play_agent_vs_agent(self, white_play="AGENT", black_play="AGENT", max_moves=500):

        self.reset_game()
        moves = 0

        while moves < max_moves:
            result = self.check_winner()
            if result:
                self.score_game(result)
                return result

            if self.turn == "white":
                move_sel = self.gamemodes[white_play]
            else:
                move_sel = self.gamemodes[black_play]

            move = move_sel(self.turn)

            if not move:
                return self.check_winner()

            self.move_piece(*move)
            moves += 1

        self.score_game("lock")
        return "lock (more moves)"

    def run_tournament(self, rounds=100, white_play="AGENT", black_play="AGENT"):

        results = {"white": 0, "black": 0, "lock": 0, "lock (more moves)": 0}

        for i in range(1, rounds + 1):
            winner = self.play_agent_vs_agent(white_play, black_play)
            results[winner] += 1
            print(f"Game {i}: {winner}")

        print("\nTOURNAMENT RESULTS")
        print("------------------")
        for k, v in results.items():
            print(f"{k.upper()}: {v}")

        return results

if __name__ == "__main__":
    model = CheckersModel()
    model.run_tournament(100, white_play="GREEDY", black_play="GREEDY")
    model.save_memory()
