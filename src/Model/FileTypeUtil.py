import mimetypes


class FileTypeUtil:
    """
    Utility class, containing various helper methods regarding file types and corresponding extensions.
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
        The result format is customized to match the QFile's 'open/save file dialog' supported extensions' parameter.
        :param extensions: List of string containing file extensions.
        :return: A string like "(*ext1 *ext2 ... *extn)".
        """

        result = "("
        for extension in extensions:
            result += '*' + extension + ' '
        result = result[:-1]
        result += ')'
        return result

    @staticmethod
    def getTextualExtensions():
        """
        Returns a string containing a selection of textual file extensions.
        The result format is customized to match the QFile's 'get open/save file dialog' supported extensions' parameter.
        :return: A string like "(TypeName1 *ext1;;TypeName2 *ext2;; ... ;;TypeNameN *extn)".
        """

        return "All formats (*odt *docx *uot *xml *tex *txt *html);;" \
               "ODF Text Document (*odt);;Word 2007-365 (*docx);;Unified Office Format text (*uot);;Word 2003 XML " \
               "(*xml);;HTML (*html);;TeX (*tex);;Rich text (*rtf);; Text(*txt)"

    @staticmethod
    def getTextualExtensionsAsList():
        """
        Returns a list containing a selection of textual file extensions.
        :return: A list with elements like "TypeName1 *ext1".
        """

        return FileTypeUtil.getTextualExtensions().split(';;')

    @staticmethod
    def getSupportedExtensions():
        """
        :return: A tuple containing all audio extensions that are supported by Speech Recognition library.
        """

        return ('.wav', '.aiff', 'aifc', '.flac')
