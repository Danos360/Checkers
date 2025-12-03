import sys
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464
WINDOW_TITLE = "Checkers"
BACKGROUND_IMAGE = "Game-Design/checkers.png"
BLACK_CHECKERS_IMAGE = "Game-Design/checkers-black.png"
WHITE_CHECKERS_IMAGE = "Game-Design/checkers-black.png"
BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(WINDOW_WIDTH,WINDOW_HEIGHT))
        self.setWindowIcon(QIcon(BLACK_CHECKERS_IMAGE))

        img_path = os.path.abspath(BACKGROUND_IMAGE)
        pixmap = QPixmap(img_path)

        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

        self.pieces = []
        self.place_board_pieces()

    def place_board_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.create_piece(row, col, "Game-Design/checkers-black.png")
                    elif row > 4:
                        self.create_piece(row, col, "Game-Design/checkers-white.png")

    def create_piece(self, row, col, image_path):
        piece = QPushButton(self.label)
        piece.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        icon = QIcon(os.path.abspath(image_path))
        piece.setIcon(icon)
        piece.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        piece.setFlat(True)

        self.pieces.append(piece)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()