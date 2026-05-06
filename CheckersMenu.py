import os
from PySide6.QtCore import Qt, QSize, QUrl, Signal
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout, QMessageBox
from PySide6.QtMultimedia import QSoundEffect

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 464

WINDOW_TITLE = "Checkers Game"
BACKGROUND_IMAGE = "Game-Design/menu-background.png"
CHECKERS_ICON_LOGO_IMAGE = "Game-Design/checkers-black2.png"
CHECKERS_LOGO_IMAGE = "Game-Design/checkers-logo.png"
START_BUTTON_IMAGE = "Game-Design/start_button.png"
RULES_BUTTON_IMAGE = "Game-Design/rules_button.png"
GAMEMODE_BUTTON_IMAGE = "Game-Design/gamemode_button.png"
CHANGEBG_BUTTON_IMAGE = "Game-Design/changebg_button.png"
SETTINGS_ICON = "Game-Design/settings-icon.png"
BACK_ICON = "Game-Design/back-icon.png"
SOUNDON_ICON = "Game-Design/soundon-icon.png"
SOUNDOFF_ICON = "Game-Design/soundoff-icon.png"
BACKGROUNDS = [
    "Game-Design/checkers-BG1-mini.png",
    "Game-Design/checkers-BG2-mini.png",
    "Game-Design/checkers-BG3-mini.png"
]

SOUND_MENU_FILE = "Game-Sounds/Menu-Sound.wav"
SOUND_CLICK_FILE = "Game-Sounds/Click_Sound.wav"
INTRO_SOUND_FILE = "Game-Sounds/game-intro.wav"

