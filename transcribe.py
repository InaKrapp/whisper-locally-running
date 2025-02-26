import torch
from pydub import AudioSegment
from faster_whisper import WhisperModel
from huggingface_hub import snapshot_download # Assuming you are using the Whisper library for transcription
import os
from lang import get_text as tx

def transcribe_audio(self):
    """
    This function turns a m4a-file into mp3 if the supplied file is a m4a-file. It then transcribes the audio file to a txt-file.
    Transcribe the given audio file and return the transcribed text:

    :param filename: Path to the audio file.
    :param translation: Boolean indicating if translation is required.
    :param accuracy: Accuracy level (1-5).
    :param device: Device to use for transcription.
    :return: Transcribed text.
    """
    # Set up information needed to use Whisper
    accuracy = self.accuracy
    if accuracy == 1:
        model_size = "tiny"
    elif accuracy == 2:
        model_size = "small"
    elif accuracy == 3:
        model_size = "medium"
    elif accuracy == 4:
        model_size = "large-v3"
    elif accuracy == 5:
        local_dir = "faster-whisper-large-v3-turbo-ct2" 
        if not os.path.exists(local_dir): # If not downloaded yet, download faster whisper turbo model.
            repo_id = "deepdml/faster-whisper-large-v3-turbo-ct2"
            snapshot_download(repo_id=repo_id, local_dir=local_dir, repo_type="model")
        model_size = "faster-whisper-large-v3-turbo-ct2"

    # Use float16 if the computer supports it
    if torch.cuda.is_available():
        model = WhisperModel(model_size, device=self.device, compute_type="float16")
    else:
        model = WhisperModel(model_size, device=self.device, compute_type="float32")

    # Convert m4a to mp3 if necessary
    filename = self.filename_path.name
    if filename.endswith(".m4a"):
        audio_segment = AudioSegment.from_file(filename)
        filename = filename.replace(".m4a", ".mp3")
        audio_segment.export(filename, format="mp3")

    # Transcribe the audio
    task = "translate" if self.translation else "transcribe"
    segments, info = model.transcribe(filename, beam_size=5, task=task)
    try:# Save the transcribed text - should I move this to the transcribe function?
        with open(f'{self.filename_path.stem}.txt', 'w', encoding="utf-8") as f:
            for segment in segments:
                f.write(segment.text)
        self.transcription_complete.emit((tx("Transcription_message_1"), self.filename_path.stem, tx("Transcription_message_2")))
    except Exception as e:
        self.error_occurred.emit(tx("Transcription_error") + str(e))
    return 