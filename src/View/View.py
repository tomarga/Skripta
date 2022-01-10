from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFileDialog

from src.View.MenuWidget.MenuWidget import Ui_MenuWidget
from src.View.ErrorDialog.ErrorDialog import Ui_ErrorDialog
from src.View.SuccessDialog.SuccessDialog import Ui_SuccessDialog
from src.View.ProcessingDialog.ProcessingDialog import Ui_ProcessingDialog

from enum import Enum

from src.Model.FileTypeUtil import FileTypeUtil
from src.View.MainWindow import MainWindow


class View(QObject):
    """
    Handles application's UI elements.
    """

    class DialogType(Enum):
        """
        Utility Enumeration of all dialog types.
        """
        SUCCESS = 1
        FAILED_REQUEST = 2
        PROCESSING = 3
        INVALID_FORMAT = 4
        DAMAGED_FILE = 5
        FILE_OPEN = 6
        FILE_SAVE = 7
        TIMED_OUT = 8
        UNAUTHORISED = 9

        def getErrorMessage(self):
            """
            :return: Dialog's error message depending on the type of the error (in HTML).
            """
            if self == self.INVALID_FORMAT:
                return "<html><head/><body><p align=\"center\">" \
                       "Provjerite je li datoteka u nekom od podržanih formata:<br>\n" \
                       "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C." \
                       "</p></body></html>"

            if self == self.DAMAGED_FILE:
                return "<html><head/><body><p align=\"center\" style=\"margin-right:105px;\">" \
                       "Greška pri obradi govora: <br>\n datoteka sadrži nerazumljiv govor." \
                       "</p></body></html>"

            if self == self.FAILED_REQUEST:
                return "<html><head/><body><p align=\"center\" style=\"margin-right:110px;\">" \
                       "Greška pri obradi zahtjeva: <br>\n provjerite kvalitetu internet veze." \
                       "</p></body></html>"

            if self == self.TIMED_OUT:
                return "<html><head/><body><p align=\"center\" style=\"margin-right:65px;\">" \
                       "Greška pri obradi zahtjeva: <br>\n prekinuto zbog vremenskog ograničenja." \
                       "</p></body></html>"

            if self == self.UNAUTHORISED:
                return "<html><head/><body><p align=\"center\" style=\"margin-right:35px;\">" \
                       "Greška pri obradi zahtjeva: neodobren pristup." \
                       "</p></body></html>"

        def isErrorDialog(self):
            """
            :return: True for error dialog types, False otherwise.
            """

            return self in [self.FAILED_REQUEST, self.DAMAGED_FILE, self.INVALID_FORMAT, self.TIMED_OUT, self.UNAUTHORISED]

    def __init__(self):
        """
        Initializes all UI elements.
        """

        super().__init__()

        self.menuWidget = QtWidgets.QWidget()
        self.menuWidgetUI = Ui_MenuWidget()
        self.menuWidgetUI.setupUi(self.menuWidget)

        self.mainWindow = MainWindow()
        self.mainWindow.setCentralWidget(self.menuWidget)

        self.processingDialog = QtWidgets.QDialog(self.mainWindow)
        self.processingDialogUI = self.initProcessingDialogUI()

        self.successDialog = QtWidgets.QDialog(self.mainWindow)
        self.successDialogUI = self.initSuccessDialogUI()

        self.errorDialog = QtWidgets.QDialog(self.mainWindow)
        self.errorDialogUI = self.initErrorDialogUI()

        self.selectFileDialog = self.initSelectFileDialog()
        self.saveFileDialog = self.initSaveFileDialog()
        
    def initSelectFileDialog(self):
        """
        Setups select file dialog options.
        The dialog is set to open the home directory, and show only audio files.
        :return: New QFileDialog instance.
        """

        audioExtensions = tuple(FileTypeUtil.getExtensionsForType('audio'))

        fileDialog = QFileDialog(self.mainWindow)

        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        fileDialog.setWindowTitle('Izaberi audio datoteku')
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilters(["Audio files {}".format(FileTypeUtil.listExtensionsAsString(audioExtensions))])
        fileDialog.setDirectory(str(Path.home()))

        return fileDialog

    def initSaveFileDialog(self):
        """
        Setups save file dialog options.
        The dialog is set to open the 'home/Transkripti' directory, and show only common textual files.
        The default file name is set to 'Novi_transkript.txt'.
        :return: New QFileDialog instance.
        """

        transcriptsDirName = str(Path.home()) + "/Transkripti"

        fileDialog = QFileDialog(self.mainWindow)

        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        fileDialog.setWindowTitle('Spremi Transkript kao')
        fileDialog.setFileMode(QFileDialog.FileMode.AnyFile)
        fileDialog.setNameFilters(FileTypeUtil.getTextualExtensionsAsList())
        fileDialog.setDirectory(transcriptsDirName)
        fileDialog.selectFile(transcriptsDirName + "/Novi_transkript.txt")

        return fileDialog

    def initErrorDialogUI(self):
        """
        Initializes Error dialog's UI.
        :return: Created instance of Ui_ErrorDialog.
        """

        errorDialogUI = Ui_ErrorDialog()
        errorDialogUI.setupUi(self.errorDialog)
        return errorDialogUI

    def initProcessingDialogUI(self):
        """
        Initializes Loading dialog's ui.
        :return: Created instance of Ui_ProcessingDialog.
        """

        processingDialogUI = Ui_ProcessingDialog()
        processingDialogUI.setupUi(self.processingDialog)
        return processingDialogUI

    def initSuccessDialogUI(self):
        """
        Initializes Success dialog's ui.
        :return: Created instance of Ui_SuccessDialog.
        """

        successDialogUI = Ui_SuccessDialog()
        successDialogUI.setupUi(self.successDialog)
        return successDialogUI

    def openDialog(self, type: DialogType):
        """
        Opens a dialog of specified type as a modal.
        For error typed dialogs, the error message is updated with appropriate message beforehand.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        if type.isErrorDialog():
            self.errorDialogUI.setText(type.getErrorMessage())
            self.errorDialog.open()

        if type == self.DialogType.SUCCESS:
            self.successDialog.open()

        if type == self.DialogType.PROCESSING:
            self.processingDialog.open()

        if type == self.DialogType.FILE_OPEN:
            self.selectFileDialog.open()

        if type == self.DialogType.FILE_SAVE:
            self.saveFileDialog.open()

    def closeDialog(self, type: DialogType):
        """
        Closes a dialog of specified type.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        if type.isErrorDialog():
            self.errorDialog.close()

        if type == self.DialogType.SUCCESS:
            self.successDialog.close()

        if type == self.DialogType.PROCESSING:
            self.processingDialog.close()
            
        if type == self.DialogType.FILE_OPEN:
            self.selectFileDialog.close()

        if type == self.DialogType.FILE_SAVE:
            self.saveFileDialog.close()

    def closeAllDialogs(self):
        """
        Closes all application's dialogs.
        :return:
        """

        for type in self.DialogType:
            self.closeDialog(type)
