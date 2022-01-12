import os, subprocess, platform
import datetime
import time

from PyQt6.QtCore import QProcess, QCoreApplication, QEvent, Qt
from PyQt6.QtGui import QKeyEvent

from src.Model.Enums.EnergyThresholdOption import EnergyThresholdOption
from src.View.Validators.DurationValidator import DurationValidator
from src.View.View import View
from src.Model.Model import Model


class Controller:
    """
    A class that handles the Model-View correspondence.
    """

    def __init__(self, model: Model, view: View):
        """
        Initializes the controller class with the given model and view instances.
        :param model: An instance of Model class.
        :param view:  An instance of View class.
        """

        self.view = view
        self.model = model

        self.resultText = ""
        self.newFilePath = ""

        self.workerProcess = QProcess()

        self.connectSignalsAndSlots()

    def connectSignalsAndSlots(self):
        """
        Connects all UI signals to appropriate slots.
        :return:
        """

        # main menu
        self.view.menuWidgetUI.LoadButton.clicked.connect(self.reset)
        self.view.menuWidgetUI.LoadButton.clicked.connect(lambda: self.view.openDialog(self.view.DialogType.LOAD_OPTIONS))

        # file input option
        self.view.optionsDialogUI.browseFileButton.clicked.connect(lambda: self.view.openDialog(self.view.DialogType.FILE_OPEN))
        self.view.selectFileDialog.fileSelected.connect(self.updateFileInputLine)
        self.view.optionsDialogUI.fileLineEdit.editingFinished.connect(self.setMaxDuration)
        self.view.optionsDialogUI.fileLineEdit.textChanged.connect(self.enableOKButton)

        # duration option
        self.view.optionsDialogUI.FromLineEdit.editingFinished.connect(self.updateToValidator)
        self.view.optionsDialogUI.ToLineEdit.editingFinished.connect(self.updateFromValidator)

        # ambient noise option
        self.view.optionsDialogUI.noiseTypeComboBox.currentTextChanged.connect(self.enableNoiseValue)

        # start transcription
        self.view.optionsDialogUI.OKButton.clicked.connect(self.startFileTranscription)

        # processing
        self.view.processingDialogUI.StopButton.clicked.connect(self.workerProcess.kill)
        self.view.processingDialogUI.StopButton.clicked.connect(lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))
        self.view.processingDialog.rejected.connect(self.workerProcess.kill)
        self.view.processingDialog.rejected.connect(lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))

        # handle result
        self.workerProcess.readyReadStandardOutput.connect(self.handleSuccess)
        self.workerProcess.readyReadStandardError.connect(self.handleFailure)
        self.view.saveFileDialog.fileSelected.connect(self.writeToFile)

        # success
        self.view.successDialogUI.OpenFileButton.clicked.connect(self.openNewFile)
        self.view.successDialogUI.OpenFileButton.clicked.connect(lambda: self.view.closeDialog(self.view.DialogType.SUCCESS))

    def enableNoiseValue(self, noiseType: str):
        """
        Enables noise value input if noise type parameter is set to 'Fiksan' or 'Hibridni'.
        :param noiseType:
        :return:
        """

        if noiseType == 'Dinamički':
            self.view.optionsDialogUI.noiseValueLineEdit.setEnabled(False)
        else:
            self.view.optionsDialogUI.noiseValueLineEdit.setEnabled(True)

    def updateToValidator(self):
        """
        Updates 'To' line validator to check that duration is not lesser
        than the one in 'From' input.
        :return:
        """

        toValidator: DurationValidator = self.view.optionsDialogUI.ToLineEdit.validator()
        toValidator.setMinInput(self.view.optionsDialogUI.FromLineEdit.text())

    def updateFromValidator(self):
        """
        Updates 'From' line validator to check that duration is not greater
        than the one in 'To' input.
        :return:
        """

        fromValidator: DurationValidator = self.view.optionsDialogUI.FromLineEdit.validator()
        fromValidator.setMaxInput(self.view.optionsDialogUI.ToLineEdit.text())

    def updateFileInputLine(self, fileInput: str):
        """
        Sets the given text to file input line edit.
        :param fileInput:
        :return:
        """

        self.view.optionsDialogUI.fileLineEdit.setText(fileInput)

        # mock 'enter' key press to trigger editFinished signal
        self.view.optionsDialogUI.OKButton.setEnabled(False)
        QCoreApplication.postEvent(self.view.optionsDialogUI.fileLineEdit,
                                   QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier))
        self.view.optionsDialogUI.OKButton.setEnabled(True)

    def setMaxDuration(self):
        """
        Sets the default duration of file in 'From' and 'To' line edits
        and setups their validation (the input cannot be longer than the max duration).
        :return:
        """

        file = self.view.optionsDialogUI.fileLineEdit.text()
        duration = self.model.getAudioDuration(file)

        if duration is not None:
            formattedDuration = time.strftime('%H:%M:%S', time.gmtime(duration))
            self.view.optionsDialogUI.ToLineEdit.setText(formattedDuration)
            self.view.optionsDialogUI.FromLineEdit.setText('00:00:00')

            # update validators
            fromValidator: DurationValidator = self.view.optionsDialogUI.FromLineEdit.validator()
            fromValidator.setMaxInput(formattedDuration)

            toValidator: DurationValidator = self.view.optionsDialogUI.ToLineEdit.validator()
            toValidator.setMaxInput(formattedDuration)

        else:
            self.view.optionsDialogUI.ToLineEdit.setText(0)

    def enableOKButton(self, fileInput: str):
        """
        Enables OK button if fileInput is not empty.
        :param fileInput:
        :return:
        """

        if fileInput.__len__():
            self.view.optionsDialogUI.OKButton.setEnabled(True)
        else:
            self.view.optionsDialogUI.OKButton.setEnabled(False)

    def startFileTranscription(self):
        """
        Slot that handles transcription from file.
        If the filePath selected in the options' dialog is empty, it does nothing.
        Otherwise, the transcription process is started in a separate process.
        :return:
        """

        filePath = self.view.optionsDialogUI.fileLineEdit.text()

        if not filePath:
            return

        # setup arguments
        args = [filePath]

        fromInput = self.view.optionsDialogUI.FromLineEdit.text()
        offset = datetime.datetime.strptime(fromInput, '%H:%M:%S').second
        args.extend(('-o', offset.__str__()))

        toInput = self.view.optionsDialogUI.ToLineEdit.text()
        to = datetime.datetime.strptime(toInput, '%H:%M:%S').second
        duration = to - offset
        args.extend(('-d', duration.__str__()))

        energyTypeInput = self.view.optionsDialogUI.noiseTypeComboBox.currentIndex()
        energyType = EnergyThresholdOption(energyTypeInput)
        args.extend(('-e', energyType.__str__()))

        energyValue = self.view.optionsDialogUI.noiseValueLineEdit.text()
        if energyValue.__len__():
            args.extend(('-sv', energyValue.__str__()))

        from src.main import ROOT_DIRECTORY
        self.workerProcess.start("python3", [ROOT_DIRECTORY.__str__() + "/src/Model/worker.py", *args])

        self.view.openDialog(self.view.DialogType.PROCESSING)

    def handleSuccess(self):
        """
        Handles the successful transcription.
        Updates the resultText attribute with the parsed data from the worker's standard output channel.
        Closes the processing dialog and opens a file save dialog.
        :return:
        """

        resultData = self.workerProcess.readAllStandardOutput()
        self.resultText = bytes(resultData).decode("utf8")

        self.view.closeDialog(self.view.DialogType.PROCESSING)

        self.model.createResultDirectory()
        self.view.openDialog(self.view.DialogType.FILE_SAVE)

    def handleFailure(self):
        """
        Handles the failed transcription.
        Closes the processing dialog and opens an error dialog with an appropriate message.
        :return:
        """

        self.view.closeDialog(self.view.DialogType.PROCESSING)

        errorData = self.workerProcess.readAllStandardError()
        errorText = bytes(errorData).decode("utf8")
        # print(errorText)

        if "OSError" in errorText:
            self.view.openDialog(self.view.DialogType.UNAUTHORISED)

        elif "UnknownValueError" in errorText:
            self.view.openDialog(self.view.DialogType.DAMAGED_FILE)

        elif "ValueError" in errorText:
            self.view.openDialog(self.view.DialogType.INVALID_FORMAT)

        elif "RequestError" in errorText:
            self.view.openDialog(self.view.DialogType.FAILED_REQUEST)

        elif "Timeout" in errorText:
            self.view.openDialog(self.view.DialogType.TIMED_OUT)

        elif "FileNotFoundError" in errorText:
            self.view.openDialog(self.view.DialogType.FILE_NOT_FOUND)

        else:
            print('Undefined error.')

    def writeToFile(self, filePath: str):
        """
        If the given filePath is valid, the result text is written into it.
        :param filePath: Path to a textual file.
        :return:
        """

        if not filePath:
            return

        self.newFilePath = filePath

        with open(filePath, 'w') as file:
            file.write(self.resultText)

        self.view.openDialog(self.view.DialogType.SUCCESS)

    def openNewFile(self):
        """
        Opens the latest transcript file using default application for its type.
        :return:
        """

        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', self.newFilePath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(self.newFilePath)
        else:  # linux
            subprocess.call(('xdg-open', self.newFilePath))

    def reset(self):
        """
        Resets the statuses/UI elements from previous transcription process.
        Closes all dialogs and resets newFilePath and resultText attributes.
        :return:
        """

        self.newFilePath = ""
        self.resultText = ""

        self.view.closeAllDialogs()
        self.view.optionsDialogUI.fileLineEdit.clear()
        self.view.optionsDialogUI.FromLineEdit.setText('00:00:00')
        self.view.optionsDialogUI.ToLineEdit.setText('00:00:00')
        self.view.optionsDialogUI.noiseTypeComboBox.setCurrentIndex(0)
        self.view.optionsDialogUI.noiseValueLineEdit.clear()