class CheckersMenu(QMainWindow):

    # Signal that sends the chosen background, game mode, and sound mode to the main manager.
    start_game_signal = Signal(str, str, bool)

    """Initialize the Checkers menu Window

    Setups:
    - Window properties.
    - Background and logo images.
    - Sound effects.
    - UI elements and layout.
    - Default game settings.

    :param sound_enabled - Wheather sound is enabled on startup.
    :type sound_enabled: bool
    """
    def __init__(self, sound_enabled = True):
        super().__init__()

        self.backgrounds = BACKGROUNDS

        self.bg_num = 1
        self.game_mode = "1v1"
        self.game_starting = False
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
        self.intro_sound.playingChanged.connect(self.on_intro_sound_changed)

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

        self.setup_layout()

        self.update_bg_preview()
        self.update_gm_preview()

        if self.sound_enabled:
            self.menu_sound.play()

    """
    Create and configure all UI elements in the menu.
    
    Including Start, Rules, Background and Game mode selectors and previews and Settings panel.
    Applies styling and connects signal to handlers. 
    """
    def setup_layout(self):
        self.start_button = QPushButton(self.label)
        self.start_button.setIcon(QIcon(START_BUTTON_IMAGE))
        self.start_button.move(100, 100)
        self.start_button.clicked.connect(self.start_game)

        self.rules_button = QPushButton(self.label)
        self.rules_button.move(125, 210)
        self.rules_button.setIcon(QIcon(RULES_BUTTON_IMAGE))
        self.rules_button.clicked.connect(self.show_rules)

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

        for btn in (self.start_button, self.rules_button, self.bg_button, self.gm_button):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; outline: none; }")
            btn.setIconSize(QSize(150, 150))
        self.rules_button.setIconSize(QSize(150, 90))
        self.start_button.setIconSize(QSize(200, 200))

        self.settings_btn = QPushButton(self)
        self.settings_btn.setIcon(QIcon(SETTINGS_ICON))
        self.settings_btn.move(WINDOW_WIDTH - 50, 10)
        self.settings_btn.clicked.connect(self.toggle_settings_panel)

        self.settings_panel = QWidget(self)
        self.settings_panel.setGeometry(WINDOW_WIDTH - 60, 50, 150, 100)
        self.settings_panel.hide()

        panel_layout = QVBoxLayout(self.settings_panel)
        panel_layout.setContentsMargins(10, 0, 10, 10)
        panel_layout.setSpacing(5)

        self.sound_btn = QPushButton()
        self.update_sound_icon()
        self.sound_btn.clicked.connect(self.toggle_sound)

        self.exit_btn = QPushButton()
        self.exit_btn.setIcon(QIcon(BACK_ICON))
        self.exit_btn.clicked.connect(self.close)

        for btn in (self.settings_btn, self.sound_btn, self.exit_btn):
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { padding: 0px; border: none; }")
            btn.setFixedSize(36, 36)
            btn.setIconSize(QSize(36, 36))

        panel_layout.addWidget(self.sound_btn)
        panel_layout.addWidget(self.exit_btn)

    """
    Switch to the next avilable background and updates the preview accordingly.
    """
    def next_background(self):
        self.bg_num = (self.bg_num+1) % len(self.backgrounds)
        self.update_bg_preview()
        self.click_sound.play()

    """
    Updates the background preview image and displays the selected background image.
    """
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

    """
    Toggles between avilable game modes.
    
    Modes:
    - "1v1"
    - "agent"
    """
    def next_gamemode(self):
        self.game_mode = "agent" if self.game_mode == "1v1" else "1v1"
        self.update_gm_preview()
        self.click_sound.play()

    """
    Updates the game mode preview label and displays the current mode in styled text.   
    """
    def update_gm_preview(self):
        self.gm_preview.setText(self.game_mode.upper())
        self.gm_preview.setAlignment(Qt.AlignCenter)
        self.gm_preview.setStyleSheet("""QLabel{font-size: 20px; font-weight: bold; 
        color: white; background-color: rgba(0,0,0,70); border-radius: 10px;}""")

    """
    Show or hide the settings panel.
    """
    def toggle_settings_panel(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())
        self.click_sound.play()

    """
    Enable or disable game sound.
    
    - Starts or stops menu music.
    - Updates sound icon.
    """
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled

        if self.sound_enabled and self.intro_sound.isPlaying() == False:
            self.menu_sound.play()
        else:
            self.menu_sound.stop()

        self.update_sound_icon()

    """
    Update the sound button icon based on current state.

    Displays either sound ON or OFF icon.
    """

    def update_sound_icon(self):
        icon = SOUNDON_ICON if self.sound_enabled else SOUNDOFF_ICON
        self.sound_btn.setIcon(QIcon(icon))

    """
    Display the game rules in a popup window.
    
    Uses a QMessageBox wit htixh text formatting.
    """
    def show_rules(self):

        rules_text = """
        <h2 align='center'>◉ Checkers 6x6 Rules ◉</h2>

        <b>Board</b><br>
        • The game is played on a 6x6 board.<br>
        • Each player starts with <b>6 pieces</b>.<br><br>

        <b>Movement</b><br>
        • Pieces move diagonally forward.<br>
        • Only one square per move.<br><br>

        <b>Capturing</b><br>
        • Capture by jumping over an opponent piece.<br>
        • If a capture is available it <b>must be taken</b>.<br><br>

        <b>Kings</b><br>
        • When a piece reaches the last row it becomes a <b>KING</b>.<br>
        • Kings move diagonally in both directions.<br><br>

        <b>Winning</b><br>
        • You win if your opponent has:<br>
        &nbsp;&nbsp;– No pieces left<br>
        &nbsp;&nbsp;– No legal moves<br><br>

        <i>Good luck and enjoy the game!</i>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("Checkers Rules")
        msg.setTextFormat(Qt.RichText)
        msg.setText(rules_text)
        msg.addButton("Close", QMessageBox.RejectRole)

        msg.exec()

    """
    Handle start button click.
    
    - Disables button interaction.
    - Plays intro sound (if enabled).
    - Lunches game immediately if sound is disabled.
    """
    def start_game(self):
        self.start_button.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        if self.sound_enabled:
            self.menu_sound.stop()
            self.intro_sound.play()
        else:
            self.launch_game()

    """
    Sends a signal to start the game with the selected settings and closes the menu.
    """
    def launch_game(self):
        selected_bg = self.backgrounds[self.bg_num - 1]

        self.start_game_signal.emit(selected_bg, self.game_mode, self.sound_enabled)

        self.close()

    """
    Triggered when intro sound state changes.
    
    Starts the game once the intro sound finished.
    """
    def on_intro_sound_changed(self):
        if not self.intro_sound.isPlaying() and not self.game_starting:
            self.game_starting = True
            self.launch_game()