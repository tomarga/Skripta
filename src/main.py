import os
from pathlib import Path

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QFileDialog

from src.MainWindow.MainWindow import Ui_MainWidget
from FileTranscript import FileTranscript
from Util import Util

# Absolute path to app root dir
ROOT_DIRECTORY = Path(__file__).resolve().parent.parent


def setupResources():
    """
    Setups resources file shortcuts.
    """

    QtCore.QDir.addSearchPath('icons', os.fspath(ROOT_DIRECTORY / "resources/icons"))
    QtCore.QDir.addSearchPath('images', os.fspath(ROOT_DIRECTORY / "resources/images"))


def setupUI(parentWidget):
    """
    Setups UI and connects main buttons' signals to slots.
    :param parentWidget: Main Widget
    """

    ui.setupUi(parentWidget)
    ui.LoadButton.clicked.connect(loadButtonClicked)


def setupWindow(parentWidget):
    """
    Setups the title, favicon and size of the main window and connects it to parent widget.
    :param parentWidget: Main Widget
    :return: Created QMainWindow instance
    """

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Skripta")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icons:favicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    window.setWindowIcon(icon)
    window.setFixedSize(800, 800)
    window.setCentralWidget(parentWidget)
    return window


def loadButtonClicked():
    """
    Slot method connected to 'Load Btn' option.
    Opens a dialog for audio file selection and initializes an object to handle the file transcription.
    """

    audioExtensions = tuple(Util.getExtensionsForType('audio'))
    file = QFileDialog.getOpenFileName(mainWidget, 'Izaberi audio datoteku', str(Path.home()),
                                       "Audio files {}".format(Util.listExtensionsAsString(audioExtensions)))

    if file[0] and file[1]:
        fileTranscript = FileTranscript(file[0], mainWidget)


if __name__ == "__main__":
    """
    Main method: setups resources and user interface and starts the initial menu.
    """

    import sys

    setupResources()

    app = QtWidgets.QApplication(sys.argv)
    mainWidget = QtWidgets.QWidget()

    ui = Ui_MainWidget()
    setupUI(mainWidget)

    appWindow = setupWindow(mainWidget)
    appWindow.show()

    sys.exit(app.exec())
