import sys

import speech_recognition as sr


def run(filePath: str):
    """
    Initializes a recognizer instance and runs the transcription of the file whose path is given as an argument.
    Outputs the result data to standard output channel if successful.
    Outputs the error message to standard error channel otherwise.
    :param filePath: Path to an audio file.
    :return:
    """

    recognizer = sr.Recognizer()
    audioFile = sr.AudioFile(filePath)

    try:
        with audioFile as source:
            audio = recognizer.record(source)
    except ValueError as e:
        sys.stderr.write("ValueError - Audio as Source: " + e.__str__())
        return

    try:
        resultData = recognizer.recognize_google(audio)
        sys.stdout.write(resultData)

    except sr.RequestError as e:
        sys.stderr.write("RequestError - Transcription" + e.__str__())

    except sr.UnknownValueError as e:
        sys.stderr.write("UnknownValueError - Transcription" + e.__str__())


if __name__ == '__main__':
    """
    Runs the transcription of the file whose path is given as command line input.
    The results are printed to standard (error) output channels.
    """

    audioFilePath = sys.argv[1]

    if audioFilePath:
        run(audioFilePath)
