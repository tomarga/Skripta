import json
import socket
import sys

import speech_recognition as sr

from typing import Tuple, Union, Iterable, TextIO

from src.Model.Enums.EnergyThresholdOption import EnergyThresholdOption
from src.Model.Enums.API import API
from src.main import ROOT_DIRECTORY


class Recognizer:
    """
    A class that handles the speech recognition process, based on various options.
    """

    class MicOptions:
        """
        A helper subclass describing the basic transcription options when it comes to microphone input.
        """

        def __init__(self, mic: int, speechTimeout: int, hotwords: str = None):

            """
            Constructor method.
            :param mic: Ordinal number of the selected microphone
            :param speechTimeout: Number of seconds of speech to listen
            :param hotwords: Path to the file containing hotwords that start the listening
            """

            self.mic = mic
            self.speechTimeout = speechTimeout
            self.hotwords = hotwords

            # print(mic, speechTimeout, hotwords)

    class FileOptions:
        """
        A helper subclass describing basic properties that need to be set before starting the recognition from an audio file.
        """

        def __init__(self, file: str,  offset: int, duration: int):
            """
            Constructor method.
            :param file: Path to an audio file

            :param offset: Offset in secs
            :param duration: Duration in secs
            """

            self.file = file
            self.offset = offset
            self.duration = duration

            # print(file, offset, duration)

    class CommonOptions:
        """
        A helper subclass describing API and background noise properties that need to be set before starting the recognition,
        whatever the transcription input source.
        """

        def __init__(self, energyOption: EnergyThresholdOption, energyValue: int, api: API, language: str,
                     phrases: Union[Iterable[str], Iterable[Tuple[str, float]]], grammar: str):
            """
            Constructor method.
            :param energyOption: Energy threshold option
            :param energyValue: Energy threshold value
            :param api: An instance of API enumeration describing supported APIs.
            :param language: A language tag i.e. "en-US"
            :param phrases: Preferred phrases: list of phrases or list of (phrase, sensitivity)
            :param grammar: Path to a .gram file defining FSG or JSGF grammar
            """

            self.energyValue = energyValue
            self.energyOption = energyOption
            self.api = api
            self.language = language
            self.phrases = phrases
            self.grammar = grammar

            # print(energyOption, energyValue, api, language, phrases, grammar)

    def __init__(self, micOptions: MicOptions, fileOptions: FileOptions, commonOptions: CommonOptions):
        """
        Initializes a worker instance with given SR options.
        :param micOptions: An instance of mic-input related transcription options.
        :param fileOptions: An instance of file-input related transcription options.
        :param commonOptions: An instance of api and background noise related options class.
        """

        self.micOptions = micOptions
        self.fileOptions = fileOptions
        self.commonOptions = commonOptions

    def initRecognizer(self, source: sr.AudioSource):
        """
        Initializes a recognizer instance and setups it's properties based on mic/audio setup options.
        :type source: audio source
        :return: The new recognizer instance
        """

        recognizer = sr.Recognizer()
        recognizer.operation_timeout = 1800  # api request timeouts after half an hour

        if self.commonOptions.energyOption == EnergyThresholdOption.FIXED:
            recognizer.energy_threshold = self.commonOptions.energyValue
            recognizer.dynamic_energy_threshold = False

        if self.commonOptions.energyOption == EnergyThresholdOption.MIXED:
            recognizer.energy_threshold = self.commonOptions.energyValue

        if self.commonOptions.energyOption == EnergyThresholdOption.DYNAMIC:
            recognizer.adjust_for_ambient_noise(source, 0.75)

        return recognizer

    def getAPIResult(self, recognizer: sr.Recognizer, audio: sr.AudioData, env: TextIO):
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

            if self.commonOptions.api == API.GOOGLE:
                apiKey = jsonData["GOOGLE_API_KEY"]
                return recognizer.recognize_google(audio, apiKey, self.commonOptions.language)

            if self.commonOptions.api == API.GOOGLE_CLOUD:
                creds = json.dumps(jsonData["GOOGLE_CLOUD_CREDS"])
                return recognizer.recognize_google_cloud(audio, creds, self.commonOptions.language,
                                                         self.commonOptions.phrases)

            if self.commonOptions.api == API.HOUNDIFY:
                clientID = jsonData["HOUNDIFY_CLIENT_ID"]
                clientKey = jsonData["HOUNDIFY_CLIENT_KEY"]
                return recognizer.recognize_houndify(audio, clientID, clientKey)

            if self.commonOptions.api == API.SPHINX:
                return recognizer.recognize_sphinx(audio, self.commonOptions.language, self.commonOptions.phrases,
                                                   self.commonOptions.grammar)

    def transcribe(self, recognizer: sr.Recognizer, audio: sr.AudioData):
        """
        Fetches the API result and logs the outcome.
        :param recognizer: Recognizer instance used to make a transcription
        :param audio: Audio data to transcribe
        :return:
        """

        env = None
        try:
            env = open(ROOT_DIRECTORY.__str__() + "/env.json", 'r')
        except OSError as e:
            sys.stderr.write("OSError - env file: " + e.__str__())

        try:
            resultData = self.getAPIResult(recognizer, audio, env)
            sys.stdout.write(resultData)

        except AssertionError as e:
            sys.stderr.write("AssertionError - Transcription: " + e.__str__())

        except sr.RequestError as e:
            sys.stderr.write("RequestError - Transcription: " + e.__str__())

        except sr.UnknownValueError as e:
            sys.stderr.write("UnknownValueError - Transcription: " + e.__str__())

        except socket.timeout as e:
            sys.stderr.write("SocketTimeoutError - Transcription: " + e.__str__())

    def handleFileInput(self):
        """
        Handles file input recognition process.
        :return:
        """

        # audio and recognizer setup
        audioFile = sr.AudioFile(self.fileOptions.file)

        try:
            with audioFile as source:
                recognizer = self.initRecognizer(source)
                audio = recognizer.record(source, self.fileOptions.duration, self.fileOptions.offset)

        except ValueError as e:
            sys.stderr.write("ValueError - Audio as Source: " + e.__str__())
            return

        except FileNotFoundError as e:
            sys.stderr.write("FileNotFoundError - Audio as Source: " + e.__str__())
            return

        # transcription
        self.transcribe(recognizer, audio)

    def handleMicInput(self):
        """
        Handles microphone input recognition process.
        :return:
        """

        mic = sr.Microphone(device_index=self.micOptions.mic)

        # recognizer setup and listening
        try:
            with mic as source:
                recognizer = self.initRecognizer(source)
                recognizer.pause_threshold = 300  # stop listening after 5 mins of silence

                # trigger timeout error if no speech is detected for 5 mins
                audio = recognizer.listen(source, timeout=300, phrase_time_limit=self.micOptions.speechTimeout,
                                          snowboy_configuration=(ROOT_DIRECTORY.__str__() + '/venv/lib/python3.8/site-packages/snowboy-1.3.0-py3.8.egg/snowboy', [self.micOptions.hotwords]))

                # saving audio to file
                with open('/home/margarita/SkriptAudio/Novi.wav', 'wb') as file:
                    file.write(audio.get_wav_data())

        except sr.WaitTimeoutError as e:
            sys.stderr.write("WaitTimeoutError - listen: " + e.__str__())
            return

        except ValueError as e:
            sys.stderr.write("ValueError - Audio as Source: " + e.__str__())
            return

        except FileNotFoundError as e:
            sys.stderr.write("FileNotFoundError - Audio as Source: " + e.__str__())
            return

        # transcription
        self.transcribe(recognizer, audio)

    def run(self):
        """
        Initializes and setups the recognizer instance based on the mic/file transcription options.
        If input is set to mic, the listening process is started, resulting in an audio source file.
        If input is set to file, the file is read, also resulting in an audio source file.
        The source file is then submitted for API transcription.
        Outputs the result data to standard output channel if successful.
        Outputs the error message to standard error channel otherwise.
        :return:
        """

        # recognize mic input
        if self.micOptions is not None:
            self.handleMicInput()
        
        # recognize file input
        elif self.fileOptions is not None:
            self.handleFileInput()
