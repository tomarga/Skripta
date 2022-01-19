## Skripta
- Desktop aplikacija koja služi za stvaranje transkripata. 
- Ulazni zapis može biti govor koji se prenosi mikrofonom ili gotova audio datoteka. 

### Instalacija
- **Linux Ubuntu 20.04 (i noviji)**
- preuzeti [skripta.tar.gz](https://pmfhr-my.sharepoint.com/:u:/g/personal/tomarga_math_pmf_hr/EQlws3h-3O1NiMGU0Lf72M8BjdcduUZx9ZfTicK13We13g) i raspakirati datoteku na željeno mjesto
- stvoriti vlastitu ```env.json``` datoteku koja prati strukturu kao u ```env.example.json```
  - [Houndify client](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancerecognize_houndifyaudio_data-audiodata-client_id-str-client_key-str-show_all-bool--false---unionstr-dictstr-any) 
  - [Google key](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancerecognize_googleaudio_data-audiodata-key-unionstr-none--none-language-str--en-us--pfilter-union0-1-show_all-bool--false---unionstr-dictstr-any)
  - [Google Cloud credentials](https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancerecognize_google_cloudaudio_data-audiodata-credentials_json-unionstr-none--none-language-str--en-us-preferred_phrases-unioniterablestr-none--none-show_all-bool--false---unionstr-dictstr-any)
- premjestiti ```env.json``` u ranije raspakirani direktorij ```skripta```
- otvoriti direktorij ```skripta``` u terminalu i pokrenuti program 
```console
user@comp:~$  ./transkripta
```

### Pokretanje *source* koda
- klonirati projekt
- instalirati ```python 3.8.10``` (ili noviji) i ```pip```
- kreirati python virtualno okruženje (*venv*)
- instalirati pakete iz ```requirements.txt``` datoteke
- pokrenuti ```skripta/src/main.py``` skriptu
***

#### Projekt je razvijen u sklopu diplomskog rada Mogućnosti prepoznavanja govora korištenjem biblioteke SpeechRecognition pod mentorstvom prof. Gorana Igalyja.
PMF ZG, Računarstvo i matematika, 20./21.
