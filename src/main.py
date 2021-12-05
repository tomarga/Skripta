import os
from pathlib import Path

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QFileDialog

from UI_MainWindow import Ui_MainWidget
from src.FileTranscript import FileTranscript
from src.Util import Util

# absolute path to app root dir
ROOT_DIRECTORY = Path(__file__).resolve().parent.parent


def setupResources():
    # setup resources path shortcuts
    QtCore.QDir.addSearchPath('icons', os.fspath(ROOT_DIRECTORY / "src/ui/resources/icons"))
    QtCore.QDir.addSearchPath('images', os.fspath(ROOT_DIRECTORY / "src/ui/resources/images"))


def setupUI(parentWidget):
    ui.setupUi(parentWidget)

    # setup signals and slots
    ui.LoadButton.clicked.connect(loadButtonClicked)


def setupWindow(parentWidget):
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Skripta")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icons:favicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    window.setWindowIcon(icon)
    window.setFixedSize(800, 800)
    window.setCentralWidget(parentWidget)
    return window


# handle file load
def loadButtonClicked():
    # Audio i Video verzija
    # file = QFileDialog.getOpenFileName(self, 'Izaberi audio/video datoteku', str(Path.home()),
    #                                            "Audio/Video files {}".format(Util.listExtensionsAsString(
    #                                                 Ui_MainWidget.audioExtensions + Ui_MainWidget.videoExtensions)))
    audioExtensions = tuple(Util.getExtensionsForType('audio'))
    file = QFileDialog.getOpenFileName(mainWidget, 'Izaberi audio datoteku', str(Path.home()),
                                       "Audio files {}".format(Util.listExtensionsAsString(audioExtensions)))

    if file[0] and file[1]:
        fileTranscript = FileTranscript(file[0], mainWidget)


if __name__ == "__main__":
    import sys

    setupResources()

    app = QtWidgets.QApplication(sys.argv)
    mainWidget = QtWidgets.QWidget()

    ui = Ui_MainWidget()
    setupUI(mainWidget)

    appWindow = setupWindow(mainWidget)
    appWindow.show()

    sys.exit(app.exec())
