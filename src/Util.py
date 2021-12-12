import mimetypes


class Util:
    """
    Utility class, containing various helper methods.
    """

    @staticmethod
    def getExtensionsForType(generalType):
        """
        For general file type (e.g. audio, image) returns the list of all possible format extensions.
        :param generalType: String containing the type of file
        :return: The list of all format extensions for given type.
        """

        mimetypes.init()
        for extension in mimetypes.types_map:
            if mimetypes.types_map[extension].split('/')[0] == generalType:
                yield extension

    @staticmethod
    def listExtensionsAsString(extensions):
        """
        For given list of file extensions, returns the string "(*ext1 *ext2 ... *extn)".
        The result format is customized to match the 'open file dialog' supported extensions' parameter.
        :param extensions: List of string containing file extensions.
        :return: A string like "(*ext1 *ext2 ... *extn)".
        """

        result = "("
        for extension in extensions:
            result += '*' + extension + ' '
        result = result[:-1]
        result += ')'
        return result
