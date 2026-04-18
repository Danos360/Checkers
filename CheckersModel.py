import random as rnd
import os
import json
import copy
import statistics
from statistics import stdev

import torch

from CheckersView import BOARD_SIZE
from CheckersNN import CheckersNet

MEMORY_FILE_PATH = "CheckersData/checkers_score_huristic6x6.json"
NN_MODEL_FILE_PATH = "CheckersData/best_model6x6.pth"

class CheckersModel:
    """
    Initialize the Checkers model.

    Handles:
    - Board state
    - Move generation
    - Game rules
    - Agent strategies (random, greedy, heuristic, neural network)
    - Reinforcement learning memory

    :param epsilon - Exploration rate for epsilon-greedy strategy
    :type epsilon: float

    :param gamma - Discount factor for future rewards.
    :type gamma: float

    :param memory_file - Path to stored board evaluations.
    :type memory_file: str

    :param nn_model_file - Path to trained neural network weights file.
    :type nn_model_file: str
    """
    def __init__(self, epsilon=0.95, gamma=0.95, memory_file=MEMORY_FILE_PATH, nn_model_file=NN_MODEL_FILE_PATH):
        self.gamma = gamma
        self.epsilon = epsilon
        self.memory_file = memory_file

        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"
        self.selected = None
        self.history = []
        self.count = 0

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.nn = CheckersNet().to(self.device)

        if os.path.exists(nn_model_file):
            self.model = torch.load(nn_model_file, map_location=self.device)
            self.nn.load_state_dict(self.model["model"])
            self.nn.eval()
            print("Loaded NN model")
        else:
            print("NN model not found")


        self.gamemodes = {
            "RANDOM": self.get_random_move,
            "AGENT": self.get_agent_move,
            "GREEDY": self.get_greedy_move,
            "GREEDY_NN": self.get_greedy_nn_move
        }

        self.values = self.load_memory()
        self.setup_pieces()

    """
    Initialize the board with starting positions for both players.
    """
    def setup_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    if row < 2:
                        self.board[row][col] = {"color": "black", "king": False}
                    elif row > BOARD_SIZE - 3:
                        self.board[row][col] = {"color": "white", "king": False}


    """
    Prints the current board state to the console.
    """
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

    """
    Convert a board state to an unique string key.
        
    :param board - martix 2D list representing the board.
    :type board: list
    
    :returns - String key represention of the board.
    :rtype: str
    """
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

    """
    Reset the game to its initial state.
    
    Clears the board, resets turn, history, reinitializes pieces.
    """
    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.selected = None
        self.turn = "white"
        self.history = []
        self.setup_pieces()

        self.history.append(copy.deepcopy(self.board))


    """
    Get the piece at a specific position.
    
    :param row - Row index.
    :type row: int      
    
    :param col - Column index.
    :type col: int    
    
    :returns - Piece dictionary or None.
    :rtype: dict | None 
    """
    def get_piece(self, row, col):
        return self.board[row][col]

    """
    Move a piece on the board.
    Handles:
    - Movment
    - Captures
    - King promotion
    - Turn switching
    
    :param old_row - Starting row.
    :type old_row: int

    :param old_col - Starting column.
    :type old_col: int

    :param new_row - Destination row.
    :type new_row: int

    :param new_col - Destination column.
    :type new_col: int
    
    :return - True is a piece became a king.
    :rtype: bool
    """
    def move_piece(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]
        if not piece:
            return False

        self.board[old_row][old_col] = None
        self.board[new_row][new_col] = piece

        if abs(old_row - new_row) == 2:
            self.remove_captured_piece(old_row, old_col, new_row, new_col)

        became_king = self.check_make_king(new_row, new_col)

        self.turn = "black" if self.turn == "white" else "white"
        self.history.append(copy.deepcopy(self.board))

        return became_king

    """
    Remove a captured piece after a jump.

    :param old_row - Starting row.
    :type old_row: int

    :param old_col - Starting column.
    :type old_col: int

    :param new_row - Destination row.
    :type new_row: int

    :param new_col - Destination column.
    :type new_col: int
    """
    def remove_captured_piece(self, old_row, old_col, new_row, new_col):
        mid_row = (old_row + new_row) // 2
        mid_col = (old_col + new_col) // 2
        self.board[mid_row][mid_col] = None

    """
    Check if a board position is within bounds.
    
    :param r - Row index.
    :type r: int      

    :param c - Column index.
    :type c: int    
    
    :return - True if position is valid.
    :rtype: bool
    """
    def check_valid_move(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    """
    Get all legal moves for a piece with capture priorities.
        
    :param row - Piece row index.
    :type row: int      

    :param col - Piece column index.
    :type col: int
    
    :param board - Optional board state.
    :type board: list
    
    :param color - Optional override color.
    :type color: str
        
    :return - List of (row, col) moves.
    :rtype: list
    """
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

    """
    Select best move using hardcoded heuristic scoring.
    
    :param color - Piece color.
    :type color: str
    
    :return - Move tuple or None.
    :rtype: tuple | None
    """
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


    """
    Select a random valid move.
    
    :param color - Piece color.
    :type color: str
    
    :return - Move tuple or None.
    :rtype: tuple | None
    """
    def get_random_move(self, color):
        all_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col):
                        all_moves.append((row, col, new_row, new_col))

        return rnd.choice(all_moves) if all_moves else None

    """
    Epsilon-Greedy move selection using stored board values.
    
    :param color - Piece color.
    :type color: str
    
    :return - Move tuple or None.
    :rtype: tuple | None
    """
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

    """
    Select best move using neural network evaluation.
    
    :param color - Piece color.
    :type color: str
    
    :return - Move tuple or None.
    :rtype: tuple | None
    """
    def get_greedy_nn_move(self, color):
        best_score = -9999
        best_moves = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    for new_row, new_col in self.get_moves(row, col):
                        simulated = self.simulate_move(row, col, new_row, new_col)

                        score = self.nn_evaluate(simulated)

                        if score > best_score:
                            best_score = score
                            best_moves = [(row, col, new_row, new_col)]
                        elif score == best_score:
                            best_moves.append((row, col, new_row, new_col))

        return rnd.choice(best_moves) if best_moves else None

    """
    Evaluate a move using heuristic rules.
    
    :return - Score value.
    :rtype: float
    """
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

    """
    Get stored value of a board from memory.
    
    :param board - Board state.
    :type board: list
    
    :return - Evaluation score.
    :rtype: float
    """
    def evaluate_board(self, board):
        key = self.board_to_key(board)
        if key in self.values:
            return self.values[key][0]
        self.count += 1
        return 0.0

    """
    Evaluate a board using the neural network.

    :param board - Board state.
    :type board: list

    :return - Predicted score.
    :rtype: float
    """
    def nn_evaluate(self, board):
        encoded_board = []
        for row in board:
            for piece in row:
                if piece is None:
                    encoded_board.extend([1, 0, 0, 0, 0])
                elif piece["color"] == "white":
                    encoded_board.extend([0, 1, 0, 0, 0] if not piece["king"] else [0, 0, 0, 1, 0])
                else:
                    encoded_board.extend([0, 0, 1, 0, 0] if not piece["king"] else [0, 0, 0, 0, 1])

        x = torch.tensor(encoded_board, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            return float(self.nn(x))

    """
    Promote a piece to king if it reaches the last row.
    
    :return - True if promotion occurred.
    :rtype: bool
    """
    def check_make_king(self, row, col):
        became_king = False
        piece = self.board[row][col]
        if not piece:
            return None

        if piece["king"]:
            return became_king

        if piece["color"] == "black" and row == BOARD_SIZE - 1:
            piece["king"] = True
            became_king = True

        if piece["color"] == "white" and row == 0:
            piece["king"] = True
            became_king = True

        return became_king

    """
    Simulate a move without modifying the real board.
    
    :return - new board state.
    :rtype: list
    """
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

    """
    Check if a move exposes the piece to capture.
    
    :return - True if risky.
    :rtype: bool
    """
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

    """
    Check if a player has any legal moves.
    
    :param color - Piece color.
    :type color: str
    
    :return - True if move exist.
    :rtype: bool
    """
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

    """
    Check if the game has a winner.
    
    :return - "white" or "black" or "lock" or None.
    :rtype: str | None
    """
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

    """
    Update memory values based on game result using discounting.
    
    :param winner - Game winner.
    :type winner: str
    """
    def score_game(self, winner):
        if winner == "white":
            reward = 1.0
        elif winner == "black":
            reward = -1.0
        else:
            reward = 0.5

        n = len(self.history)

        for i, board in enumerate(self.history):
            discounted = reward * (self.gamma ** (n - i - 1))
            key = self.board_to_key(board)

            if key not in self.values:
                self.values[key] = [discounted, 1]
            else:
                old, count = self.values[key]
                new = (old * count + discounted) / (count + 1)
                self.values[key] = [new, count + 1]

    """
    Load stored board evaluations from file.
    
    :return - Dictionary of board values.
    :rtype: dict
    """
    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)

        return {}

    """
    Save board evaluations to file.
    """
    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.values, f, indent=2)

    """
    Simulate a game between two players.
    
    :param white_play - Strategy for white.
    :type white_play: str
    
    :param black_play - Strategy for black.
    :type black_play: str
    
    :param max_moves: Maximum moves before draw.
    :type max_moves: int
    
    :return - Game result.
    :rtype: str
    """
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

    """
    Run multile games and collect statistics.
    
    :param rounds - number of games.
    :type rounds: int
    
    :param white_play - Strategy for white.
    :type white_play: str
    
    :param black_play - Strategy for black.
    :type black_play: str
    
    :return - Results dictionary.
    :rtype: dict
    """
    def run_tournament(self, rounds=100, white_play="AGENT", black_play="AGENT"):

        results = {"white": 0, "black": 0, "lock": 0, "lock (more moves)": 0}
        mean_score_list = []

        for i in range(1, rounds + 1):
            winner = self.play_agent_vs_agent(white_play, black_play)
            results[winner] += 1
            if i % 100 == 0:
                print(f"Game {i}")
            mean_score_list.append(self.count/len(self.history))

        print("\nTOURNAMENT RESULTS")
        print("------------------")
        for k, v in results.items():
            print(f"{k.upper()}: {v}")

        print(f"unknown board count {self.count}")

        print(f"Mean new boards: {statistics.mean(mean_score_list)}")
        print(f"STD new boards: {stdev(mean_score_list)}")
        return results

if __name__ == "__main__":
    model = CheckersModel()
    model.run_tournament(1000, white_play="GREEDY_NN", black_play="GREEDY")