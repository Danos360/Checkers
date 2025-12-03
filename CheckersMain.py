import sys
from PySide6.QtWidgets import QApplication
from CheckersMenu import MenuWindow


def main():
    app = QApplication(sys.argv)
    menu = MenuWindow()
    menu.show()
    app.exec()


if __name__ == "__main__":
    main()
