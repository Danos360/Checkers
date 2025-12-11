import sys
import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton
from CheckersModel import CheckersModel
from CheckersView import CheckersView
from CheckersController import CheckersController

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 464
WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/menu-background.png"
CHECKERS_ICON_LOGO_IMAGE = "Game-Design/checkers-icon-logo.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"

START_BUTTON_IMAGE = "Game-Design/start_button.png"


class CheckersMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.backgrounds = [
            "Game-Design/checkers-BG1.png",
            "Game-Design/checkers-BG2.png",
            "Game-Design/checkers-BG3.png"

        ]

        self.bg_num = 1
        self.game_mode = "1v1"

        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(WINDOW_WIDTH,WINDOW_HEIGHT))
        self.setWindowIcon(QIcon(CHECKERS_ICON_LOGO_IMAGE))

        img_path = os.path.abspath(BACKGROUND_IMAGE)
        pixmap = QPixmap(img_path)

        logo_path = os.path.abspath(CHECKERS_LOGO_IMAGE)
        logo_pixmap = QPixmap(logo_path)

        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

        self.logo = QLabel(self)
        self.logo.setPixmap(logo_pixmap)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFixedSize(QSize(400, 100))
        self.logo.move(0, 50)
        self.logo.setScaledContents(True)

        self.start_button = QPushButton(self.label)
        self.start_button.setIcon(QIcon(START_BUTTON_IMAGE))
        self.start_button.setIconSize(QSize(200, 200))
        self.start_button.move(100, 100)
        self.start_button.setFlat(True)
        self.start_button.setStyleSheet("QPushButton { padding: 0px; border: none; }")
        self.start_button.clicked.connect(self.start_game)

        self.bg_button = QPushButton("Change BG", self.label)
        self.bg_button.setGeometry(50, 280, 100, 50)
        self.bg_button.clicked.connect(self.next_background)

        self.bg_preview = QLabel(self.label)
        self.bg_preview.setGeometry(50, 335, 100, 100)
        self.bg_preview.setScaledContents(True)

        self.gm_button = QPushButton("Game Mode", self.label)
        self.gm_button.setGeometry(250, 280, 100, 50)
        self.gm_button.clicked.connect(self.next_gamemode)

        self.gm_preview = QLabel(self.label)
        self.gm_preview.setGeometry(250, 335, 100, 100)
        self.gm_preview.setScaledContents(True)

        self.update_bg_preview()
        self.update_gm_preview()


    def next_background(self):
        self.bg_num = (self.bg_num+1) % len(self.backgrounds)
        self.update_bg_preview()

    def update_bg_preview(self):
        pix = QPixmap(self.backgrounds[self.bg_num - 1])
        self.bg_preview.setPixmap(pix)

    def next_gamemode(self):
        self.game_mode = "agent" if self.game_mode == "1v1" else "1v1"
        self.update_gm_preview()

    def update_gm_preview(self):
        self.gm_preview.setText(self.game_mode.upper())
        self.gm_preview.setAlignment(Qt.AlignCenter)
        self.gm_preview.setStyleSheet("""QLabel{font-size: 20px; font-weight: bold; color: white; background-color: rgba(0,0,0,70); border-radius: 10px;}""")

    def start_game(self):
        selected_bg = self.backgrounds[self.bg_num-1]

        model = CheckersModel()
        view = CheckersView(selected_bg)
        controller = CheckersController(model, view, self.game_mode)

        view.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    window = CheckersMenu()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()