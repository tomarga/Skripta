import os

from scipy.io import wavfile
from pyogg import FlacFile, PyOggError

from src.Model.FileTypeUtil import FileTypeUtil


class Model:
    """
    Applications Model class - handles audio files' checkups.
    """

    def __init__(self):
        """
        Initializes a Model.
        """

    def checkFileFormat(self, filePath: str):
        """
        Checks if selected file is in (Speech Recognition) supported file format.
        Supported audio formats are:
        WAV(must be in PCM/LPCM format), AIFF, AIFF-C and FLAC(OGG-FLAC is not supported).
        :return:
            <code>True</code> if the file is supported
            <code>False</code> otherwise
        """

        filename, fileExtension = os.path.splitext(filePath)

        if fileExtension == '.wav' and not self.isLPCMFormat(filePath):
            return False

        if fileExtension == '.flac' and self.isOggFormat(filePath):
            return False

        if fileExtension not in FileTypeUtil.getSupportedExtensions():
            return False

        return True

    @staticmethod
    def isLPCMFormat(filePath: str):
        """
        Checks if .wav file is in a format supported by the SpeechRecognition package.
        :return:
            <code>True</code> if the file is in uncompressed (PCM/LPCM) format
            <code>False</code> otherwise
        """

        try:
            # wavfile.read docs - "Return the sample rate (in samples/sec) and data from an LPCM WAV file."
            sampleRate, data = wavfile.read(filePath)
            return True

        except ValueError as e:
            return False

    @staticmethod
    def isOggFormat(filePath: str):
        """
        Checks if .flac file is in a format unsupported by the SpeechRecognition package.
        :return:
            <code>True</code> if the file s wrapped in OGG container
            <code>False</code> otherwise
        """

        try:
            # PyOgg docs - "Opens and reads an OGG-FLAC file to a buffer."
            flac = FlacFile(filePath)
            return True

        except ValueError as e:
            return False

        except PyOggError as e:
            return False
