import random as rnd
import os
import json
from CheckersView import BOARD_SIZE

class CheckersModel:
    def __init__(self, gamma=0.95, memory_file="checkers_scores.json"):
        self.gamma = gamma
        self.memory_file = memory_file

        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"
        self.selected = None
        self.history = []

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

    def board_to_key(self):
        key = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is None:
                    key.append(".")
                else:
                    if piece["color"] == "white":
                        key.append("W" if piece["king"] else "w")
                    else:
                        key.append("B" if piece["king"] else "b")
        key.append(self.turn[0])
        return "".join(key)


    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.turn = "white"
        self.history = []
        self.setup_pieces()

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

        self.history.append(self.board_to_key())

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
                    for new_row, new_col in self.get_moves(row, col, board=self.board, color=color):
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
                    for new_row, new_col in self.get_moves(row, col, board=self.board, color=color):
                        all_moves.append((row, col, new_row, new_col))

        return rnd.choice(all_moves) if all_moves else None

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
            reward = 0.0
        else:
            reward = 0.5

        N = len(self.history)
        for i, key in enumerate(self.history):
            discounted = reward * (self.gamma ** (N - i - 1))

            if key not in self.values:
                self.values[key] = [discounted, 1]
            else:
                old, count = self.values[key]
                new = (old * count + discounted) / (count + 1)
                self.values[key] = [new, count + 1]

    def play_agent_vs_agent(self, gamemode="AGENTS", agent_color="white", max_moves=500):
        self.reset_game()
        moves = 0

        while moves < max_moves:
            result = self.check_winner()
            if result:
                self.score_game(result)
                return result

            if gamemode == "RANDOM":
                if self.turn == agent_color:
                    move = self.get_agent_move(self.turn)
                else:
                    move = self.get_random_move(self.turn)
            else:
                move = self.get_agent_move(self.turn)

            if not move:
                return self.check_winner()

            self.move_piece(*move)
            moves += 1

        self.score_game("lock")
        return "lock (more moves)"

    def run_tournament(self, rounds=100, gamemode="AGENTS", agent_color="white"):
        if gamemode == "AGENTS":
            results = {"white": 0, "black": 0, "lock": 0, "lock (more moves)": 0}
        else:
            results = {"agent": 0, "random": 0, "lock": 0, "lock (more moves)": 0}

        for i in range(1, rounds + 1):
            winner = self.play_agent_vs_agent(gamemode, agent_color)

            if gamemode == "AGENTS":
                results[winner] += 1
            else:
                if winner == agent_color:
                    results["agent"] += 1
                elif winner == ("black" if agent_color == "white" else "white"):
                    results["random"] += 1
                else:
                    results[winner] += 1

            print(f"Game {i}: {winner}")

        print("\nTOURNAMENT RESULTS")
        print("------------------")
        for k, v in results.items():
            print(f"{k.upper()}: {v}")

        return results

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.values, f, indent=2)


if __name__ == "__main__":
    model = CheckersModel()
    model.run_tournament(50)
    # model.run_tournament(50, gamemode="RANDOM")
    model.save_memory()

