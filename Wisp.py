import sys
import torch
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QTextEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import QStandardPaths
from pathlib import Path
from pydub import AudioSegment
from faster_whisper import WhisperModel
import os
from lang import get_text as tx
from audio import Recorder

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

        # set the window title
        self.setWindowTitle(tx("Window_title"))
        self.setGeometry(100, 100, 400, 100)

        # Create a layout
        layout = QGridLayout()
        self.setLayout(layout)

        # Create a line widget: QLabel will display what is typed into QLineEdit
        self.button_record = QPushButton(tx('Start_voice_recording'))
        self.button_record.clicked.connect(self.record_speech)
        self.file_record = "output"
        self.recording = True
        self.button_state = "record"
        self.recorder = Recorder(channels=2, rate=16000, frames_per_buffer=1024)
        self.recording_edit = QTextEdit()
        self.recording_edit.setText(tx("Voice_recording_not_yet_started"))
        #self.filename_record = QLineEdit()

        # Create a button to allow the user to choose and file and display the name of the chosen file.
        file_browse = QPushButton(tx('Select_a_file'))
        file_browse.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()

        # Set defaults
        self.accuracy = 2
        self.translation= 0

        # Create a button that allows to choose accuracy.
        accuracy_button = QPushButton(tx('Select_speed_and_accuracy'))
        accuracy_button.clicked.connect(self.choose_accuracy)

        # Display default option at the start. Display choosen option if the user changes it.
        self.accuracy_edit = QLineEdit()
        self.accuracy_edit.setText(tx("Default_precision"))


        # Create a button that allows to choose if the audio should be translated
        translation_button = QPushButton(tx("Translation_selection"))
        translation_button.clicked.connect(self.choose_translation)
        # Display default option at the start. Display choosen option if the user changes it.
        self.translation_edit = QLineEdit()
        self.filepath_edit = QLineEdit()
        self.translation_edit.setText(tx("Default_translation"))

        # Create a button that allows the user to start the transcription process and show at the beginning that transcription has not started yet.
        self.transcription_edit = QTextEdit()
        self.transcription_edit.setText(tx("Transcription_not_started_yet"))
        file_transcribe = QPushButton(tx('Start_transcription'))

        # Display the message that the transcription process started and start the transcription process.
        file_transcribe.pressed.connect(self.transcription_message)
        file_transcribe.clicked.connect(self.transcribe)

        # Create a button that allows to close the program
        close_button = QPushButton(tx("Close_program"), self)
        close_button.clicked.connect(self.close)

        # Place all created buttons on the layout. 
        # Place the button and text field for recording speech:
        layout.addWidget(QLabel(tx("Whisper_words_to_text")))
        layout.addWidget(QLabel(tx("Record_something")))
        layout.addWidget(self.button_record, 2, 0)
        layout.addWidget(self.recording_edit, 3, 0)
        # Place the file browser button and the field which shows the currently choosen file
        layout.addWidget(QLabel(tx("Choose_file")), 4, 0)
        layout.addWidget(file_browse, 5, 0) 
        layout.addWidget(QLabel(tx("Choosen_file")), 6, 0)
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
            self.recording_edit.setText(tx('Voice_recording_started'))
            # Change filepath to the path where the recording should be stored.
            filepath = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            if not os.path.exists(filepath + tx("folder_name")):
                os.mkdir(filepath + tx("folder_name"))
            filepath = filepath + tx("folder_name")
            os.chdir(filepath)
            # Select a name to store the recording under
            fileword = tx("file_name")
            filename = fileword+".wav"
            # Check that file "Sprachaufnahme" does not exist yet. If it does, rename the new file to "Sprachaufnahme_2", "Sprachaufnahme_3" and so on.
            file = Path(f"{filename}")
            fileindex = 2
            while file.exists() == True:
                filename = f"{fileword}_{fileindex}.wav"
                fileindex = fileindex + 1
                file = Path(f"{filename}")
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
                self.recording_edit.setText(tx("Microphone_not_recognized"))
                return
            # Change button text to 'Sprachaufnahme beenden'
            self.button_record.setText(tx("Stop_recording"))
            self.button_state = 'stop recording'
        else:
            # If the user presses the button again, stop recording
            filename = self.filename
            self.recFile.stop_recording()
            # Show the user that the recording has ended.
            self.recording_edit.setText(f"{tx('Recording_message_1')}'{filename}'{tx('Recording_message_2')}")
            # Give the user the option to start a new recording
            self.button_record.setText(tx("Start_voice_recording"))
            self.button_state = 'record'
            # Close the soundfile where the speech was recorded. Once it is closed, it is available for transcription
            self.recFile.close()
    
    def open_file_dialog(self):
        # Define where the program should look for audio files
        filepath = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        if not os.path.exists(filepath + tx("folder_name")):
            os.mkdir(filepath + tx("folder_name"))
        filepath = filepath + tx("folder_name")
        os.chdir(filepath)

        # Start 'choose a file' dialog
        filenametuple = QFileDialog.getOpenFileName(
            self,
            tx("Choose_file"),
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
        items = [tx("Option_fast"), tx("Option_medium"), tx("Option_slow"), tx("Option_very_slow")]

        # Create field to allow the user to choose
        item, ok = QInputDialog.getItem(self,  tx("Transcription_setting"), tx("Text_transcription_setting"), items, 0, False)
        
        # Once the user gave their input, depending on user choice, set the accuracy variable and show the user what the current setting is.
        if ok and item:
            if item == tx("Option_fast"):
                self.accuracy = 1
                self.accuracy_edit.setText(tx("Setting_fast"))
            if item == tx("Option_medium"):
                self.accuracy = 2
                self.accuracy_edit.setText(tx("Setting_medium"))
            if item == tx("Option_slow"):
                self.accuracy = 3
                self.accuracy_edit.setText(tx("Setting_slow"))
            if item == tx("Option_very_slow"):
                self.accuracy = 4
                self.accuracy_edit.setText(tx("Setting_very_slow"))
            

    def choose_translation(self):
        "This method allows the user to choose if the text should be translated to English."
        # Define options: Yes or No.
        items = [tx("No"), tx("Yes")]

        # Create field to allow user to choose
        item, ok =  QInputDialog.getItem(self, tx("Translation_setting"), tx("Text_Translation_setting"), items, 0, False)

        # Once the user gave their input, depending on user choice, set the translation-variable to 1 or 0 and show the user what the current setting is
        if ok and item == tx("Yes"):
            self.translation = 1
            self.translation_edit.setText(tx("Yes"))
        if ok and item == tx("No"):
            self.translation = 0
            self.translation_edit.setText(tx("No"))

    def transcription_message(self):
        "This method makes the message appear that the transcription started. It runs before the 'transcribe' function."
        self.transcription_edit.setText(tx("Transcription_started"))


    def transcribe(self):
        " This function turns a m4a-file into mp3 if the supplied file is a m4a-file. It then transcribes the audio file to a txt-file."
        # Get objects from previous user inputs:
        try:
            filename = self.filename_path.name
        except AttributeError:
                self.transcription_edit.setText(tx("No_file_selected"))
                dlg = QMessageBox.warning(self,tx("No_file_warning"),tx("No_file_text"))
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
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        # Set up information needed to use Whisper

        # If no translation is requested, use fasterWhisper
        if accuracy == 1:
            model_size = "tiny"
        elif accuracy == 2:
            model_size = "small"
        elif accuracy == 3:
            model_size = "medium"
        elif accuracy == 4:
            model_size = "large-v3"

        # Use float16 if the computer supports it
        if torch.cuda.is_available():
            model = WhisperModel(model_size, device=device, compute_type="float16")
        else:
            model = WhisperModel(model_size, device=device, compute_type="float32")


        filesize = Path(f'{filename}').stat().st_size
        if filesize > 0:
            if translation == 1:
                segments, info = model.transcribe(filename, beam_size=5, task="translate") # What does a change in beam size do?
            else:
                segments, info = model.transcribe(filename, beam_size=5)
            # Creates a new file where the transcription will be stored:
            f = open(f'{filename_stem}.txt', 'w')
            f.close()

            #print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            try:
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

                    with open(f'{filename_stem}.txt', 'a') as f:
                        f.write(segment.text)  # Can I show a message across several lines?
            except UnicodeEncodeError:
                dlg = QMessageBox.warning(self,tx("No_sound_warning"),tx("No_sound_text"))
                if dlg:
                    return

        else: 
            self.transcription_edit.setText(tx("No_sound_found"))
            return

        self.transcription_edit.setText(f"{tx('Transcription_message_1')}'{filename_stem}.txt' {tx('Transcription_message_2')}")



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and display main window
    window = MainWindow()

    # Start the event loop
    sys.exit(app.exec())
