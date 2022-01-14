from enum import Enum


class API(Enum):
    """
    Utility Enumeration of all speech recognition API types.
    """

    GOOGLE = 0
    GOOGLE_CLOUD = 1
    SPHINX = 2
    HOUNDIFY = 3

    def __str__(self):
        """
        :return: The option's name in lowercase
        """

        return self.name.lower()
