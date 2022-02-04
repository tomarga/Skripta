import argparse

from skripta.src.Model.Enums.EnergyThresholdOption import EnergyThresholdOption
from skripta.src.Model.Enums.API import API
from skripta.src.Model.Workers.Recognizer import Recognizer


def setupParser():
    """
    Setups parser for command line arguments.
    :return: Parser instance with defined arguments.
    """

    newParser = argparse.ArgumentParser()

    # input type
    newParser.add_argument("-i", "--input", type=str, help="the input type, should be 'file' or 'mic")

    # file options
    newParser.add_argument("-f", "--file", type=str, help="the audio file path")
    newParser.add_argument("-o", "--offset", type=int, help="offset of audio file in secs")
    newParser.add_argument("-d", "--duration", type=int, help="duration of audio file in secs")

    # mic options
    newParser.add_argument("-m", "--mic", type=int, help="ordinal number of the microphone input")
    newParser.add_argument("-st", "--speech_timeout", type=int, help="number of seconds of speech to listen")
    newParser.add_argument("-hw", "--hotwords", type=str, help="path to the hotwords file")

    # common options
    newParser.add_argument("-e", "--energy", type=lambda energy: EnergyThresholdOption[energy.upper()],
                           help="one of the tree energy threshold options", choices=list(EnergyThresholdOption),
                           default=EnergyThresholdOption.DYNAMIC)

    newParser.add_argument("-sv", "--start_value", type=int, help="starter value for non-dynamic threshold options")

    # api-specific options
    newParser.add_argument("-a", "--api", type=lambda api: API[api.upper()], help="one of the 4 supported APIs",
                           choices=list(API), default=API.GOOGLE)

    newParser.add_argument("-l", "--language", type=str, help="language in the audio file", default="en-US")
    newParser.add_argument("-p", "--phrases", nargs="*", type=str, help="preferred phrases")
    newParser.add_argument("-pv", "--phrases_values", nargs="*", type=float, help="sensitivity values of preferred phrases")
    newParser.add_argument("-g", "--grammar", type=str, help=".gram file path")

    return newParser


def getTranscriptionOptions():
    """
    Creates the instance of MicOptions, FileOptions and CommonOptions based on the command line inputs.
    :return: Tuple (mic_options, file_options, common_options)
    """

    micOptions = fileOptions = None

    # file options
    if args.input == 'file':
        fileOptions = Recognizer.FileOptions(args.file, args.offset, args.duration)

    # mic options
    elif args.input == 'mic':
        micOptions = Recognizer.MicOptions(args.mic, args.speech_timeout, args.hotwords)

    # common options
    phrases = args.phrases
    if args.phrases_values:
        for index, phrase in enumerate(args.phrases):
            # values are 'inverted' because of the sphinx package implementation
            phrases[index] = (phrase, 1 - args.phrases_values[index])

    commonOptions = Recognizer.CommonOptions(args.energy, args.start_value, args.api, args.language, phrases, args.grammar)

    return (micOptions, fileOptions, commonOptions)


if __name__ == '__main__':
    """
    Runs the transcription of the file whose path is given as command line input.
    The results are printed to standard (error) output channels.
    """

    parser = setupParser()
    args = parser.parse_args()

    options = getTranscriptionOptions()
    worker = Recognizer(*options)
    worker.run()
