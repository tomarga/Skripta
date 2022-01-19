import os.path

from PyQt6.QtGui import QValidator


class FileInputValidator(QValidator):
    """
    File input text validator.
    """

    def validate(self, input: str, cursorPosition: int):
        """
        :param input: LineEdit text
        :param cursorPosition:
        :return: Acceptable if the input contains a path to existing file,
                 Intermediate, otherwise.
        """

        if os.path.isfile(input):
            return (QValidator.State.Acceptable, input, cursorPosition)

        return (QValidator.State.Intermediate, input, cursorPosition)
