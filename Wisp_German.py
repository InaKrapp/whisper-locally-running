import sys
import torch
import pyaudio
import wave
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QTextEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QInputDialog, QMessageBox)
from pathlib import Path
from pydub import AudioSegment
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
from lang import get_text as tx

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

        # set the window title
        self.setWindowTitle(tx("window_title"))
        self.setGeometry(100, 100, 400, 100)

        # Create a layout
        layout = QGridLayout()
        self.setLayout(layout)

        # Create a line widget: QLabel will display what is typed into QLineEdit
        self.button_record = QPushButton('Sprachaufnahme starten')
        self.button_record.clicked.connect(self.record_speech)
        self.file_record = "output"
        self.recording = True
        self.button_state = "record"
        self.recorder = Recorder(channels=2, rate=16000, frames_per_buffer=1024)
        self.recording_edit = QTextEdit()
        self.recording_edit.setText("Sprachaufnahme wurde noch nicht gestartet.")
        #self.filename_record = QLineEdit()

        # Create a button to allow the user to choose and file and display the name of the chosen file.
        file_browse = QPushButton('Datei auswählen')
        file_browse.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()

        # Set defaults
        self.accuracy = 2
        self.translation= 0

        # Create a button that allows to choose accuracy.
        accuracy_button = QPushButton('Geschwindigkeit und Genauigkeit auswählen')
        accuracy_button.clicked.connect(self.choose_accuracy)

        # Display default option at the start. Display choosen option if the user changes it.
        self.accuracy_edit = QLineEdit()
        self.accuracy_edit.setText("Mittlere Geschwindigkeit und Präzision")


        # Create a button that allows to choose if the audio should be translated
        translation_button = QPushButton('Auswählen: Soll der Text auf Englisch übersetzt werden?')
        translation_button.clicked.connect(self.choose_translation)
        # Display default option at the start. Display choosen option if the user changes it.
        self.translation_edit = QLineEdit()
        self.filepath_edit = QLineEdit()
        self.translation_edit.setText("Nein")

        # Create a button that allows the user to start the transcription process and show at the beginning that transcription has not started yet.
        self.transcription_edit = QTextEdit()
        self.transcription_edit.setText("Transkription wurde noch nicht gestartet.")
        file_transcribe = QPushButton('Transkribieren starten')

        # Display the message that the transcription process started and start the transcription process.
        file_transcribe.pressed.connect(self.transcription_message)
        file_transcribe.clicked.connect(self.transcribe)

        # Create a button that allows to close the program
        close_button = QPushButton("Programm schließen", self)
        close_button.clicked.connect(self.close)

        # Place all created buttons on the layout. 
        # Place the button and text field for recording speech:
        layout.addWidget(QLabel('Whisper wandelt gesprochene Worte in Text um.'))
        layout.addWidget(QLabel('Nimm etwas auf, was du sagst:'))
        layout.addWidget(self.button_record, 2, 0)
        layout.addWidget(self.recording_edit, 3, 0)
        # Place the file browser button and the field which shows the currently choosen file
        layout.addWidget(QLabel('Oder wähle eine Datei aus, die transkribiert werden soll:'))
        layout.addWidget(file_browse, 5, 0) 
        layout.addWidget(QLabel('Ausgewählte Datei:'), 6, 0)
        layout.addWidget(self.filename_edit, 7,0) 

        # Add the other two buttons to define accuracy and translation
        layout.addWidget(accuracy_button, 8, 0)
        layout.addWidget(self.accuracy_edit, 9, 0)
        layout.addWidget(translation_button, 10, 0)
        layout.addWidget(self.translation_edit, 11, 0)

        # Add the button to start the transcription process
        layout.addWidget(file_transcribe, 12, 0)
        layout.addWidget(self.transcription_edit, 13, 0)
        layout.addWidget(close_button, 14, 0)

        # show the windows
        self.show()

    def record_speech(self):
        "This method allows the user to record their own speech, starting and stopping a recording."
        if self.button_state == 'record':
            # Show that recording has started:
            self.recording_edit.setText("Sprachaufnahme wurde gestartet.")
            # Change filepath to the path where the recording should be stored.
            filepath = Path(resolve_path(Path(__file__).parent))
            os.chdir(filepath)
            # Select a name to store the recording under
            filename = "Sprachaufnahme.wav"
            # Check that file "Sprachaufnahme" does not exist yet. If it does, rename the new file to "Sprachaufnahme_2", "Sprachaufnahme_3" and so on.
            file =filepath.joinpath(f"{filename}")
            fileindex = 2
            while file.exists() == True:
                filename = f"Sprachaufnahme_{fileindex}.wav"
                fileindex = fileindex + 1
                file =filepath.joinpath(filename)
            # Make filename available to be displayed once the recording has finished.
            path = Path(filename)
            self.filename_edit.setText(str(path.name))
            self.filename = filename
            self.filename_path = path
            try: # Open file where to save the recording
                self.recFile = self.recorder.open(f"{filename}", 'wb')
                # Start recording
                self.recFile.start_recording()
            except OSError:
                self.recording_edit.setText("Mikrofon nicht erkannt. Bitte versuche ein anderes Mikrofon oder benutze eine andere Software für die Sprachaufnahme.")
                return
            # Change button text to 'Sprachaufnahme beenden'
            self.button_record.setText("Sprachaufnahme beenden")
            self.button_state = 'stop recording'
        else:
            # If the user presses the button again, stop recording
            filename = self.filename
            self.recFile.stop_recording()
            # Show the user that the recording has ended.
            self.recording_edit.setText(f"Sprachaufnahme wurde beendet.\n Die Aufnahme wurde unter dem Namen '{filename}' im Ordner 'Soundaufnahmen' gespeichert. \n Du kannst sie mit einem Klick auf 'Transkribieren starten' direkt in Text umwandeln, eine neue Aufnahme starten oder eine andere Datei zum transkribieren auswählen.")
            # Give the user the option to start a new recording
            self.button_record.setText("Sprachaufnahme starten")
            self.button_state = 'record'
            # Close the soundfile where the speech was recorded. Once it is closed, it is available for transcription
            self.recFile.close()
    
    def open_file_dialog(self):
        # Define where the program should look for audio files
        filepath = Path(resolve_path(Path(__file__).parent))

        # Start 'choose a file' dialog
        filenametuple = QFileDialog.getOpenFileName(
            self,
            "Wähle eine Datei aus",
           str(filepath),
            "Audio (*.wav *.mp3 *.m4a *.flac)" # Select which file type to allow.
        )
        # Change directory.
        os.chdir(filepath)

        # Get the filename the user has choosen. Display it using setText.
        filename = filenametuple[0]
        if filename:
            path = Path(filename)
            self.filename_edit.setText(str(path.name))
            self.filename = filename
            self.filename_path = path


    def choose_accuracy(self):
        "This method allows the user to choose how precise and fast the transcription should be."
        # Define options: Fast and imprecise, medium, slow and precise, very slow and very precise
        items = ["Am schnellsten, geringe Präzision", "Mittlere Geschwindigkeit und Präzision", "Langsam, hohe Präzision", "Am langsamsten, höchste Präzision"]

        # Create field to allow the user to choose
        item, ok = QInputDialog.getItem(self, "Wahl der Präzision und Geschwindigkeit", "Wie präzise soll die Übersetzung sein? Genauere Übersetzungen benötigen mehr Zeit.", items, 0, False)
        
        # Once the user gave their input, depending on user choice, set the accuracy variable and show the user what the current setting is.
        if ok and item:
            if item == "Am schnellsten, geringe Präzision":
                self.accuracy = 1
                self.accuracy_edit.setText("Einstellung: Schnell, wenig präzise")
            if item == "Mittlere Geschwindigkeit und Präzision":
                self.accuracy = 2
                self.accuracy_edit.setText("Einstellung: Mittlere Geschwindigkeit und Präzision")
            if item == "Langsam, hohe Präzision":
                self.accuracy = 3
                self.accuracy_edit.setText("Einstellung: Langsam, hohe Präzision")
            if item == "Am langsamsten, höchste Präzision":
                self.accuracy = 4
                self.accuracy_edit.setText("Einstellung: Sehr langsam, sehr hohe Präzision")
            

    def choose_translation(self):
        "This method allows the user to choose if the text should be translated to English."
        # Define options: Yes or No.
        items = ["Nein", "Ja"]

        # Create field to allow user to choose
        item, ok =  QInputDialog.getItem(self, "Soll der Text übersetzt werden?", "Textübersetzung:", items, 0, False)

        # Once the user gave their input, depending on user choice, set the translation-variable to 1 or 0 and show the user what the current setting is
        if ok and item == "Ja":
            self.translation = 1
            self.translation_edit.setText("Ja")
        if ok and item == "Nein":
            self.translation = 0
            self.translation_edit.setText("Nein")

    def transcription_message(self):
        "This method makes the message appear that the transcription started. It runs before the 'transcribe' function."
        self.transcription_edit.setText("Transkription wurde gestartet. Bitte warten...")


    def transcribe(self):
        " This function turns a m4a-file into mp3 if the supplied file is a m4a-file. It then transcribes the audio file to a txt-file."
        # Get objects from previous user inputs:
        try:
            filename = self.filename_path.name
        except AttributeError:
                self.transcription_edit.setText("Transkription kann noch nicht starten. Wähle eine Audiodatei aus oder nimm einige gesprochene Worte auf.")
                dlg = QMessageBox.warning(self,"Du hast noch keine Audiodatei ausgewählt","Du musst eine Audiodatei auswählen oder eine neue Sprachaufnahme machen, damit Whisper sie transkribieren kann.")
                if dlg:
                    return
        filetype =self.filename_path.suffix
        filename_stem = self.filename_path.stem
        filepath = self.filename_path.parent
        translation = self.translation
        accuracy = self.accuracy

        # Change directory to filepath again.
        # This is required to make sure the user can change the directory in the openfilebutton and the program will still find the file he picked.
        os.chdir(filepath)

        # if the given file is of type m4a, it gets converted to mp3.
        if filetype == '.m4a': # Import m4a file and export it as mp3
            raw_audio = AudioSegment.from_file(f"{filename}", format='m4a')
            raw_audio.export(f"{filename_stem}.mp3", format='mp3')
            filename = f"{filename_stem}.mp3"
       
        # Set up information needed to use Whisper
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        if accuracy == 1:
            model_id = "openai/whisper-tiny"
        elif accuracy == 2:
            model_id = "openai/whisper-small"
        elif accuracy == 3:
            model_id = "openai/whisper-medium"
        elif accuracy == 4:
            model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )

        filesize = Path(f'{filename}').stat().st_size
        if filesize > 0:
            # Start transcription (and translation if the user requested it)
            if translation == 1: 
                result = pipe(filename, generate_kwargs={"task": "translate"})
            else:
                result = pipe(filename)
        else: 
            self.transcription_edit.setText(f"Diese Datei enthält keinen Ton. \n Möglicherweise war das Mikrofon kaputt. \n Versuche es mit einer anderen oder fertige eine neue an.")
            return
        # Write the result to a .txt file:
        with open(f'{filename_stem}.txt', 'w') as f:
            try:
                f.write(result["text"])  # Can I show a message across several lines?
            except UnicodeEncodeError:
                dlg = QMessageBox.warning(self,"Keine Sprache erkannt","Whisper hat keine Worte erkannt. Vielleicht war das Hintergrundrauschen in der Aufnahme zu stark, oder du hast eine Aufnahme ausgewählt, in der niemand etwas gesagt hat.")
                if dlg:
                    return

        self.transcription_edit.setText(f"Transkription wurde abgeschlossen. \n Die Datei '{filename_stem}.txt' enthält den Text und kann mit einem beliebigen Texteditor (bspw. einem Office-Programm) geöffnet werden. Sie ist im selben Ordner zu finden wie die Audiodatei.")

