import numpy as np
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal


class LanguagesLookup(QObject):
    """
    A worker class for lookup supported languages.
    """

    finished = pyqtSignal(list)

    def run(self):
        """
        Fetches the list of languages supported by Google's Speech-to-Text API.
        When done, emits the result in the format of a list of 2-element lists [language-name, language-tag].
        :return:
        """

        try:
            table = pd.read_html('https://cloud.google.com/speech-to-text/docs/languages', match='BCP-47')
            dataframe = table[0]

            languages = dataframe['Name']
            tags = dataframe['BCP-47']

            tuples = np.array((languages, tags)).T
            resultTuples = [tuple(row) for row in tuples]
            result = np.unique(resultTuples, axis=0)

        except Exception as e:
            print('Exception - fetch languages: ', e.__str__())
            self.finished.emit([['English (United States)', 'en-US']])
            return

        self.finished.emit(result)
        return
