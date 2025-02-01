import sys
import os
import torch
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QTextEdit, QLabel, QPushButton, QGridLayout, QFileDialog, QInputDialog, QMessageBox)
from PyQt6.QtCore import QStandardPaths, QThread, pyqtSignal
from pathlib import Path
from lang import get_text as tx
from audio import Recorder
from transcribe import transcribe_audio

class TranscriptionWorker(QThread):
    transcription_complete = pyqtSignal(tuple)
    error_occurred = pyqtSignal(str)

    def __init__(self, filename_path, translation, accuracy, device):
        super().__init__()
        self.filename_path = filename_path
        self.translation = translation
        self.accuracy = accuracy
        self.device = device

    def run(self):
        try:
            if not self.filename_path:
                raise Exception(tx("No_file_selected"))

            # Set the current working directory to where the file is located
            os.chdir(self.filename_path.parent)
            filename = self.filename_path.name

            # Check if the file exists and is not empty
            if not os.path.exists(filename):
                raise Exception(tx("File_not_found"))

            filesize = Path(filename).stat().st_size
            if filesize == 0:
                self.error_occurred.emit(tx("No_sound_found"))
                return

            # Perform the transcription
            transcribed_text = transcribe_audio(filename, self.translation, self.accuracy, self.device)

            # Save the transcribed text
            try:
                with open(f'{self.filename_path.stem}.txt', 'w') as f:
                    f.write(transcribed_text)
                self.transcription_complete.emit((tx("Transcription_message_1"), self.filename_path.stem, tx("Transcription_message_2")))
            except Exception as e:
                self.error_occurred.emit(tx("File_operation_error") + str(e))
        except ValueError as e:
            self.error_occurred.emit(tx("No_sound_text"))
        except Exception as e:
            self.error_occurred.emit(tx("Transcription_error") + str(e))
            #pass

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

        # File browser button and field
        file_browse = QPushButton(tx('Select_a_file'))
        file_browse.clicked.connect(self.open_file_dialog)
        self.filename_edit = QLineEdit()
        self.filename_edit.setReadOnly(True)

        # Accuracy and Translation
        self.accuracy = 5
        self.translation = 0

        # Create a button that allows to choose accuracy.
        accuracy_button = QPushButton(tx('Select_speed_and_accuracy'))
        accuracy_button.clicked.connect(self.choose_accuracy)

        self.accuracy_edit = QLineEdit()
        self.accuracy_edit.setText(tx("Default_precision"))
        self.accuracy_edit.setReadOnly(True)
        
        # Create a button that allows to choose if the audio should be translated
        translation_button = QPushButton(tx("Translation_selection"))
        translation_button.clicked.connect(self.choose_translation)
        self.translation_edit = QLineEdit()
        self.translation_edit.setText(tx("Default_translation"))
        self.translation_edit.setReadOnly(True)

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
        layout.addWidget(translation_button, 10, 0)
        layout.addWidget(self.translation_edit, 11, 0)

        # Add the button to start the transcription process
        layout.addWidget(self.transcription_button, 12, 0)
        layout.addWidget(self.transcription_edit, 13, 0)
        layout.addWidget(close_button, 14, 0)


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
            str(filepath),
            "Audio (*.wav *.mp3 *.m4a *.flac)"
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

    def choose_translation(self):
        # Existing code remains unchanged
        items = [tx("No"), tx("Yes")]
        item, ok = QInputDialog.getItem(self, tx("Translation_setting"), tx("Text_Translation_setting"), items, 0, False)
        if ok and item:
            if item == tx("Yes"):
                self.translation = 1
                self.translation_edit.setText(tx("Yes"))
            else:
                self.translation = 0
                self.translation_edit.setText(tx("No"))

    def transcription_message(self):
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
        self.worker = TranscriptionWorker(self.filename_path, self.translation, self.accuracy, "cuda:0" if torch.cuda.is_available() else "cpu")
        self.worker.transcription_complete.connect(self._update_transcription_result)
        self.worker.error_occurred.connect(self._handle_transcription_error)
        self.worker.finished.connect(self._transcription_finished)
        self.worker.start()

    def _update_transcription_result(self, message_parts):
        message_1, file_stem, message_2 = message_parts
        self.transcription_edit.setText(f"{message_1}'{file_stem}.txt'{message_2}")

    def _handle_transcription_error(self, error_message):
        #self.transcription_edit.setText(f"{tx('Transcription_error')}{error_message}")
        self.transcription_edit.setText(f"{error_message}")

    def _transcription_finished(self):
        # Enable the transcription button again
        self.transcription_button.setEnabled(True)
        # You can reset the button text or perform other cleanup actions here
        self.transcription_button.setText(tx('Start_transcription'))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()