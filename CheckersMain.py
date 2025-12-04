import sys
from PySide6.QtWidgets import QApplication
from CheckersMenu import CheckersMenu


def main():
    app = QApplication(sys.argv)

    menu = CheckersMenu()
    menu.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
