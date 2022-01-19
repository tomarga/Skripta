from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """
    Main Window of the application.
    """

    def __init__(self, parent=None):
        """
        Initializes a main window's basic properties.
        :param parent: Parent widget.
        """

        super().__init__(parent)

        self.setWindowTitle("Skripta")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons:favicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setFixedSize(800, 800)
