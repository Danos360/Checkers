import os
import random
from PySide6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QSize, QUrl, Qt, Signal
from PySide6.QtMultimedia import QSoundEffect

WINDOW_WIDTH = 464
WINDOW_HEIGHT = 464

BOARD_SIZE = 6
CELL_SIZE = WINDOW_WIDTH // BOARD_SIZE

WINDOW_TITLE = "Checkers Game"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-black2.png"
CHECKERS_MOVE = "Game-Design/checkers-shadow.png"
SETTINGS_ICON = "Game-Design/settings-icon.png"
BACK_ICON = "Game-Design/back-icon.png"
SOUNDON_ICON = "Game-Design/soundon-icon.png"
SOUNDOFF_ICON = "Game-Design/soundoff-icon.png"
DARKMODE_ICON = "Game-Design/darkmode-icon.png"
LIGHTMODE_ICON = "Game-Design/lightmode-icon.png"

SOUND_CLICK_FILE = "Game-Sounds/Click_Sound.wav"
SOUND_MOVE = "Game-Sounds/make-move.wav"
SOUND_KING = "Game-Sounds/make-king.wav"
SOUND_GAME_START = "Game-Sounds/game-start1.wav"
SOUND_GAME_WIN = [
    "Game-Sounds/game-win1.wav",
    "Game-Sounds/game-win2.wav"
]
SOUND_GAME_LOSE = [
    "Game-Sounds/game-over1.wav",
    "Game-Sounds/game-over2.wav",
    "Game-Sounds/game-over3.wav"
]

SKIN_SETS = {
    "Game-Design/checkers-BG1-mini.png": {
        "black": "Game-Design/checkers-black.png",
        "white": "Game-Design/checkers-white.png",
        "black_king": "Game-Design/checkers-blackKing.png",
        "white_king": "Game-Design/checkers-whiteKing.png",
    },

    "Game-Design/checkers-BG2-mini.png": {
        "black": "Game-Design/checkers-black2.png",
        "white": "Game-Design/checkers-white2.png",
        "black_king": "Game-Design/checkers-blackKing2.png",
        "white_king": "Game-Design/checkers-whiteKing2.png",
    },

    "Game-Design/checkers-BG3-mini.png": {
        "black": "Game-Design/checkers-black2.png",
        "white": "Game-Design/checkers-white2.png",
        "black_king": "Game-Design/checkers-blackKing2.png",
        "white_king": "Game-Design/checkers-whiteKing2.png",
    }
}

