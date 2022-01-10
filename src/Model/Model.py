import os
from pathlib import Path


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
