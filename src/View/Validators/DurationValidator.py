import datetime

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QValidator


class DurationValidator(QValidator):
    """
    File's duration validator.
    """

    def __init__(self, parent: QObject, maxInput: str = None, minInput: str = '00:00:00'):
        """
        Initializes a validator with maximum duration.
        :param maxInput: String in format '%H:%M:%S'
        :param minInput: String in format '%H:%M:%S'
        """

        super().__init__(parent)
        
        self.maxInput = maxInput
        self.minInput = minInput

    def setMaxInput(self, maxInput: str = None):
        """
        Updates maxInput value.
        :param maxInput:
        :return:
        """

        self.maxInput = maxInput
        
    def setMinInput(self, minInput: str = None):
        """
        Updates minInput value.
        :param minInput:
        :return:
        """

        self.minInput = minInput

    def validate(self, input: str, cursorPosition: int):
        """
        :param input: LineEdit text
        :param cursorPosition:
        :return: Acceptable if the input represents duration between min and max,
                 Intermediate if the input is in valid format and max input is unknown,
                 Invalid, otherwise.
        """

        # check if valid format
        try:
            duration = datetime.datetime.strptime(input, '%H:%M:%S')
        except ValueError as e:
            print('ValueError - validate duration: ', e.__str__())
            return (QValidator.State.Invalid, input, cursorPosition)

        # check if less than min duration
        minDuration = datetime.datetime.strptime(self.minInput, '%H:%M:%S')

        if duration < minDuration:
            return (QValidator.State.Invalid, input, cursorPosition)

        # check if exceeds max duration
        if self.maxInput is None:
            return (QValidator.State.Intermediate, input, cursorPosition)

        maxDuration = datetime.datetime.strptime(self.maxInput, '%H:%M:%S')

        if duration > maxDuration:
            return (QValidator.State.Invalid, input, cursorPosition)

        return (QValidator.State.Acceptable, input, cursorPosition)
