import os

from PyQt6 import QtWidgets
from pyogg import FlacFile
from scipy.io import wavfile
from src.FormatErrorDialog.FormatErrorDialog import Ui_UnsupportedFormatDialog


# A class that takes the name of the file and creates a transcript out of it, if possible.
class FileTranscript:

    supportedExtensions = ('.wav', '.aiff', 'aifc', '.flac')

    def __init__(self, fileName, parentWidget):
        self.fileName = fileName
        self.checkFileFormat(parentWidget)

    # Checks if .wav file is in uncompressed (PCM/LPCM) format.
    def isLPCMFormat(self):
        try:
            # wavfile.read docs - "Return the sample rate (in samples/sec) and data from an LPCM WAV file."
            sampleRate, data = wavfile.read(self.fileName)
            return True
        except ValueError as e:
            return False
        except:
            return False

    # Checks if .flac file is in OGG container.
    def isOggFormat(self):
        try:
            # PyOgg docs - "Opens and reads an OGG-FLAC file to a buffer."
            flac = FlacFile(self.fileName)
            return True
        except ValueError as e:
            return False
        except:
            return False

    # Checks if selected file is in supported file format. If not, displays an error dialog.
    def checkFileFormat(self, parentWidget):
        # init format error dialog
        invalidFormatDialog = QtWidgets.QDialog(parentWidget)
        invalidFormatDialogUI = Ui_UnsupportedFormatDialog()
        invalidFormatDialogUI.setupUi(invalidFormatDialog)

        filename, fileExtension = os.path.splitext(self.fileName)

        if fileExtension == '.wav' and not self.isLPCMFormat():
            # self.reformatFile()
            invalidFormatDialog.show()

        if fileExtension == '.flac' and self.isOggFormat():
            # self.reformatFile()
            invalidFormatDialog.show()

        if fileExtension not in FileTranscript.supportedExtensions:
            # self.reformatFile()
            invalidFormatDialog.show()

    # def reformatFile(self):
    #     return
