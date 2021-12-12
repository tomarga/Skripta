import os

from PyQt6 import QtWidgets
from pyogg import FlacFile
from scipy.io import wavfile
from src.FormatErrorDialog.FormatErrorDialog import Ui_UnsupportedFormatDialog


class FileTranscript:
    """
    A class that takes the name of the file and handles its transcription.
    """

    supportedExtensions = ('.wav', '.aiff', 'aifc', '.flac')

    def __init__(self, fileName, parentWidget):
        """
        Constructor method.
        :param fileName: Name of the audio file that the user wants to transcribe.
        :param parentWidget: Main Widget.
        """

        self.fileName = fileName
        self.checkFileFormat(parentWidget)

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
        except:
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
        except:
            return False

    def checkFileFormat(self, parentWidget):
        """
        Checks if selected file is in supported file format.
        Supported audio formats are:
        WAV(must be in PCM/LPCM format), AIFF, AIFF-C and FLAC(OGG-FLAC is not supported).
        If not, displays an error dialog with an appropriate message.
        :param parentWidget: MainWidget
        """

        # init format error dialog
        invalidFormatDialog = QtWidgets.QDialog(parentWidget)
        invalidFormatDialogUI = Ui_UnsupportedFormatDialog()
        invalidFormatDialogUI.setupUi(invalidFormatDialog)

        filename, fileExtension = os.path.splitext(self.fileName)

        if fileExtension == '.wav' and not self.isLPCMFormat():
            invalidFormatDialog.show()

        if fileExtension == '.flac' and self.isOggFormat():
            invalidFormatDialog.show()

        if fileExtension not in FileTranscript.supportedExtensions:
            invalidFormatDialog.show()
