import mimetypes


# Utility class, containing various helper methods.
class Util:

    # For general file type (e.g. audio, image) returns the list of all possible format extensions.
    @staticmethod
    def getExtensionsForType(generalType):
        mimetypes.init()
        for extension in mimetypes.types_map:
            if mimetypes.types_map[extension].split('/')[0] == generalType:
                yield extension

    # For given list of file extensions, returns the string "(*ext1 *ext2 ... *extn)"
    @staticmethod
    def listExtensionsAsString(extensions):
        result = "("
        for extension in extensions:
            result += '*' + extension + ' '
        result = result[:-1]
        result += ')'
        return result