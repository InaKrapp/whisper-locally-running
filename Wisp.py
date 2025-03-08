import sys
import os
import torch
import math
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QTextEdit, QCheckBox, QLabel, QPushButton, QGridLayout, QFileDialog, QInputDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import QStandardPaths
from pathlib import Path
from lang import get_text as tx
from audio import Recorder
from transcribe import TranscriptionWorker

# This is a modified version which allows diarization.

class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the window title
        self.setWindowTitle(tx("Window_title"))
        self.setGeometry(100, 100, 400, 400)

        # Create a layout
        layout = QGridLayout()
        self.setLayout(layout)

        # Initialize widgets
        self.button_record = QPushButton(tx('Start_voice_recording'))
        self.button_record.clicked.connect(self.record_speech)
        self.file_record = "output"
        self.recording = True
        self.button_state = "record"
        self.recorder = Recorder(channels=2, rate=16000, frames_per_buffer=1024)
        self.recording_edit = QTextEdit()
        self.recording_edit.setText(tx("Voice_recording_not_yet_started"))
        self.recording_edit.setReadOnly(True)

        # Initialize progress bar:
        self.progress_bar = QProgressBar()

        # File browser button and field
        file_browse = QPushButton(tx('Select_a_file'))
        file_browse.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()
        self.filename_edit.setReadOnly(True)

        # Accuracy, translation and diarization default values:
        self.accuracy = 5
        self.translation = 0
        self.diarization = 0

        # Create a button that allows to choose accuracy.
        accuracy_button = QPushButton(tx('Select_speed_and_accuracy'))
        accuracy_button.clicked.connect(self.choose_accuracy)

        self.accuracy_edit = QLineEdit()
        self.accuracy_edit.setText(tx("Default_precision"))
        self.accuracy_edit.setReadOnly(True)
        
        # Create a checkbox that allows to choose if the audio should be translated and if speakers should be recognized
        self.translatecheckbox = QCheckBox(tx("Translation_setting"))
        self.translatecheckbox.setChecked(False)
        self.translatecheckbox.stateChanged.connect(self.choose_translation)
        self.speakercheckbox = QCheckBox(tx("Diarization_setting"))
        self.speakercheckbox.setChecked(False)
        self.speakercheckbox.stateChanged.connect(self.choose_diarization)

        # Transcription button
        self.transcription_edit = QTextEdit()
        self.transcription_edit.setText(tx("Transcription_not_started_yet"))
        self.transcription_edit.setReadOnly(True)
        self.transcription_button = QPushButton(tx('Start_transcription'))

        # Connect transcription button
        self.transcription_button.clicked.connect(self.start_transcription)
        self.transcription_button.pressed.connect(self.transcription_message)

        # Create a button that allows to close the program
        close_button = QPushButton(tx("Close_program"), self)
        close_button.clicked.connect(self.close)

        # Initialize the worker thread
        self.worker = None

        # Add widgets to the layout
        layout.addWidget(QLabel(tx("Whisper_words_to_text")), 0, 0)
        layout.addWidget(QLabel(tx("Record_something")), 1, 0)
        layout.addWidget(self.button_record, 2, 0)
        layout.addWidget(self.recording_edit, 3, 0)
        layout.addWidget(QLabel(tx("Choose_file")), 4, 0)
        layout.addWidget(file_browse, 5, 0)
        layout.addWidget(QLabel(tx("Choosen_file")), 6, 0)
        layout.addWidget(self.filename_edit, 7, 0)
        
        # Add the other two buttons to define accuracy and translation
        layout.addWidget(accuracy_button, 8, 0)
        layout.addWidget(self.accuracy_edit, 9, 0)
        layout.addWidget(self.speakercheckbox, 10, 0)
        layout.addWidget(self.translatecheckbox, 11, 0)

        # Add the button to start the transcription process
        layout.addWidget(self.transcription_button, 12, 0)
        layout.addWidget(self.transcription_edit, 13, 0)

        # Add the progress bar:
        layout.addWidget(self.progress_bar, 14, 0)

        # Add the button to close the program
        layout.addWidget(close_button, 15, 0)

        # Show the window
        self.show()

    def record_speech(self):
        # Existing code remains unchanged
        if self.button_state == 'record':
            self.recording_edit.setText(tx('Voice_recording_started'))
            filepath = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            if not os.path.exists(filepath + tx("folder_name")):
                os.mkdir(filepath + tx("folder_name"))
            filepath = filepath + tx("folder_name")
            os.chdir(filepath)
            filename = tx("file_name") + ".wav"
            file = Path(f"{filename}")
            fileindex = 2
            while file.exists():
                filename = f"{tx('file_name')}_{fileindex}.wav"
                fileindex += 1
                file = Path(f"{filename}")
            path = Path(filename)
            self.filename_edit.setText(str(path.name))
            self.filename_path = path

            try:
                self.recFile = self.recorder.open(f"{filename}", 'wb')
                self.recFile.start_recording()
            except OSError:
                self.recording_edit.setText(tx("Microphone_not_recognized"))
                return

            self.button_record.setText(tx("Stop_recording"))
            self.button_state = 'stop recording'
        else:
            self.recFile.stop_recording()
            self.recording_edit.setText(f"{tx('Recording_message_1')}'{self.filename_path.name}'{tx('Recording_message_2')}")
            self.button_record.setText(tx("Start_voice_recording"))
            self.button_state = 'record'
            self.recFile.close()

    def open_file_dialog(self):
        # Existing code remains unchanged
        filepath = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        if not os.path.exists(filepath + tx("folder_name")):
            os.mkdir(filepath + tx("folder_name"))
        filepath = filepath + tx("folder_name")
        os.chdir(filepath)

        filenametuple = QFileDialog.getOpenFileName(
            self,
            tx("Choose_file"),
            str(filepath), # Check - Whisper should be able to use mp4 automatically.
            "Audio (*.wav *.mp3 *.m4a *.flac *.mp4)"
        )

        filename = filenametuple[0]
        if filename:
            path = Path(filename)
            self.filename_edit.setText(str(path.name))
            self.filename_path = path

    def choose_accuracy(self):
        # Existing code remains unchanged
        items = [tx("Option_fast"), tx("Option_medium"), tx("Option_slow"), tx("Option_very_slow"), tx("Option_turbo")]
        item, ok = QInputDialog.getItem(self, tx("Transcription_setting"), tx("Text_transcription_setting"), items, 0, False)
        if ok and item:
            if item == tx("Option_fast"):
                self.accuracy = 1
                self.accuracy_edit.setText(tx("Setting_fast"))
            elif item == tx("Option_medium"):
                self.accuracy = 2
                self.accuracy_edit.setText(tx("Setting_medium"))
            elif item == tx("Option_slow"):
                self.accuracy = 3
                self.accuracy_edit.setText(tx("Setting_slow"))
            elif item == tx("Option_very_slow"):
                self.accuracy = 4
                self.accuracy_edit.setText(tx("Setting_very_slow"))
            elif item == tx("Option_turbo"):
                self.accuracy = 5
                self.accuracy_edit.setText(tx("Setting_turbo"))

    def choose_translation(self, state):
        """Select if text should be translated to english. Default is state 0, means no translation to english."""
        if state == 0:
            self.translation = 0
        else:
            self.translation = 1
    
    def choose_diarization(self, state):
        """Select if speakers should be recognized. Default is state 0, means no speaker recognition."""
        if state == 0:
            self.diarization = 0
        else:
            self.diarization = 1

    def transcription_message(self):
        """ A message to be displayed once the transcription started, to show the user that the program works as intended."""
        self.transcription_edit.setText(tx("Transcription_started"))

    def start_transcription(self):
        if self.transcription_button.text() == tx('Start_transcription'):
            # Disable the button to prevent multiple clicks
            self.transcription_button.setEnabled(False)
            self.transcription_message()
            # Start the worker thread for transcription
            self._start_transcription_worker()
        else:
            # If the user wants to stop the transcription, implement if needed
            pass

    def _start_transcription_worker(self):
        # Create a new worker thread for the transcription
        self.worker = TranscriptionWorker(self.filename_path, self.translation, self.diarization, self.accuracy, "cuda:0" if torch.cuda.is_available() else "cpu")
        # Give the progressbar the length of the whole audio:
        self.worker.initialize_progressbar.connect(self._initialize_progressbar)
        # Tell the progressbar to which length the audio is already transcribed:
        self.worker.update_progressbar.connect(self._update_progressbar)
        # Send a message to the user if the transcription is finished.
        self.worker.transcription_complete.connect(self._update_transcription_result)
        # Send another message to the user if some error occured.
        self.worker.error_occurred.connect(self._handle_transcription_error)
        # Modify the user interface so the user can start the next transcription
        self.worker.finished.connect(self._transcription_finished)
        self.worker.start()

    def _initialize_progressbar(self, total):
        self.progress_bar.setRange(0, round(total))
    
    def _update_progressbar(self, segment_end):
        print("Segment end:", segment_end)
        self.progress_bar.setValue(math.ceil(segment_end))

    def _update_transcription_result(self, message_parts):
        message_1, file_stem, message_2 = message_parts
        self.transcription_edit.setText(f"{message_1}'{file_stem}.txt'{message_2}")

    def _handle_transcription_error(self, error_message):
        self.transcription_edit.setText(f"{error_message}")

    def _transcription_finished(self):
        # Enable the transcription button again
        self.transcription_button.setEnabled(True)
        # You can reset the button text or perform other cleanup actions here
        self.transcription_button.setText(tx('Start_transcription'))

def main():
    app = QApplication(sys.argv)
    # Increase font size
    app.setStyleSheet('* { font-size: 12pt;}')
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()