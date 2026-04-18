import sys
from PySide6.QtWidgets import QApplication
from CheckersMenu import CheckersMenu
from CheckersModel import CheckersModel
from CheckersView import CheckersView
from CheckersController import CheckersController

class CheckersMain:
    """
    Initialize the application and the main menu.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.menu = None
        self.controller = None

        self.show_menu()

    """
    Create and display the main menu view.

    Connects the menu's signals to the application's launcher logic
    to ensure correct transition to the game.

    :param sound_enabled: Initial state of the sound setting.
    :type sound_enabled: bool
    """
    def show_menu(self, sound_enabled=True):
        self.menu = CheckersMenu(sound_enabled)

        self.menu.start_game_signal.connect(self.launch_game)

        self.menu.show()

    """
    Initialize and launch the Checkers game.

    This method acts as the bridge between the menu and the game loop.
    It initializes the MVC logic.

    :param bg: Path to the selected board background.
    :type bg: str
    
    :param mode: Selected game mode (1v1 or Agent).
    :type mode: str
    
    :param sound: Whether sound is enabled for the game session.
    :type sound: bool
    """
    def launch_game(self, bg, mode, sound):
        model = CheckersModel()
        view = CheckersView(bg, sound)

        self.controller = CheckersController(model, view, mode)

        view.back_to_menu_signal.connect(self.show_menu)

        view.show()
        view.play_start_sound()

        if self.menu:
            self.menu.close()
            self.menu = None

    """
    Execute the main event loop of the application.

    :return: Exit code of the application.
    :rtype: int
    """
    def run(self):
        return self.app.exec()

"""
Main entry point for the application.

Starts the main class that manages the game and ensures 
the program exits correctly when closed.
"""
if __name__ == "__main__":
    launcher = CheckersMain()
    sys.exit(launcher.run())
