import os
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464
BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

WINDOW_TITLE = "Checkers Game"

CHECKERS_LOGO_IMAGE = "Game-Design/checkers-black2.png"
CHECKERS_MOVE = "Game-Design/checkers-shadow.png"
SKIN_SETS = {
    "Game-Design/checkers-BG1.png": {
        "black": "Game-Design/checkers-black.png",
        "white": "Game-Design/checkers-white.png",
        "black_king": "Game-Design/checkers-blackKing.png",
        "white_king": "Game-Design/checkers-whiteKing.png",
    },

    "Game-Design/checkers-BG2.png": {
        "black": "Game-Design/checkers-black2.png",
        "white": "Game-Design/checkers-white2.png",
        "black_king": "Game-Design/checkers-blackKing2.png",
        "white_king": "Game-Design/checkers-whiteKing2.png",
    },

    "Game-Design/checkers-BG3.png": {
        "black": "Game-Design/checkers-black2.png",
        "white": "Game-Design/checkers-white2.png",
        "black_king": "Game-Design/checkers-blackKing2.png",
        "white_king": "Game-Design/checkers-whiteKing2.png",
    }
}

class CheckersView(QMainWindow):
    def __init__(self, bg_image):
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(CHECKERS_LOGO_IMAGE))

        self.on_piece_click = None
        self.on_move_click = None

        self.piece_buttons = []
        self.move_buttons = []
        self.shadow_buttons = []

        self.skin = SKIN_SETS.get(bg_image, SKIN_SETS["Game-Design/checkers-BG1.png"])

        bg = QPixmap(os.path.abspath(bg_image))
        self.label = QLabel(self)
        self.label.setPixmap(bg)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

    def draw_board(self, board):
        for btn in self.piece_buttons:
            btn.deleteLater()
        for btn in self.move_buttons:
            btn.deleteLater()
        self.piece_buttons = []
        self.move_buttons = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = board[row][col]
                if piece:
                    self.draw_piece(row, col, piece)

    def draw_piece(self, row, col, piece):

        btn = QPushButton(self.label)

        if piece["king"] and piece["color"] == "black":
            icon = self.skin["black_king"]
        elif piece["king"] and piece["color"] == "white":
            icon = self.skin["white_king"]
        elif piece["color"] == "black":
            icon = self.skin["black"]
        else:
            icon = self.skin["white"]

        btn.setIcon(QIcon(icon))
        btn.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        btn.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        btn.setFlat(True)
        btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")

        btn.clicked.connect(lambda _, brow=row, bcol=col: self.on_piece_click(brow, bcol))
        btn.show()
        self.piece_buttons.append(btn)

    def show_moves(self, moves):
        for btn in self.move_buttons:
            btn.deleteLater()
        self.move_buttons = []

        for row, col in moves:
            btn = QPushButton(self.label)
            btn.setIcon(QIcon(CHECKERS_MOVE))
            btn.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            btn.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")

            btn.clicked.connect(lambda _, brow=row, bcol=col: self.on_move_click(brow, bcol))
            btn.show()
            self.move_buttons.append(btn)

    def draw_shadow(self, row, col):
        btn = QPushButton(self.label)
        btn.setIcon(QIcon(CHECKERS_MOVE))  # shadow image
        btn.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        btn.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        btn.setFlat(True)
        btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")

        btn.lower()
        btn.show()

        self.shadow_buttons.append(btn)

    def clear_shadows(self):
        for btn in self.shadow_buttons:
            btn.deleteLater()
        self.shadow_buttons = []

    def show_winner(self, color):
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"{color.upper()} wins!")
        msg.exec()