def resolve_path(path):
    "This function navigates to 'Soundaufnahmen' folder or, if it does not exist, the 'Documents' folder to allow the user to choose an audio-file from there."
    if getattr(sys, "frozen", False):
        resolved_path = Path(os.path.abspath(os.path.join(sys._MEIPASS, path)))
        target_filepath = resolved_path.parents[3].joinpath('Documents')
        sound_targetfilepath = target_filepath.joinpath('Soundaufnahmen')
        if sound_targetfilepath.exists() and sound_targetfilepath.is_dir():
            target_filepath = sound_targetfilepath
        else: 
            os.mkdir(sound_targetfilepath)
            target_filepath = sound_targetfilepath
    else: 
        resolved_path = Path(os.path.abspath(os.path.join(os.getcwd(), path)))
        target_filepath = resolved_path.parents[1].joinpath('Documents')
        sound_targetfilepath = target_filepath.joinpath('Soundaufnahmen')
        if sound_targetfilepath.exists() and sound_targetfilepath.is_dir():
            target_filepath = sound_targetfilepath
        else:
            os.mkdir(sound_targetfilepath)
            target_filepath = sound_targetfilepath
    return target_filepath

# Check if this contains unnecessary code. Be careful not to delete anything important, though.
class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                            channels=self.channels,
                                            rate=self.rate,
                                            input=True,
                                            frames_per_buffer=self.frames_per_buffer,
                                            stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and display main window
    window = MainWindow()

    # Start the event loop
    sys.exit(app.exec())
