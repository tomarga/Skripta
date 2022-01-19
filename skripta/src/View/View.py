from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import QFileDialog

from skripta.src.View.ResultDialog.ResultDialog import Ui_ResultDialog
from skripta.src.View.Validators.DurationValidator import DurationValidator
from skripta.src.View.Validators.FileInputValidator import FileInputValidator
from skripta.src.View.MenuWidget.MenuWidget import Ui_MenuWidget
from skripta.src.View.ErrorDialog.ErrorDialog import Ui_ErrorDialog
from skripta.src.View.FileOptionsDialog.FileOptionsDialog import Ui_OptionsDialog as Ui_FileOptionsDialog
from skripta.src.View.MicOptionsDialog.MicOptionsDialog import Ui_OptionsDialog as Ui_MicOptionsDialog
from skripta.src.View.SuccessDialog.SuccessDialog import Ui_SuccessDialog
from skripta.src.View.ProcessingDialog.ProcessingDialog import Ui_ProcessingDialog

from enum import Enum

from skripta.src.Model.Utils.FileTypeUtil import FileTypeUtil
from skripta.src.View.MainWindow import MainWindow


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
        LISTENING = 4
        INVALID_FORMAT = 5
        DAMAGED_FILE = 6
        FILE_OPEN = 7
        FILE_SAVE = 8
        GRAMMAR_OPEN = 9
        HOTWORDS_OPEN = 10
        TIMED_OUT = 11
        UNAUTHORISED = 12
        FILE_NOT_FOUND = 13
        MIC_NOT_FOUND = 14
        LISTENING_TIMED_OUT = 15
        FILE_OPTIONS = 16
        MIC_OPTIONS = 17
        RESULT = 18

        def getErrorMessage(self):
            """
            :return: Dialog's error message depending on the type of the error (in HTML).
            """
            if self == self.INVALID_FORMAT:
                return "Provjerite je li datoteka u nekom od podržanih formata: " \
                       "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C."

            if self == self.DAMAGED_FILE:
                return "Greška pri obradi govora: nerazumljiv govor."

            if self == self.FAILED_REQUEST:
                return "Greška pri obradi zahtjeva: provjerite kvalitetu internet veze."

            if self == self.TIMED_OUT:
                return "Greška pri obradi zahtjeva: prekinuto zbog vremenskog ograničenja."

            if self == self.UNAUTHORISED:
                return "Greška pri obradi zahtjeva: neodobren pristup."

            if self == self.FILE_NOT_FOUND:
                return "Greška pri obradi datoteke: nepostojeća datoteka."

            if self == self.MIC_NOT_FOUND:
                return "Greška pri slušanju: problem s mikrofonom."

            if self == self.LISTENING_TIMED_OUT:
                return "Greška pri slušanju: govor nije registriran ni nakon 5 min."

            return "Greška!"
            
        def getProcessingMessage(self):
            """
            :return: Dialog's processing message depending on the type of the process (in HTML).
            """

            if self == self.PROCESSING:
                return "Obrada audio sadržaja u tijeku."

            if self == self.LISTENING:
                return "Slušanje u tijeku."

            return "Procesiranje..."

        @staticmethod
        def getMessageHTML(message: str):
            """
            Wraps the dialog message in a HTML format.
            :param: message
            :return:
            """

            return "<html><head/><body><p align=\"center\">" + message + "</p></body></html>"

        def isErrorDialog(self):
            """
            :return: True for error dialog types, False otherwise.
            """

            return self in [self.FAILED_REQUEST, self.DAMAGED_FILE, self.INVALID_FORMAT,
                            self.TIMED_OUT, self.UNAUTHORISED, self.FILE_NOT_FOUND,
                            self.LISTENING_TIMED_OUT, self.MIC_NOT_FOUND]
        
        def isProcessingDialog(self):
            """
            :return: True for processing dialog types, False otherwise.
            """
            
            return self in [self.PROCESSING, self.LISTENING]

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
        self.selectGrammarDialog = self.initSelectGrammarDialog()
        self.selectHotwordDialog = self.initSelectHotwordsDialog()
        self.saveFileDialog = self.initSaveFileDialog()

        self.fileOptionsDialog = QtWidgets.QDialog(self.mainWindow)
        self.fileOptionsDialogUI = self.initFileOptionsDialog()
        self.setFileOptionsValidators()

        self.micOptionsDialog = QtWidgets.QDialog(self.mainWindow)
        self.micOptionsDialogUI = self.initMicOptionsDialog()
        self.setMicOptionsValidators()

        self.resultDialog = QtWidgets.QDialog(self.mainWindow)
        self.resultDialogUI = self.initResultDialogUI()

    def setFileOptionsValidators(self):
        """
        Sets validators for inputs on file options' dialog.
        :return:
        """

        # set file input validator
        fileInputValidator = FileInputValidator(self.fileOptionsDialog)
        self.fileOptionsDialogUI.fileLineEdit.setValidator(fileInputValidator)

        # set duration 'from' validator
        fromInputValidator = DurationValidator(self.fileOptionsDialog)
        self.fileOptionsDialogUI.FromLineEdit.setValidator(fromInputValidator)

        # set duration 'to' validator
        toInputValidator = DurationValidator(self.fileOptionsDialog)
        self.fileOptionsDialogUI.ToLineEdit.setValidator(toInputValidator)

        # set noise value validator
        noiseValidator = QIntValidator(0, 4000, self.fileOptionsDialog)
        self.fileOptionsDialogUI.noiseValueLineEdit.setValidator(noiseValidator)

        # set keywords sensibility validator
        sensibilityValidator = QDoubleValidator(0.0, 1.0, 2, self.fileOptionsDialog)
        sensibilityValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.fileOptionsDialogUI.sensitivityLineEdit.setValidator(sensibilityValidator)

    def setMicOptionsValidators(self):
        """
        Sets validators for inputs on mic options' dialog.
        :return:
        """

        # set duration validator
        durationValidator = DurationValidator(self.micOptionsDialog, minInput='00:00:05', maxInput='01:00:00')
        self.micOptionsDialogUI.durationLineEdit.setValidator(durationValidator)

        # set noise value validator
        noiseValidator = QIntValidator(0, 4000, self.micOptionsDialog)
        self.micOptionsDialogUI.noiseValueLineEdit.setValidator(noiseValidator)

        # set keywords sensibility validator
        sensibilityValidator = QDoubleValidator(0.0, 1.0, 2, self.micOptionsDialog)
        sensibilityValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.micOptionsDialogUI.sensitivityLineEdit.setValidator(sensibilityValidator)

    def getDialog(self, type: DialogType):
        """
        :param type: Dialog type
        :return: Corresponding QDialog instance
        """

        if type.isErrorDialog():
            return self.errorDialog

        if type.isProcessingDialog():
            return self.processingDialog

        if type == self.DialogType.SUCCESS:
            return self.successDialog

        if type == self.DialogType.FILE_OPEN:
            return self.selectFileDialog

        if type == self.DialogType.FILE_SAVE:
            return self.saveFileDialog

        if type == self.DialogType.FILE_OPTIONS:
            return self.fileOptionsDialog

        if type == self.DialogType.MIC_OPTIONS:
            return self.micOptionsDialog

        if type == self.DialogType.GRAMMAR_OPEN:
            return self.selectGrammarDialog

        if type == self.DialogType.HOTWORDS_OPEN:
            return self.selectHotwordDialog

        if type == self.DialogType.RESULT:
            return self.resultDialog

    def initFileOptionsDialog(self):
        """
        Setups transcription from file options dialog's UI.
        :return: New OptionsDialogUI instance.
        """

        optionsDialogUI = Ui_FileOptionsDialog()
        optionsDialogUI.setupUi(self.fileOptionsDialog)

        optionsDialogUI.languageComboBox.addItem('English (United States)', 'en-US')

        return optionsDialogUI

    def initMicOptionsDialog(self):
        """
        Setups transcription from file options dialog's UI.
        :return: New OptionsDialogUI instance.
        """

        optionsDialogUI = Ui_MicOptionsDialog()
        optionsDialogUI.setupUi(self.micOptionsDialog)

        optionsDialogUI.languageComboBox.addItem('English (United States)', 'en-US')

        return optionsDialogUI

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
        fileDialog.setNameFilters(["Audio datoteke {}".format(FileTypeUtil.listExtensionsAsString(audioExtensions))])
        fileDialog.setDirectory(str(Path.home()))

        return fileDialog
    
    def initSelectGrammarDialog(self):
        """
        Setups select file dialog options for the grammar file selection.
        The dialog is set to open the home directory, and show only .gram, .fsg and .jsfg files.
        :return: New QFileDialog instance.
        """

        fileDialog = QFileDialog(self.mainWindow)

        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        fileDialog.setWindowTitle('Izaberi gramatiku')
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilters(["Gramatike (*.gram *.fsg *.jsfg)"])
        fileDialog.setDirectory(str(Path.home()))

        return fileDialog

    def initSelectHotwordsDialog(self):
        """
        Setups select file dialog options for the hotwords file selection.
        The dialog is set to open the home directory, and show only .umdl and .pmdl files.
        :return: New QFileDialog instance.
        """

        fileDialog = QFileDialog(self.mainWindow)

        fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        fileDialog.setWindowTitle('Izaberi model okidača')
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilters(["Model (*.umdl *.pmdl)"])
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

    def initResultDialogUI(self):
        """
        Initializes Result dialog's ui.
        :return: Created instance of Ui_ResultDialog.
        """

        resultDialogUI = Ui_ResultDialog()
        resultDialogUI.setupUi(self.resultDialog)
        return resultDialogUI

    def openDialog(self, type: DialogType):
        """
        Opens a dialog of specified type as a modal.
        For error and processing typed dialogs, the error message is updated with appropriate message beforehand.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        if type.isErrorDialog():
            self.errorDialogUI.setText(type.getMessageHTML(type.getErrorMessage()))

        if type.isProcessingDialog():
            self.processingDialogUI.setText(type.getMessageHTML(type.getProcessingMessage()))

        self.getDialog(type).open()

    def closeDialog(self, type: DialogType):
        """
        Closes a dialog of specified type.
        :param type: Any member of DialogType enumeration.
        :return:
        """

        self.getDialog(type).close()

    def closeAllDialogs(self):
        """
        Closes all application's dialogs.
        :return:
        """

        for type in self.DialogType:
            self.closeDialog(type)
