import argparse

from EnergyThresholdOption import EnergyThresholdOption
from API import API
from Recognizer import Recognizer


def setupParser():
    """
    Setups parser for command line arguments.
    :return: Parser instance with defined arguments.
    """

    newParser = argparse.ArgumentParser()

    # file
    newParser.add_argument("file", type=str, help="the audio file path")

    # basic options
    newParser.add_argument("-e", "--energy", type=lambda energy: EnergyThresholdOption[energy.upper()],
                           help="one of the tree energy threshold options", choices=list(EnergyThresholdOption),
                           default=EnergyThresholdOption.DYNAMIC)

    newParser.add_argument("-sv", "--start_value", type=int, help="starter value for non-dynamic threshold options")
    newParser.add_argument("-o", "--offset", type=int, help="offset of audio file in secs")
    newParser.add_argument("-d", "--duration", type=int, help="duration of audio file in secs")

    # api-specific options
    newParser.add_argument("-a", "--api", type=lambda api: API[api.upper()], help="one of the 4 supported APIs",
                           choices=list(API), default=API.GOOGLE)

    newParser.add_argument("-l", "--language", type=str, help="language in the audio file", default="en-US")
    newParser.add_argument("-p", "--phrases", nargs="*", type=str, help="preferred phrases")
    newParser.add_argument("-pv", "--phrases_values", nargs="*", type=float, help="sensitivity values of preferred phrases")
    newParser.add_argument("-g", "--grammar", type=str, help=".gram file path")

    return newParser


if __name__ == '__main__':
    """
    Runs the transcription of the file whose path is given as command line input.
    The results are printed to standard (error) output channels.
    """

    parser = setupParser()
    args = parser.parse_args()

    phrases = args.phrases
    if args.phrases_values:
        for index, phrase in enumerate(args.phrases):
            phrases[index] = (phrase, args.phrases_values[index])

    file = args.file
    basicOptions = Recognizer.BasicOptions(args.energy, args.start_value, args.offset, args.duration)
    apiOptions = Recognizer.APIOptions(args.api, args.language, phrases, args.grammar)

    worker = Recognizer(file, basicOptions, apiOptions)
    worker.run()
