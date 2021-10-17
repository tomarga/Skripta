from PyQt6 import QtWidgets, QtGui

from MainWindow import Ui_MainWidget

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    MainWidget = QtWidgets.QWidget()
    ui = Ui_MainWidget()
    ui.setupUi(MainWidget)

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Skripta")
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("./resources/favicon.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
    window.setWindowIcon(icon)
    window.setFixedSize(800, 800)
    window.setCentralWidget(MainWidget)

    window.show()
    sys.exit(app.exec())
