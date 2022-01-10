from enum import Enum


class API(Enum):
    """
    Utility Enumeration of all speech recognition API types.
    """

    GOOGLE = 1
    GOOGLE_CLOUD = 2
    SPHINX = 3
    HOUNDIFY = 4

    def __str__(self):
        """
        :return: The option's name in lowercase
        """

        return self.name.lower()
