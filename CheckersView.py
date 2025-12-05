import os
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464
BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/checkers-BGtest.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"
CHECKERS_BLACK = "Game-Design/checkers-black.png"
CHECKERS_WHITE = "Game-Design/checkers-white.png"
CHECKERS_MOVE = "Game-Design/checkers-shadow.png"
CHECKERS_BLACK_KING = "Game-Design/checkers-blackKing.png"
CHECKERS_WHITE_KING = "Game-Design/checkers-whiteKing.png"

class CheckersView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(CHECKERS_LOGO_IMAGE))

        self.on_piece_click = None
        self.on_move_click = None

        self.piece_buttons = []
        self.move_buttons = []

        bg = QPixmap(os.path.abspath(BACKGROUND_IMAGE))
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
            icon = CHECKERS_BLACK_KING
        elif piece["king"] and piece["color"] == "white":
            icon = CHECKERS_WHITE_KING
        elif piece["color"] == "black":
            icon = CHECKERS_BLACK
        else:
            icon = CHECKERS_WHITE

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

    def show_winner(self, color):
        msg = QMessageBox(self)
        msg.setWindowTitle("Game Over")
        msg.setText(f"{color.upper()} wins!")
        msg.exec()