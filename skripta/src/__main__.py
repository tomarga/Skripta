import os
import sys
from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication

from skripta.src.View.View import View
from skripta.src.Model.Model import Model
from skripta.src.Controller.Controller import Controller

# Absolute path to app root dir ('skripta')
ROOT_DIRECTORY = Path(__file__).resolve().parent.parent


def setupResources():
    """
    Setups resources' file shortcuts.
    """

    QtCore.QDir.addSearchPath('icons', os.fspath(ROOT_DIRECTORY / "resources/icons"))
    QtCore.QDir.addSearchPath('images', os.fspath(ROOT_DIRECTORY / "resources/images"))


def main():
    """
    Main function.
    Connects the parts of MVC pattern and starts the app.
    """

    app = QApplication(sys.argv)

    setupResources()

    view = View()
    model = Model()
    controller = Controller(model, view)

    view.mainWindow.show()

    sys.exit(app.exec())
