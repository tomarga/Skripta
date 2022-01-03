import subprocess, os, platform
from pathlib import Path

import speech_recognition
import speech_recognition as sr

from PyQt6 import QtWidgets
from pyogg import FlacFile
from scipy.io import wavfile

from PyQt6.QtWidgets import QFileDialog

from src.ErrorDialog.ErrorDialog import Ui_ErrorDialog
from src.SuccessDialog.SuccessDialog import Ui_SuccessDialog
from src.Util import Util


class FileTranscript:
    """
    A class that takes the name of the file and handles its transcription.
    """

    supportedExtensions = ('.wav', '.aiff', 'aifc', '.flac')

    def __init__(self, fileName, parentWidget):
        """
        Constructor method.
        Triggers transcript creation.
        Displays the appropriate success/failure dialog when the transcription process is over.

        :param fileName: Name of the audio file that the user wants to transcribe.
        :param parentWidget: Main Widget.
        """

        self.fileName = fileName
        self.parentWidget = parentWidget

        self.invalidFormatDialog = QtWidgets.QDialog(self.parentWidget)
        self.initFormatErrorDialog()

        self.failedTranscriptionDialog = QtWidgets.QDialog(self.parentWidget)
        self.initFailedTranscriptionDialog()

        self.successDialog = QtWidgets.QDialog(self.parentWidget)
        self.initSuccessDialog()

        if not self.checkFileFormat():
            self.invalidFormatDialog.exec()
            return

        self.resultFilePath = self.createTranscript()
        if not self.resultFilePath:
            self.failedTranscriptionDialog.exec()
        elif self.resultFilePath != "canceled":
            self.successDialog.exec()

    def initFormatErrorDialog(self):
        """
        Initializes Format Error dialog with an appropriate message.
        :return:
        """

        invalidFormatMessage = "<html><head/><body><p align=\"center\">" \
                               "Provjerite je li datoteka u nekom od podržanih formata:<br>\n" \
                               "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C." \
                               "</p></body></html>"

        invalidFormatDialogUI = Ui_ErrorDialog()
        invalidFormatDialogUI.setupUi(self.invalidFormatDialog, invalidFormatMessage)

    def initFailedTranscriptionDialog(self):
        """
        Initializes Failed Transcription dialog with an appropriate message.
        :return:
        """

        invalidFormatMessage = "<html><head/><body><p align=\"center\">" \
                               "Greška pri procesiranju: oštećena ili nepodržana audio datoteka.<br>\n" \
                               "Provjerite je li datoteka u nekom od podržanih formata:<br>\n" \
                               "WAV (PCM/LPCM), FLAC (nativni), AIFF i AIFF-C." \
                               "</p></body></html>"

        invalidFormatDialogUI = Ui_ErrorDialog()
        invalidFormatDialogUI.setupUi(self.failedTranscriptionDialog, invalidFormatMessage)

    def initSuccessDialog(self):
        """
        Initializes Success dialog's ui.
        :return:
        """

        successDialogUI = Ui_SuccessDialog()
        successDialogUI.setupUi(self.successDialog)
        successDialogUI.OpenFileButton.clicked.connect(self.openTranscriptFile)

    def isLPCMFormat(self):
        """
        Checks if .wav file is in a format supported by the SpeechRecognition package.
        :return:
            <code>True</code> if the file is in uncompressed (PCM/LPCM) format
            <code>False</code> otherwise
        """

        try:
            # wavfile.read docs - "Return the sample rate (in samples/sec) and data from an LPCM WAV file."
            sampleRate, data = wavfile.read(self.fileName)
            return True
        except ValueError as e:
            return False

    def isOggFormat(self):
        """
        Checks if .flac file is in a format unsupported by the SpeechRecognition package.
        :return:
            <code>True</code> if the file s wrapped in OGG container
            <code>False</code> otherwise
        """
        try:
            # PyOgg docs - "Opens and reads an OGG-FLAC file to a buffer."
            flac = FlacFile(self.fileName)
            return True
        except ValueError as e:
            return False

    def checkFileFormat(self):
        """
        Checks if selected file is in (Speech Recognition) supported file format.
        Supported audio formats are:
        WAV(must be in PCM/LPCM format), AIFF, AIFF-C and FLAC(OGG-FLAC is not supported).
        :return:
            <code>True</code> if the file is supported
            <code>False</code> otherwise
        """

        filename, fileExtension = os.path.splitext(self.fileName)

        if fileExtension == '.wav' and not self.isLPCMFormat():
            return False

        if fileExtension == '.flac' and self.isOggFormat():
            return False

        if fileExtension not in FileTranscript.supportedExtensions:
            return False

        return True

    def createTranscript(self):
        """
        Creates transcript out of an audio file and saves the result in a new file.
        :return: A string containing path to newly made textual file, if successfull.
                 "canceled" if the user cancels the process meanwhile.
                 An empty string, otherwise.
        """

        recognizer = sr.Recognizer()
        audioFile = sr.AudioFile(self.fileName)

        try:
            with audioFile as source:
                audio = recognizer.record(source)
        except ValueError as e:
            print("ValueError - Audio as Source: " + e.__str__())
            return ""

        try:
            resultData = recognizer.recognize_google(audio)
            print(resultData)

            transcriptsDirName = str(Path.home()) + "/Transkripti"
            if not os.path.isdir(transcriptsDirName):
                os.mkdir(transcriptsDirName)

            transcriptFile = QFileDialog.getSaveFileName( self.parentWidget,
                "Spremi transkript kao", transcriptsDirName + "/Novi_transkript.txt", Util.getTextualExtensions())

            if transcriptFile[0] and transcriptFile[1]:
                with open(transcriptFile[0], 'w') as file:
                    file.write(resultData)
                return transcriptFile[0]

        except speech_recognition.RequestError as e:
            print("RequestError - Transcription" + e.__str__())
            return ""
        except speech_recognition.UnknownValueError as e:
            print("UnknownValueError - Transcription" + e.__str__())
            return ""

        return "canceled"

    def openTranscriptFile(self):
        """
        Opens the latest transcript file using its default application.
        :return:
        """

        if platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', self.resultFilePath))
        elif platform.system() == 'Windows':  # Windows
            os.startfile(self.resultFilePath)
        else:  # linux
            subprocess.call(('xdg-open', self.resultFilePath))
