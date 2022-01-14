import json
import socket
import sys

import speech_recognition as sr

from typing import Tuple, Union, Iterable, TextIO

from src.Model.Enums.EnergyThresholdOption import EnergyThresholdOption
from src.Model.Enums.API import API


class Recognizer:
    """
    A class that handles the speech recognition process, based on various options.
    """

    class BasicOptions:
        """
        A helper subclass describing basic properties that need to be set before starting the recognition.
        """

        def __init__(self, energyOption: EnergyThresholdOption, energyValue: int, offset: int, duration: int):
            """
            Constructor method.
            :param energyOption: Energy threshold option
            :param energyValue: Energy threshold value
            :param offset: Offset in secs
            :param duration: Duration in secs
            """

            self.energyOption = energyOption
            self.energyValue = energyValue
            self.offset = offset
            self.duration = duration

            # print(energyOption, energyValue, offset, duration)

    class APIOptions:
        """
        A helper subclass describing API properties that need to be set before starting the recognition.
        """

        def __init__(self, api: API, language: str, phrases: Union[Iterable[str], Iterable[Tuple[str, float]]], grammar: str):
            """
            Constructor method.
            :param api: An instance of API enumeration describing supported APIs.
            :param language: A language tag i.e. "en-US"
            :param phrases: Preferred phrases: list of phrases or list of (phrase, sensitivity)
            :param grammar: Path to a .gram file defining FSG or JSGF grammar
            """

            self.api = api
            self.language = language
            self.phrases = phrases
            self.grammar = grammar

            # print(api, language, phrases, grammar)

    def __init__(self, file: str, basicOptions: BasicOptions, apiOptions: APIOptions):
        """
        Initializes a worker instance with given SR options.
        :param file: A path to audio file to transcribe.
        :param basicOptions: An instance of non-api related transcription options.
        :param apiOptions: An instance of api options class.
        """

        self.file = file
        self.basicOptions = basicOptions
        self.apiOptions = apiOptions

    def calibrateThreshold(self, recognizer: sr.Recognizer, source: sr.AudioSource):
        """
        Sets the recognizer's properties regarding the ambient noise, based on the basicOption's energy property.
        The 'fixed' option sets the threshold to the specified value and disables the dynamic adjustment.
        The 'mixed' options sets the 'starter' threshold to the specified value.
        The 'dynamic' option sets the 'starter' threshold based on the first sec of the audio source.
        :param recognizer:
        :param source:
        :return:
        """

        if self.basicOptions.energyOption == EnergyThresholdOption.FIXED:
            recognizer.energy_threshold = self.basicOptions.energyValue
            recognizer.dynamic_energy_threshold = False

        if self.basicOptions.energyOption == EnergyThresholdOption.MIXED:
            recognizer.energy_threshold = self.basicOptions.energyValue

        if self.basicOptions.energyOption == EnergyThresholdOption.DYNAMIC:
            recognizer.adjust_for_ambient_noise(source, 0.75)

    def run(self):
        """
        Initializes a recognizer instance and runs the transcription of the file, with options set in the constructor.
        Outputs the result data to standard output channel if successful.
        Outputs the error message to standard error channel otherwise.
        :return:
        """

        audioFile = sr.AudioFile(self.file)

        recognizer = sr.Recognizer()
        recognizer.operation_timeout = 1800  # timeout after half an hour

        try:
            with audioFile as source:
                self.calibrateThreshold(recognizer, source)

                audio = recognizer.record(source, self.basicOptions.duration, self.basicOptions.offset)

        except ValueError as e:
            sys.stderr.write("ValueError - Audio as Source: " + e.__str__())
            return

        except FileNotFoundError as e:
            sys.stderr.write("FileNotFoundError - Audio as Source: " + e.__str__())
            return

        env = None
        try:
            from src.main import ROOT_DIRECTORY
            env = open(ROOT_DIRECTORY.__str__() + "/env.json", 'r')
        except OSError as e:
            sys.stderr.write("OSError - env file: " + e.__str__())

        try:
            resultData = self.getResult(recognizer, audio, env)
            sys.stdout.write(resultData)

        except AssertionError as e:
            sys.stderr.write("AssertionError - Transcription: " + e.__str__())

        except sr.RequestError as e:
            sys.stderr.write("RequestError - Transcription: " + e.__str__())

        except sr.UnknownValueError as e:
            sys.stderr.write("UnknownValueError - Transcription: " + e.__str__())

        except socket.timeout as e:
            sys.stderr.write("SocketTimeoutError - Transcription: " + e.__str__())

    def getResult(self, recognizer: sr.Recognizer, audio: sr.AudioData, env: TextIO):
        """
        Makes an API request and returns the result.
        :param recognizer: A recognizer instance
        :param audio: A audio data instance
        :param env: An IO Stream containing environmental variables
        :return: The result text
        @:raises:
            RequestError: if the env key is invalid, there are internet connection issues or if the Sphinx was not installed properly
            UnknownValueError: if the speech recognition process failed due to speech being unintelligible
            AssertionError: if the api request arguments are not of expected type
            socket.timeout: if the request takes more than half an hour to retrieve result
        """

        with env:
            jsonData = json.load(env)

            if self.apiOptions.api == API.GOOGLE:
                apiKey = jsonData["GOOGLE_API_KEY"]
                return recognizer.recognize_google(audio, apiKey, self.apiOptions.language)

            if self.apiOptions.api == API.GOOGLE_CLOUD:
                creds = json.dumps(jsonData["GOOGLE_CLOUD_CREDS"])
                return recognizer.recognize_google_cloud(audio, creds, self.apiOptions.language, self.apiOptions.phrases)

            if self.apiOptions.api == API.HOUNDIFY:
                clientID = jsonData["HOUNDIFY_CLIENT_ID"]
                clientKey = jsonData["HOUNDIFY_CLIENT_KEY"]
                return recognizer.recognize_houndify(audio, clientID, clientKey)

            if self.apiOptions.api == API.SPHINX:
                return recognizer.recognize_sphinx(audio, self.apiOptions.language, self.apiOptions.phrases, self.apiOptions.grammar)
