import os
from pathlib import Path

import speech_recognition as sr


class Model:
    """
    Applications Model class - handles audio files' checkups.
    """

    def __init__(self):
        """
        Initializes a Model.
        """

    @staticmethod
    def createResultDirectory():
        """
        Creates a new HOME/Transkripti directory if it doesn't already exist.
        :return:
        """

        dirPath = str(Path.home()) + "/Transkripti"
        if not os.path.isdir(dirPath):
            os.mkdir(dirPath)

    @staticmethod
    def getAudioDuration(filePath: str):
        """
        :param filePath: Path to an audio file.
        :return: Duration of the given audio file in seconds,
                 or None if duration cannot be retrieved.
        """

        try:
            with sr.AudioFile(filePath) as source:
                return source.DURATION

        except ValueError as e:
            print('ValueError - Audio Duration: ', e.__str__())
            return None
