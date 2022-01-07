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

    class DialogTypes(Enum):
        """
        Utility Enumeration of all dialog types.
        """
        SUCCESS = 1
        FAILURE = 2
        PROCESSING = 3
        INVALID_FORMAT = 4
        FILE_OPEN = 5
        FILE_SAVE = 6

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

        self.invalidFormatDialog = QtWidgets.QDialog(self.mainWindow)
        self.invalidFormatDialogUI = self.initFormatErrorDialogUI()

        self.processingDialog = QtWidgets.QDialog(self.mainWindow)
        self.processingDialogUI = self.initProcessingDialogUI()

        self.failedTranscriptionDialog = QtWidgets.QDialog(self.mainWindow)
        self.failedTranscriptionDialogUI = self.initFailedTranscriptionDialogUI()

        self.successDialog = QtWidgets.QDialog(self.mainWindow)
        self.successDialogUI = self.initSuccessDialogUI()

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

    def initFormatErrorDialogUI(self):
        """
        Initializes Format Error dialog with an appropriate message.
        :return: Created instance of Ui_ErrorDialog.
        """

        invalidFormatMessage = "<html><head/><body><p align=\"center\">" \
                               "Provjerite je li datoteka u nekom od podržanih formata:<br>\n" \
                               "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C." \
                               "</p></body></html>"

        invalidFormatDialogUI = Ui_ErrorDialog()
        invalidFormatDialogUI.setupUi(self.invalidFormatDialog, invalidFormatMessage)
        return invalidFormatDialogUI

    def initFailedTranscriptionDialogUI(self):
        """
        Initializes Failed Transcription dialog with an appropriate message.
        :return: Created instance of Ui_ErrorDialog.
        """

        failedTranscriptionMessage = "<html><head/><body><p align=\"center\">" \
                                     "Greška pri obradi: oštećena ili nepodržana audio datoteka.<br>\n" \
                                     "Provjerite je li datoteka u nekom od podržanih formata:<br>\n" \
                                     "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C." \
                                     "</p></body></html>"

        failedTranscriptionUI = Ui_ErrorDialog()
        failedTranscriptionUI.setupUi(self.failedTranscriptionDialog, failedTranscriptionMessage)
        return failedTranscriptionUI

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

    def openDialog(self, type: DialogTypes):
        """
        Opens a dialog of specified type.
        In case of the processing dialog exceptionally, the main window is disabled.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        if type == self.DialogTypes.SUCCESS:
            self.successDialog.open()

        if type == self.DialogTypes.FAILURE:
            self.failedTranscriptionDialog.open()

        if type == self.DialogTypes.PROCESSING:
            self.processingDialog.open()

        if type == self.DialogTypes.INVALID_FORMAT:
            self.invalidFormatDialog.open()

        if type == self.DialogTypes.FILE_OPEN:
            self.selectFileDialog.open()

        if type == self.DialogTypes.FILE_SAVE:
            self.saveFileDialog.open()

    def closeDialog(self, type: DialogTypes):
        """
        Closes a dialog of specified type.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        if type == self.DialogTypes.SUCCESS:
            self.successDialog.close()

        if type == self.DialogTypes.FAILURE:
            self.failedTranscriptionDialog.close()

        if type == self.DialogTypes.PROCESSING:
            self.processingDialog.close()

        if type == self.DialogTypes.INVALID_FORMAT:
            self.invalidFormatDialog.close()
            
        if type == self.DialogTypes.FILE_OPEN:
            self.selectFileDialog.close()

        if type == self.DialogTypes.FILE_SAVE:
            self.saveFileDialog.close()

    def closeAllDialogs(self):
        """
        Closes all application's dialogs.
        :return:
        """

        for type in self.DialogTypes:
            self.closeDialog(type)
