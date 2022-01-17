import os
from pathlib import Path

import speech_recognition as sr
from PyQt6.QtCore import QThread

from src.Model.Utils.AlsaContext import hideAlsaErrors
from src.Model.Workers.LanguagesLookup import LanguagesLookup


class Model:
    """
    Applications Model class - handles audio files' checkups.
    """

    def __init__(self):
        """
        Initializes a Model.
        """

        self.googleLanguages = [['English (United States)', 'en-US']]

        self.thread = QThread()
        self.worker = LanguagesLookup()

        self.fetchGoogleLanguages()

    def fetchGoogleLanguages(self):
        """
        Starts a new thread that fetches supported languages.
        Saves the result to googleLanguages property.
        :return:
        """

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.setLanguages)

        self.thread.start()

    def setLanguages(self, languages: any):
        """
        Sets the given value to googleLanguages property.
        :param languages:
        :return:
        """

        self.googleLanguages = languages

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

    @staticmethod
    def getMicrophones():
        """
        :return: The list of available microphone inputs.
        """

        with hideAlsaErrors():
            return sr.Microphone.list_microphone_names()