class CheckersView(QMainWindow):

    # Signal that calls the main manager to return to the menu with the current sound mode.
    back_to_menu_signal = Signal(bool)

    """
    Initialize the game view.

    Setups:
    - Window properties.
    - Background and board display.
    - UI elements and layout.
    - Sound effects.
    - Skin set based on selected background.

    :param bg_image - Selected background image path.
    :type bg_image: str

    :param sound_enabled - Initial sound state.
    :type sound_enabled: bool
    """
    def __init__(self, bg_image, sound_enabled=True):
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
        self.sound_enabled = sound_enabled
        self.dark_mode = False

        self.skin = SKIN_SETS.get(bg_image)

        self.label = QLabel(self)
        bg = QPixmap(os.path.abspath(bg_image))
        self.label.setPixmap(bg)
        self.label.setGeometry(68, 68, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setScaledContents(True)

        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile(SOUND_CLICK_FILE))

        self.move_sound = QSoundEffect()
        self.move_sound.setSource(QUrl.fromLocalFile(SOUND_MOVE))

        self.king_sound = QSoundEffect()
        self.king_sound.setSource(QUrl.fromLocalFile(SOUND_KING))

        self.game_start_sound = QSoundEffect()
        self.game_start_sound.setSource(QUrl.fromLocalFile(SOUND_GAME_START))

        self.win_sound = QSoundEffect()
        self.lose_sound = QSoundEffect()

        self.play_start_sound()
        self.setup_layout()

    """
    Create and configure UI layout.
    
    Includes:
    - Settings panel. (menu, sound toggle, theme toggle).
    - Top bar. (turn indication, timer).
    
    Also connects button signal to their handlers.
    """
    def setup_layout(self):
        self.top_bar = QWidget(self)
        self.top_bar.setGeometry(0, 0, 600, 50)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(542, 50, 150, 160)
        self.settings_panel.hide()

        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(20)

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(10, 0, 10, 10)
        panel_layout.setSpacing(5)

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
        self.theme_btn = QPushButton()

        for btn in (self.settings_btn, self.menu_btn, self.sound_btn, self.theme_btn):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")
            btn.setFixedSize(36, 36)
            btn.setIconSize(QSize(36, 36))

        self.settings_btn.setIcon(QIcon(SETTINGS_ICON))
        self.menu_btn.setIcon(QIcon(BACK_ICON))
        self.sound_btn.setIcon(QIcon(SOUNDON_ICON))
        self.theme_btn.setIcon(QIcon(LIGHTMODE_ICON))

        self.settings_btn.clicked.connect(self.toggle_settings_panel)
        self.menu_btn.clicked.connect(self.back_to_menu)
        self.sound_btn.clicked.connect(self.toggle_sound)
        self.theme_btn.clicked.connect(self.toggle_theme)

        top_layout.addWidget(self.turn_text)
        top_layout.addSpacing(60)
        top_layout.addWidget(self.timer_text)
        top_layout.addStretch()
        top_layout.addWidget(self.settings_btn)

        panel_layout.addWidget(self.menu_btn)
        panel_layout.addWidget(self.sound_btn)
        panel_layout.addWidget(self.theme_btn)

        self.update_sound_icon()
        self.toggle_theme()

    """
    Render the entire board.
    
    Clears existing pieces and redraw them based on current state.
    
    :param board - Matrix 2D list representing the board state.
    :type board: list 
    """
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

    """
    Draw a piece on the board.
    
    Selects the current image based on the color and King flag.
    
    :param row - Row index.
    :type row: int
    
    :param col - Column index.
    :type col: int
    
    :param piece - Piece data (color + king flag).
    :type piece: dict
    """
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

    """
    Display available moves as clicked overlays.
    
    :param moves - List of (row, col) position.
    :type moves: list[tuple[int, int]]
    """
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

    """
    Draw a background shadow under a square. Used for visualization.
    
    :param row - Row index.
    :type row: int
    
    :param col - Column index.
    :type col: int
    """
    def draw_shadow(self, row, col):
        btn = QPushButton(self.label)
        btn.setIcon(QIcon(CHECKERS_MOVE))
        btn.setGeometry(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        btn.setIconSize(QSize(CELL_SIZE, CELL_SIZE))
        btn.setFlat(True)
        btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")

        btn.lower()
        btn.show()

        self.shadow_buttons.append(btn)

    """
    Remove all shadow highlights from the board.
    """
    def clear_shadows(self):
        for btn in self.shadow_buttons:
            btn.deleteLater()
        self.shadow_buttons = []

    """
    Show or hide the settings panel.
    """
    def toggle_settings_panel(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())
        self.play_click_sound()

    """
    Update sound button icon based on current state.
    """
    def update_sound_icon(self):
        icon = SOUNDON_ICON if self.sound_enabled else SOUNDOFF_ICON
        self.sound_btn.setIcon(QIcon(icon))

    """
    Toggle between dark mode and light mode.
    
    Updates UI styling and button icon.
    """
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.apply_theme(True)
            self.theme_btn.setIcon(QIcon(DARKMODE_ICON))
        else:
            self.apply_theme(False)
            self.theme_btn.setIcon(QIcon(LIGHTMODE_ICON))

        self.play_click_sound()

    """
    Enable or disable sound.
    """
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.update_sound_icon()

    """
    Close current game view and calls a signal the opens the main menu.
    """
    def back_to_menu(self):
        self.back_to_menu_signal.emit(self.sound_enabled)

        self.close()

    """
    Display end of game overlay.
    
    Shows:
    - Winner.
    - Time player.
    - Restart and menu buttons.
    
    :param winner - Winning player.
    :type winner: str
    
    :param timer - Game duration.
    :type timer: str
    
    :param on_restart - Callback for restarting the game.
    :type on_restart: Callable
    
    :param on_menu - Callback for returning to menu.
    :type on_menu: Callable
    """
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
        restart_btn.setStyleSheet( "color: white;" )
        menu_btn.setStyleSheet( "color: white;" )

        restart_btn.clicked.connect(on_restart)
        menu_btn.clicked.connect(on_menu)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(time_played)
        layout.addSpacing(40)

        layout.addWidget(restart_btn)
        layout.addWidget(menu_btn)

        self.end_screen.show()

    """
    Apply visual theme to the UI.
    
    :param dark_mode - True for dark mode, False for light mode.
    :type dark_mode: bool
    """
    def apply_theme(self, dark_mode: bool):
        window_bg = "#1e1e1e" if dark_mode else "#f0f0f0"
        text_color = "white" if dark_mode else "black"
        panel_bg = "#1e1e1e" if dark_mode else "#f0f0f0"
        label_bg = "rgba(255,255,255,100)" if dark_mode else "rgba(0,0,0,160)"

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {window_bg};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                color: {text_color};
            }}
        """)

        for text in (self.turn_text, self.timer_text):
            text.setStyleSheet(f"""
                font-size: 18px; font-weight: bold; color: white;
                background-color: {label_bg};
                padding: 6px 14px; border-radius: 8px;
            """)

        self.top_bar.setStyleSheet(f"background-color: {panel_bg};")
        self.settings_panel.setStyleSheet(f"background-color: {panel_bg};")

    """
    Play click sound effect.
    """
    def play_click_sound(self):
        self.click_sound.play()

    """
    Play move sound if sound is enabled.
    """
    def play_move_sound(self):
        if self.sound_enabled:
            self.move_sound.play()

    """
    Play king promotion sound if sound is enabled.
    """
    def play_king_sound(self):
        if self.sound_enabled:
            self.king_sound.play()

    """
    Play game start sound if sound is enabled.
    """
    def play_start_sound(self):
        if self.sound_enabled:
            self.game_start_sound.play()

    """
    Play random win sound if sound is enabled.
    """
    def play_win_sound(self):
        if self.sound_enabled:
            self.win_sound.setSource(QUrl.fromLocalFile(
                random.choice(SOUND_GAME_WIN)
            ))
            self.win_sound.play()

    """
    Play random loss sound if sound is enabled.
    """
    def play_lose_sound(self):
        if self.sound_enabled:
            self.lose_sound.setSource(QUrl.fromLocalFile(
                random.choice(SOUND_GAME_LOSE)
            ))
            self.lose_sound.play()