import sys
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
from CheckersGame import GameWindow

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 464
WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/menu-background.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"

class MenuWindow(QMainWindow):
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

        self.start_button = QPushButton("Start Game", self.label)
        self.start_button.setGeometry(100, 200, 200, 50)
        self.start_button.clicked.connect(self.start_game)

    def start_game(self):
        self.game_window = GameWindow()
        self.game_window.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = MenuWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()