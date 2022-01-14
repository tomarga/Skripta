from enum import Enum


class EnergyThresholdOption(Enum):
    """
    Utility Enumeration of all energy threshold options. Represents the energy level threshold for sounds.
    Values below this threshold are considered silence, and values above this threshold are considered speech.
    The speech recognizer has the options to have the threshold fixed to one value, start with one value
    and then dynamically adjust it, or deal with it dynamically without the start value.
    """

    DYNAMIC = 0
    MIXED = 1
    FIXED = 2

    def __str__(self):
        """
        :return: The option's name in lowercase
        """

        return self.name.lower()
