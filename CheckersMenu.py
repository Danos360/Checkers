import sys
import os

from PySide6.QtCore import Qt, QSize, QUrl, QTimer
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PySide6.QtMultimedia import QSoundEffect
from CheckersModel import CheckersModel
from CheckersView import CheckersView
from CheckersController import CheckersController

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 464
WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/menu-background.png"
CHECKERS_ICON_LOGO_IMAGE = "Game-Design/checkers-black2.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"

START_BUTTON_IMAGE = "Game-Design/start_button.png"
GAMEMODE_BUTTON_IMAGE = "Game-Design/gamemode_button.png"
CHANGEBG_BUTTON_IMAGE = "Game-Design/changebg_button.png"
SETTINGS_ICON = "Game-Design/settings-icon.png"
SOUNDON_ICON = "Game-Design/soundon-icon.png"
SOUNDOFF_ICON = "Game-Design/soundoff-icon.png"
SOUND_MENU_FILE = "Game-Sounds/Menu-Sound.wav"
SOUND_CLICK_FILE = "Game-Sounds/Click_Sound.wav"
INTRO_SOUND_FILE = "Game-Sounds/game-intro.wav"

class CheckersMenu(QMainWindow):
    def __init__(self, sound_enabled = True):
        super().__init__()

        self.backgrounds = [
            "Game-Design/checkers-BG1-mini.png",
            "Game-Design/checkers-BG2-mini.png",
            "Game-Design/checkers-BG3-mini.png"
        ]

        self.bg_num = 1
        self.game_mode = "1v1"
        self.game_starting = True
        self.sound_enabled = sound_enabled

        self.setWindowTitle(WINDOW_TITLE)
        self.setFixedSize(QSize(WINDOW_WIDTH,WINDOW_HEIGHT))
        self.setWindowIcon(QIcon(CHECKERS_ICON_LOGO_IMAGE))

        img_path = os.path.abspath(BACKGROUND_IMAGE)
        pixmap = QPixmap(img_path)

        logo_path = os.path.abspath(CHECKERS_LOGO_IMAGE)
        logo_pixmap = QPixmap(logo_path)

        self.menu_sound = QSoundEffect()
        self.menu_sound.setSource(QUrl.fromLocalFile(SOUND_MENU_FILE))
        self.menu_sound.setLoopCount(-2)

        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile(SOUND_CLICK_FILE))

        self.intro_sound = QSoundEffect()
        self.intro_sound.setSource(QUrl.fromLocalFile(INTRO_SOUND_FILE))

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

        self.setup_layout(self.sound_enabled)

        self.update_bg_preview()
        self.update_gm_preview()

        if self.sound_enabled:
            self.menu_sound.play()

    def setup_layout(self, sound_state):
        self.start_button = QPushButton(self.label)
        self.start_button.setIcon(QIcon(START_BUTTON_IMAGE))
        self.start_button.move(100, 100)
        self.start_button.clicked.connect(self.start_game)

        self.bg_button = QPushButton(self.label)
        self.bg_button.setIcon(QIcon(CHANGEBG_BUTTON_IMAGE))
        self.bg_button.move(25, 235)
        self.bg_button.clicked.connect(self.next_background)

        self.bg_preview = QLabel(self.label)
        self.bg_preview.setGeometry(50, 335, 100, 100)
        self.bg_preview.setScaledContents(True)

        self.gm_button = QPushButton(self.label)
        self.gm_button.setIcon(QIcon(GAMEMODE_BUTTON_IMAGE))
        self.gm_button.move(225, 235)
        self.gm_button.clicked.connect(self.next_gamemode)

        self.gm_preview = QLabel(self.label)
        self.gm_preview.setGeometry(250, 335, 100, 100)
        self.gm_preview.setScaledContents(True)

        for btn in (self.start_button, self.bg_button, self.gm_button):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")
            btn.setIconSize(QSize(150, 150))
        self.start_button.setIconSize(QSize(200, 200))

        self.settings_btn = QPushButton(self)
        self.settings_btn.setIcon(QIcon(SETTINGS_ICON))
        self.settings_btn.move(WINDOW_WIDTH - 50, 10)
        self.settings_btn.clicked.connect(self.toggle_settings_panel)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(WINDOW_WIDTH - 60, 40, 150, 60)
        self.settings_panel.hide()

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)

        self.sound_btn = QPushButton()
        self.update_sound_icon()
        self.sound_btn.clicked.connect(self.toggle_sound)

        for btn in (self.settings_btn, self.sound_btn):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")
            btn.setFixedSize(36, 36)
            btn.setIconSize(QSize(36, 36))

        panel_layout.addWidget(self.sound_btn)

    def next_background(self):
        self.bg_num = (self.bg_num+1) % len(self.backgrounds)
        self.update_bg_preview()
        self.click_sound.play()

    def update_bg_preview(self):
        size = self.bg_preview.size()

        pix = QPixmap(self.backgrounds[self.bg_num - 1]).scaled(size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        out = QPixmap(size)
        out.fill(Qt.transparent)

        pr = QPainter(out)
        path = QPainterPath()
        path.addRoundedRect(out.rect(), 20, 20)
        pr.setClipPath(path)
        pr.drawPixmap(0, 0, pix)
        pr.end()

        self.bg_preview.setPixmap(out)

    def next_gamemode(self):
        self.game_mode = "agent" if self.game_mode == "1v1" else "1v1"
        self.update_gm_preview()
        self.click_sound.play()

    def update_gm_preview(self):
        self.gm_preview.setText(self.game_mode.upper())
        self.gm_preview.setAlignment(Qt.AlignCenter)
        self.gm_preview.setStyleSheet("""QLabel{font-size: 20px; font-weight: bold; color: white; background-color: rgba(0,0,0,70); border-radius: 10px;}""")

    def toggle_settings_panel(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())
        self.click_sound.play()

    def update_sound_icon(self):
        icon = SOUNDON_ICON if self.sound_enabled else SOUNDOFF_ICON
        self.sound_btn.setIcon(QIcon(icon))

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

        if self.sound_enabled and self.intro_sound.isPlaying() == False:
            self.menu_sound.play()
        else:
            self.menu_sound.stop()

        self.update_sound_icon()

    def start_game(self):
        self.start_button.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        if self.sound_enabled:
            self.menu_sound.stop()
            self.intro_sound.play()

            QTimer.singleShot(3500, self.launch_game)
        else:
            self.launch_game()

    def launch_game(self):
        selected_bg = self.backgrounds[self.bg_num - 1]

        model = CheckersModel()
        view = CheckersView(selected_bg, self.sound_enabled)
        controller = CheckersController(model, view, self.game_mode)

        view.show()
        view.play_start_sound()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = CheckersMenu()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()