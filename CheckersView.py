import os
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464
BOARD_SIZE = 8
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

WINDOW_TITLE = "Checkers Game"

CHECKERS_LOGO_IMAGE = "Game-Design/checkers-black2.png"
CHECKERS_MOVE = "Game-Design/checkers-shadow.png"
SETTINGS_ICON = "Game-Design/settings-icon.png"
BACK_ICON = "Game-Design/back-icon.png"
SOUNDON_ICON = "Game-Design/soundon-icon.png"
SOUNDOFF_ICON = "Game-Design/soundoff-icon.png"

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
    def __init__(self, bg_image, sound_state):
        super().__init__()
        self.setFixedSize(600, 600)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(CHECKERS_LOGO_IMAGE))

        self.on_piece_click = None
        self.on_move_click = None

        self.piece_buttons = []
        self.move_buttons = []
        self.shadow_buttons = []

        self.end_screen = None

        self.skin = SKIN_SETS.get(bg_image, SKIN_SETS["Game-Design/checkers-BG1.png"])

        self.label = QLabel(self)
        bg = QPixmap(os.path.abspath(bg_image))
        self.label.setPixmap(bg)
        self.label.setGeometry(68, 68, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

        self.setup_layout(sound_state)

    def setup_layout(self, sound_state):
        self.top_bar = QWidget(self)
        self.top_bar.setGeometry(0, 0, 600, 50)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(542, 50, 150, 100)
        self.settings_panel.hide()

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(20)

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)

        self.turn_text = QLabel("Turn: WHITE")
        self.timer_text = QLabel("Time: 00:00")

        for lb in (self.turn_text, self.timer_text):
            lb.setAlignment(Qt.AlignCenter)
            lb.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: white;"
                "background-color: rgba(0,0,0,160);"
                "padding: 6px 14px; border-radius: 8px;"
            )

        self.settings_btn = QPushButton()
        self.menu_btn = QPushButton()
        self.sound_btn = QPushButton()
        for btn in (self.settings_btn, self.menu_btn, self.sound_btn):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")
            btn.setFixedSize(36, 36)
            btn.setIconSize(QSize(36, 36))

        self.settings_btn.setIcon(QIcon(SETTINGS_ICON))
        self.menu_btn.setIcon(QIcon(BACK_ICON))
        self.sound_enabled = sound_state
        self.update_sound_icon()

        self.settings_btn.clicked.connect(self.toggle_settings_panel)
        self.menu_btn.clicked.connect(self.back_to_menu)
        self.sound_btn.clicked.connect(self.toggle_sound)

        top_layout.addWidget(self.turn_text)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.timer_text)
        top_layout.addStretch()
        top_layout.addWidget(self.settings_btn)

        panel_layout.addWidget(self.menu_btn)
        panel_layout.addWidget(self.sound_btn)

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

    def update_sound_icon(self):
        icon = SOUNDON_ICON if self.sound_enabled else SOUNDOFF_ICON
        self.sound_btn.setIcon(QIcon(icon))

    def toggle_settings_panel(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.update_sound_icon()

    def back_to_menu(self):
        self.close()

        from CheckersMenu import CheckersMenu
        self.menu = CheckersMenu()
        self.menu.show()

    def show_end_screen(self, winner, timer, on_restart, on_menu):
        self.turn_text.setText("Turn: Game Over")

        self.end_screen = QWidget(self)
        self.end_screen.setGeometry(0, 0, 464, 464)
        self.end_screen.setStyleSheet( "background-color: rgba(0, 0, 0, 160);" )
        self.end_screen.move(68, 68)

        layout = QVBoxLayout(self.end_screen)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel(f"{winner.upper()} WINS!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet( "font-size: 36px; font-weight: bold; color: white;" )

        time_played = QLabel(f"Time Played: {timer}")
        time_played.setAlignment(Qt.AlignCenter)
        time_played.setStyleSheet( "font-size: 20px; font-weight: bold; color: white;" )

        restart_btn = QPushButton("Play Again")
        menu_btn = QPushButton("Main Menu")

        restart_btn.clicked.connect(on_restart)
        menu_btn.clicked.connect(on_menu)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(time_played)
        layout.addSpacing(40)

        layout.addWidget(restart_btn)
        layout.addWidget(menu_btn)

        self.end_screen.show()