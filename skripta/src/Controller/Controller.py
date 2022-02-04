import os, subprocess, platform
import datetime
import sys
import time
from typing import Union

from PyQt6.QtCore import QProcess, QCoreApplication, QEvent, Qt
from PyQt6.QtGui import QKeyEvent

from skripta.src.View.FileOptionsDialog.FileOptionsDialog import Ui_OptionsDialog as Ui_FileOptionsDialog
from skripta.src.View.MicOptionsDialog.MicOptionsDialog import Ui_OptionsDialog as Ui_MicOptionsDialog

from skripta.src.Model.Enums.API import API
from skripta.src.Model.Enums.EnergyThresholdOption import EnergyThresholdOption
from skripta.src.View.Validators.DurationValidator import DurationValidator
from skripta.src.View.View import View
from skripta.src.Model.Model import Model


OptionsDailogUI = Union[Ui_MicOptionsDialog, Ui_FileOptionsDialog]


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

        self.newFilePath = ""

        self.workerProcess = QProcess()

        self.connectSignalsAndSlots()

    def connectSignalsAndSlots(self):
        """
        Connects all UI signals to appropriate slots.
        :return:
        """

        # transcription options related signals and slots
        self.connectMicOptionsSignalsAndSlots()
        self.connectFileOptionsSignalsAndSlots()
        self.connectCommonOptionsSignalsAndSlots()
        # grammar
        self.view.selectGrammarDialog.fileSelected.connect(self.updateGrammarText)
        
        # processing
        self.view.processingDialogUI.StopButton.clicked.connect(self.workerProcess.kill)
        self.view.processingDialogUI.StopButton.clicked.connect(
            lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))
        self.view.processingDialog.rejected.connect(self.workerProcess.kill)
        self.view.processingDialog.rejected.connect(lambda: self.view.closeDialog(self.view.DialogType.PROCESSING))

        # handle result
        self.workerProcess.readyReadStandardOutput.connect(self.handleResult)
        self.workerProcess.readyReadStandardError.connect(self.handleFailure)

        self.view.resultDialogUI.saveButton.clicked.connect(self.startFileSave)
        self.view.saveFileDialog.fileSelected.connect(self.writeToFile)

        # success
        self.view.successDialogUI.OpenFileButton.clicked.connect(self.openNewFile)
        self.view.successDialogUI.OpenFileButton.clicked.connect(
            lambda: self.view.closeDialog(self.view.DialogType.SUCCESS))

    def connectFileOptionsSignalsAndSlots(self):
        """
        Connects signals and slots specific to file input options.
        :return:
        """

        # main menu
        self.view.menuWidgetUI.LoadButton.clicked.connect(
            lambda: self.view.openDialog(self.view.DialogType.FILE_OPTIONS))

        # options menu
        self.view.fileOptionsDialogUI.resetButton.clicked.connect(self.resetFileOptions)

        # file input option
        self.view.fileOptionsDialogUI.browseFileButton.clicked.connect(
            lambda: self.view.openDialog(self.view.DialogType.FILE_OPEN))
        self.view.selectFileDialog.fileSelected.connect(self.updateFileInputLine)
        self.view.fileOptionsDialogUI.fileLineEdit.editingFinished.connect(self.setMaxDuration)
        self.view.fileOptionsDialogUI.fileLineEdit.textChanged.connect(self.enableOKButton)

        # duration option
        self.view.fileOptionsDialogUI.FromLineEdit.editingFinished.connect(self.updateToValidator)
        self.view.fileOptionsDialogUI.ToLineEdit.editingFinished.connect(self.updateFromValidator)

        # start transcription
        self.view.fileOptionsDialogUI.OKButton.clicked.connect(self.startFileTranscription)
        
    def connectMicOptionsSignalsAndSlots(self):
        """
        Connects signals and slots specific to mic input options.
        :return: 
        """

        # main menu
        self.view.menuWidgetUI.RecordButton.clicked.connect(
            lambda: self.view.openDialog(self.view.DialogType.MIC_OPTIONS))
        self.view.menuWidgetUI.RecordButton.clicked.connect(self.updateMicOptions)

        # options menu
        self.view.micOptionsDialogUI.resetButton.clicked.connect(self.resetMicOptions)

        # hotwords
        self.view.micOptionsDialogUI.browseHotwordsButton.clicked.connect(
            lambda: self.view.openDialog(self.view.DialogType.HOTWORDS_OPEN))
        self.view.selectHotwordDialog.fileSelected.connect(self.view.micOptionsDialogUI.hotwordsLineEdit.setText)

        # start listening
        self.view.micOptionsDialogUI.OKButton.clicked.connect(self.startListening)
        
    def connectCommonOptionsSignalsAndSlots(self):
        """
        Connects signals and slots related to transcription options that exist on both mic and file options dialogs.
        :return: 
        """

        optionsDialogUis = [self.view.fileOptionsDialogUI, self.view.micOptionsDialogUI]
        
        for dialogUi in optionsDialogUis:
            
            # ambient noise option
            dialogUi.noiseTypeComboBox.currentTextChanged.connect(
                lambda noiseType, dialog=dialogUi: self.enableNoiseValue(noiseType, dialog))

            # api + language option
            self.model.worker.finished.connect(lambda languages, dialog=dialogUi: self.updateLanguagesDropdown(dialog))
            dialogUi.apiComboBox.currentTextChanged.connect(lambda text, dialog=dialogUi: self.updateLanguagesDropdown(dialog))

            # phrases + grammar
            dialogUi.apiComboBox.currentTextChanged.connect(lambda text, dialog=dialogUi: self.enablePhrasesAndGrammar(dialog))

            dialogUi.browseGrammarButton.clicked.connect(
                lambda dialog=dialogUi: self.view.openDialog(self.view.DialogType.GRAMMAR_OPEN))

    def updateMicOptions(self):
        """
        Updates the mic options dropdown with available microphone inputs.
        :return:
        """

        self.view.micOptionsDialogUI.micComboBox.clear()
        self.view.micOptionsDialogUI.micComboBox.addItems(self.model.getMicrophones())

        # set to default mic
        for index, mic in enumerate(self.model.getMicrophones()):
            if 'default' in mic.lower():
                self.view.micOptionsDialogUI.micComboBox.setCurrentIndex(index)
                break

    def updateGrammarText(self, text: str):
        """
        Update grammar line edit text on mic options or file options dialog, depending on which one is active.
        :return:
        """

        if self.view.micOptionsDialog.isVisible():
            self.view.micOptionsDialogUI.grammarLineEdit.setText(text)
        elif self.view.fileOptionsDialog.isVisible():
            self.view.fileOptionsDialogUI.grammarLineEdit.setText(text)

    def enablePhrasesAndGrammar(self, optionsDialogUi: OptionsDailogUI):
        """
        Enables 'preferred phrases' option if the currently selected api is Sphinx or Google Cloud.
        Enables 'grammar' option if the currently selected api is Sphinx.
        :param optionsDialogUi: Mic or File options dialogs UI
        :return:
        """

        api = optionsDialogUi.apiComboBox.currentText()

        isSphinx = 'sphinx' in api.lower()

        optionsDialogUi.sensitivityLineEdit.setEnabled(isSphinx)
        optionsDialogUi.grammarLineEdit.setEnabled(isSphinx)
        optionsDialogUi.browseGrammarButton.setEnabled(isSphinx)

        isSphinxOrCloud = isSphinx or 'cloud' in api.lower()

        optionsDialogUi.phrasesTextEdit.setEnabled(isSphinxOrCloud)

    def updateLanguagesDropdown(self, optionsDialogUi: OptionsDailogUI):
        """
        Update supported languages dropdown based on the given api name.
        Set default language to English (US).
        :param optionsDialogUi: Mic or File options dialogs UI
        :return:
        """

        api = optionsDialogUi.apiComboBox.currentText()

        optionsDialogUi.languageComboBox.clear()

        if 'google' in api.lower():
            for index, language in enumerate(self.model.googleLanguages):
                optionsDialogUi.languageComboBox.addItem(language[0], language[1])

                if language[1] == 'en-US':
                    optionsDialogUi.languageComboBox.setCurrentIndex(index)

        else:
            optionsDialogUi.languageComboBox.addItem('English (United States)', 'en-US')
            optionsDialogUi.languageComboBox.setCurrentIndex(0)

    def enableNoiseValue(self, noiseType: str, optionsDialogUi: OptionsDailogUI):
        """
        Enables noise value input if noise type parameter is set to 'Fiksan' or 'Hibridni'.
        :param optionsDialogUi: Mic or File options dialogs UI
        :param noiseType:
        :return:
        """

        if noiseType == 'Dinamički':
            optionsDialogUi.noiseValueLineEdit.setEnabled(False)
        else:
            optionsDialogUi.noiseValueLineEdit.setEnabled(True)

    def updateToValidator(self):
        """
        Updates 'To' line validator to check that duration is not lesser
        than the one in 'From' input.
        :return:
        """

        toValidator: DurationValidator = self.view.fileOptionsDialogUI.ToLineEdit.validator()
        toValidator.setMinInput(self.view.fileOptionsDialogUI.FromLineEdit.text())

    def updateFromValidator(self):
        """
        Updates 'From' line validator to check that duration is not greater
        than the one in 'To' input.
        :return:
        """

        fromValidator: DurationValidator = self.view.fileOptionsDialogUI.FromLineEdit.validator()
        fromValidator.setMaxInput(self.view.fileOptionsDialogUI.ToLineEdit.text())

    def updateFileInputLine(self, fileInput: str):
        """
        Sets the given text to file input line edit.
        :param fileInput:
        :return:
        """

        self.view.fileOptionsDialogUI.fileLineEdit.setText(fileInput)

        # mock 'enter' key press to trigger editFinished signal
        self.view.fileOptionsDialogUI.OKButton.setEnabled(False)
        QCoreApplication.postEvent(self.view.fileOptionsDialogUI.fileLineEdit,
                                   QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Return, Qt.KeyboardModifier.NoModifier))
        self.view.fileOptionsDialogUI.OKButton.setEnabled(True)

    def setMaxDuration(self):
        """
        Sets the default duration of file in 'From' and 'To' line edits
        and setups their validation (the input cannot be longer than the max duration).
        :return:
        """

        file = self.view.fileOptionsDialogUI.fileLineEdit.text()
        duration = self.model.getAudioDuration(file)

        if duration is not None:
            formattedDuration = time.strftime('%H:%M:%S', time.gmtime(duration))
            self.view.fileOptionsDialogUI.ToLineEdit.setText(formattedDuration)
            self.view.fileOptionsDialogUI.FromLineEdit.setText('00:00:00')

            # update validators
            fromValidator: DurationValidator = self.view.fileOptionsDialogUI.FromLineEdit.validator()
            fromValidator.setMaxInput(formattedDuration)

            toValidator: DurationValidator = self.view.fileOptionsDialogUI.ToLineEdit.validator()
            toValidator.setMaxInput(formattedDuration)

        else:
            self.view.fileOptionsDialogUI.ToLineEdit.setText('00:00:00')

    def enableOKButton(self, fileInput: str):
        """
        Enables OK button if fileInput is not empty.
        :param fileInput:
        :return:
        """

        if fileInput.__len__():
            self.view.fileOptionsDialogUI.OKButton.setEnabled(True)
        else:
            self.view.fileOptionsDialogUI.OKButton.setEnabled(False)

    def startListening(self):
        """
        Slot that handles transcription from mic input.
        The listening and transcription process is started in a separate process.
        :return:
        """

        args = self.getMicWorkerArguments()
        print(args)

        # from skripta.src.__main__ import ROOT_DIRECTORY
        # self.workerProcess.start("python3", [ROOT_DIRECTORY.__str__() + "/src/Model/worker.py", *args])

        self.workerProcess.start('worker-cli', [*args])

        self.view.openDialog(self.view.DialogType.LISTENING)

    def startFileTranscription(self):
        """
        Slot that handles transcription from file.
        If the filePath selected in the options' dialog is empty, it does nothing.
        Otherwise, the transcription process is started in a separate process.
        :return:
        """

        args = self.getFileWorkerArguments()
        print(args)

        # from skripta.src.__main__ import ROOT_DIRECTORY
        # self.workerProcess.start("python3", [ROOT_DIRECTORY.__str__() + "/src/Model/worker.py", *args])

        self.workerProcess.start('worker-cli', [*args])

        self.view.openDialog(self.view.DialogType.PROCESSING)

    def getSeconds(self, input: str):
        """
        Helper method, retrieves the number of seconds from given text input.
        :param input: String in format 'HH:MM:SS'
        :return: Number od seconds
        """

        seconds = 0

        seconds += datetime.datetime.strptime(input, '%H:%M:%S').hour * 3600
        seconds += datetime.datetime.strptime(input, '%H:%M:%S').minute * 60
        seconds += datetime.datetime.strptime(input, '%H:%M:%S').second

        return seconds

    def getFileWorkerArguments(self):
        """
        Creates a list of command line inputs for worker process in case of a file input.
        :return: The created list of arguments.
        """

        # input type
        args = ['-i', 'file']

        # file
        filePath = self.view.fileOptionsDialogUI.fileLineEdit.text()
        args.extend(('-f', filePath))

        # from
        fromInput = self.view.fileOptionsDialogUI.FromLineEdit.text()
        offset = self.getSeconds(fromInput)
        args.extend(('-o', offset.__str__()))

        # to
        toInput = self.view.fileOptionsDialogUI.ToLineEdit.text()
        to = self.getSeconds(toInput)
        duration = to - offset
        args.extend(('-d', duration.__str__()))

        # common
        args.extend(self.getCommonWorkerArguments(self.view.fileOptionsDialogUI))

        return args

    def getMicWorkerArguments(self):
        """
        Creates a list of command line inputs for worker process in case of a mic input.
        :return: The created list of arguments.
        """

        # input type
        args = ['-i', 'mic']

        # microphone
        mic = self.view.micOptionsDialogUI.micComboBox.currentIndex()
        args.extend(('-m', mic.__str__()))

        # duration
        durationInput = self.view.micOptionsDialogUI.durationLineEdit.text()
        duration = self.getSeconds(durationInput)
        args.extend(('-st', duration.__str__()))

        # hotwords
        hotword = self.view.micOptionsDialogUI.hotwordsLineEdit.text()
        if len(hotword):
            args.extend(('-hw', hotword))

        # common
        args.extend(self.getCommonWorkerArguments(self.view.micOptionsDialogUI))

        return args
    
    def getCommonWorkerArguments(self, optionsDialogUi: OptionsDailogUI):
        """
        :param optionsDialogUi: mic or file options dialog's ui
        :return: The list of command line arguments that are the same for both mic and file inputs.
        """
        
        args = []

        energyTypeInput = optionsDialogUi.noiseTypeComboBox.currentIndex()
        energyType = EnergyThresholdOption(energyTypeInput)
        args.extend(('-e', energyType.__str__()))

        energyValue = optionsDialogUi.noiseValueLineEdit.text()
        if energyValue.__len__():
            args.extend(('-sv', energyValue.__str__()))

        # api specific options
        apiValue = optionsDialogUi.apiComboBox.currentIndex()
        api = API(apiValue)
        args.extend(('-a', api.__str__()))

        language = optionsDialogUi.languageComboBox.currentData()
        args.extend(('-l', language.__str__()))

        phrasesArgs = self.getPhrasesArguments(optionsDialogUi)
        args.extend(phrasesArgs)

        grammarInput = optionsDialogUi.grammarLineEdit.text()
        if len(grammarInput) and optionsDialogUi.grammarLineEdit.isEnabled():
            args.extend(('-g', grammarInput))

        return args
        
    def getPhrasesArguments(self, optionsDialogUi: OptionsDailogUI):
        """
        :param optionsDialogUi: mic or file options dialog's ui
        :return: The list of worker's command line arguments related to preferred phrases.
        """

        args = []

        if optionsDialogUi.phrasesTextEdit.isEnabled():
            phrasesList = []
            valuesList = []

            phrasesInput = optionsDialogUi.phrasesTextEdit.toPlainText()

            lines = phrasesInput.split('\n')

            for index, line in enumerate(lines):
                if len(line) > 0:
                    phrasesList.append(line.strip())

            if optionsDialogUi.sensitivityLineEdit.isEnabled():

                phrasesList = []

                fallbackSensibility = optionsDialogUi.sensitivityLineEdit.text()
                if not self.isSensibilityInputValid(fallbackSensibility):
                    fallbackSensibility = "1"

                for line in lines:
                    words = line.strip().split()

                    if len(words) < 1:
                        continue

                    if len(words) == 1:
                        phrasesList.append(words[0])
                        valuesList.append(fallbackSensibility)
                        continue

                    if self.isSensibilityInputValid(words[-1]):
                        phrasesList.append(' '.join(words[:-1]))
                        valuesList.append(words[-1])
                    else:
                        phrasesList.append(' '.join(words))
                        valuesList.append(fallbackSensibility.__str__())

            if len(phrasesList):
                args.extend(('-p', *phrasesList))

            if len(valuesList):
                args.extend(('-pv', *valuesList))

        return args

    def isSensibilityInputValid(self, input: str):
        """
        Check if the given input represents a float value greater than 0 and less than 1.
        :param input:
        :return: True if valid, False otherwise
        """

        try:
            number = float(input)
        except ValueError as e:
            print('ValueError - invalid sensibility: ', e.__str__())
            return False

        if number < 0 or number > 1:
            return False

        return True

    def handleResult(self):
        """
        Handles the output of worker process.
        If the output indicates that the listening process is over, the message in the processing dialog is updated appropriately.
        If the output contains the resulting script, the textarea in the result dialog is filled with the parsed data
        from the worker's standard output channel and the result dialog replaces the processing dialog.
        :return:
        """

        resultData = self.workerProcess.readAllStandardOutput()
        resultText = bytes(resultData).decode("utf8")

        print('worker output:', resultText)

        # handle end of listening
        if resultText == "Done listening":
            self.view.openDialog(self.view.DialogType.PROCESSING)
            return

        # handle end of transcription
        self.view.resultDialogUI.resultTextEdit.setPlainText(resultText)

        self.view.closeDialog(self.view.DialogType.PROCESSING)
        self.view.openDialog(self.view.DialogType.RESULT)

    def handleFailure(self):
        """
        Handles the failed transcription.
        Closes the processing dialog and opens an error dialog with an appropriate message.
        :return:
        """

        errorData = self.workerProcess.readAllStandardError()
        errorText = bytes(errorData).decode("utf8")

        print('error:', errorText)

        # ignore debug.info outputs
        if "INFO:" in errorText:
            return

        # ignore alsa outputs
        if "ALSA" in errorText:
            return

        # closes processing dialog and kills the process
        self.view.closeDialog(self.view.DialogType.PROCESSING)

        if "OSError" in errorText:
            self.view.openDialog(self.view.DialogType.UNAUTHORISED)

        elif "ValueError - Mic as Source: " in errorText:
            self.view.openDialog(self.view.DialogType.MIC_NOT_FOUND)

        elif "UnknownValueError" in errorText:
            self.view.openDialog(self.view.DialogType.DAMAGED_FILE)

        elif "ValueError" in errorText:
            self.view.openDialog(self.view.DialogType.INVALID_FORMAT)

        elif "RequestError" in errorText:
            self.view.openDialog(self.view.DialogType.FAILED_REQUEST)

        elif "WaitTimeoutError - listen" in errorText:
            self.view.openDialog(self.view.DialogType.LISTENING_TIMED_OUT)

        elif "Timeout" in errorText:
            self.view.openDialog(self.view.DialogType.TIMED_OUT)

        elif "FileNotFoundError" in errorText:
            self.view.openDialog(self.view.DialogType.FILE_NOT_FOUND)

        else:
            print('Undefined error.')
            self.view.errorDialogUI.setText(self.view.DialogType.getMessageHTML('Greška!'))
            self.view.errorDialog.open()

    def startFileSave(self):
        """
        Creates the result directory if needed and opens the file save dialog.
        :return:
        """

        self.model.createResultDirectory()
        self.view.openDialog(self.view.DialogType.FILE_SAVE)

    def writeToFile(self, filePath: str):
        """
        If the given filePath is valid, the result text is written into it.
        If successful, the success dialog is opened, and the result dialog closed.
        :param filePath: Path to a textual file.
        :return:
        """

        if not filePath:
            return

        self.newFilePath = filePath

        with open(filePath, 'w') as file:
            file.write(self.view.resultDialogUI.resultTextEdit.toPlainText())

        self.view.closeDialog(self.view.DialogType.RESULT)
        self.view.resultDialog.accept()
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

    def resetFileOptions(self):
        """
        Resets the statuses/UI elements from previous transcription from file process.
        Sets the newFilePath attribute to an empty string.
        :return:
        """

        self.newFilePath = ""

        self.view.fileOptionsDialogUI.fileLineEdit.clear()
        self.view.fileOptionsDialogUI.FromLineEdit.setText('00:00:00')
        self.view.fileOptionsDialogUI.ToLineEdit.setText('00:00:00')

        self.resetCommonOptions(self.view.fileOptionsDialogUI)

    def resetMicOptions(self):
        """
        Resets the statuses/UI elements from previous transcription from mic input process.
        Sets the newFilePath attribute to an empty string.
        :return:
        """

        self.newFilePath = ""

        self.updateMicOptions()
        self.view.micOptionsDialogUI.durationLineEdit.setText('00:00:05')
        self.view.micOptionsDialogUI.hotwordsLineEdit.clear()

        self.resetCommonOptions(self.view.micOptionsDialogUI)
        
    def resetCommonOptions(self, dialogUi: OptionsDailogUI):
        """
        Resets all common file/mic options in the given dialog.
        :param dialogUi: File or mic options dialog's ui
        :return: 
        """

        dialogUi.noiseTypeComboBox.setCurrentIndex(0)
        dialogUi.noiseValueLineEdit.clear()
        dialogUi.apiComboBox.setCurrentIndex(0)
        self.updateLanguagesDropdown(dialogUi)
        dialogUi.phrasesTextEdit.clear()
        dialogUi.sensitivityLineEdit.clear()
        dialogUi.grammarLineEdit.clear()
