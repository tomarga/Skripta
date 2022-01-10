import os, subprocess, platform

from PyQt6.QtCore import QProcess

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

        self.view.menuWidgetUI.LoadButton.clicked.connect(self.reset)
        self.view.menuWidgetUI.LoadButton.clicked.connect(lambda: self.view.openDialog(self.view.DialogType.FILE_OPEN))

        self.view.selectFileDialog.fileSelected.connect(self.startFileTranscription)

        self.workerProcess.readyReadStandardOutput.connect(self.handleSuccess)
        self.workerProcess.readyReadStandardError.connect(self.handleFailure)

        self.view.processingDialogUI.StopButton.clicked.connect(self.workerProcess.kill)
        self.view.processingDialogUI.StopButton.clicked.connect(lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))

        self.view.processingDialog.rejected.connect(self.workerProcess.kill)
        self.view.processingDialog.rejected.connect(lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))

        self.view.saveFileDialog.fileSelected.connect(self.writeToFile)

        self.view.successDialogUI.OpenFileButton.clicked.connect(self.openNewFile)
        self.view.successDialogUI.OpenFileButton.clicked.connect(lambda: self.view.closeDialog(self.view.DialogType.SUCCESS))

    def startFileTranscription(self, filePath: str):
        """
        Slot that handles transcription from file.
        If the given filePath is empty, it does nothing.
        Otherwise, the transcription process is started in a separate process.
        :return:
        """

        if not filePath:
            return

        from src.main import ROOT_DIRECTORY
        self.workerProcess.start("python3", [ROOT_DIRECTORY.__str__() + "/src/Model/worker.py", filePath])

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
        self.view.closeAllDialogs()

        self.newFilePath = ""
        self.resultText = ""
