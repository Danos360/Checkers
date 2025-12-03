import sys
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464

WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/checkers-test.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"
BLACK_CHECKERS_IMAGE = "Game-Design/checkers-black.png"
WHITE_CHECKERS_IMAGE = "Game-Design/checkers-white.png"
CHECKERS_MOVE_IMAGE = "Game-Design/checkers-shadow.png"

BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(WINDOW_WIDTH,WINDOW_HEIGHT))
        self.setWindowIcon(QIcon(CHECKERS_LOGO_IMAGE))

        img_path = os.path.abspath(BACKGROUND_IMAGE)
        pixmap = QPixmap(img_path)

        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

        self.pieces = []
        self.selected_piece = None
        self.highlight_buttons = []

        self.place_board_pieces()

    def place_board_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.create_piece(row, col, BLACK_CHECKERS_IMAGE)
                    elif row > 4:
                        self.create_piece(row, col, WHITE_CHECKERS_IMAGE)

    def create_piece(self, row, col, image_path):
        piece = QPushButton(self.label)
        piece.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        icon = QIcon(os.path.abspath(image_path))
        piece.setIcon(icon)
        piece.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        piece.setFlat(True)
        piece.setStyleSheet("QPushButton { padding: 0px; border: none; }")

        piece.clicked.connect(lambda _, p=piece: self.select_piece_dynamic(p))

        self.pieces.append({ "button": piece, "row": row, "col": col, "color": image_path })

    def select_piece(self, row, col, piece_button):
        self.clear_highlights()

        self.selected_piece = (row, col, piece_button)

        piece_data = next(p for p in self.pieces if p["button"] == piece_button)
        color = piece_data["color"]

        direction = -1 if "white" in color else 1

        possible_moves = [
            (row + direction, col - 1),
            (row + direction, col + 1)
        ]

        for r, c in possible_moves:
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                self.create_highlight(r, c)

    def create_highlight(self, row, col):
        highlight = QPushButton(self.label)
        highlight.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        icon = QIcon(os.path.abspath(CHECKERS_MOVE_IMAGE))
        highlight.setIcon(icon)
        highlight.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        highlight.setStyleSheet("QPushButton { padding: 0px; border: none; }")

        highlight.clicked.connect(lambda _, r=row, c=col: self.move_piece(r, c))
        highlight.show()

        self.highlight_buttons.append(highlight)

    def clear_highlights(self):
        for btn in self.highlight_buttons:
            btn.deleteLater()
        self.highlight_buttons.clear()

    def move_piece(self, new_row, new_col):
        if not self.selected_piece:
            return

        old_row, old_col, piece_button = self.selected_piece

        piece_button.setGeometry(
            new_col * CELL_SIZE,
            new_row * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        for p in self.pieces:
            if p["button"] == piece_button:
                p["row"] = new_row
                p["col"] = new_col
                break

        self.selected_piece = None
        self.clear_highlights()

    def select_piece_dynamic(self, piece_button):
        piece_data = next(p for p in self.pieces if p["button"] == piece_button)
        row = piece_data["row"]
        col = piece_data["col"]

        self.select_piece(row, col, piece_button)

def main():
    app = QApplication(sys.argv)
    window = GameWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()