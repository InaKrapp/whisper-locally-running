"""
language switch module.

Provides the TEXT dictionary containing the translation
for all text elements in the GUI.
"""

import warnings
import locale

# get language setting from environment variable
LANG = "DE" if "DE" in locale.getlocale()[0].upper() else "EN"

TEXT_EN = {
    "Window_title": "Transcription software Whisper:",
    "Start_voice_recording": "Start voice recording",
    "Voice_recording_not_yet_started": "Voice recording has not yet been started.",
    "Select_a_file": "Select a file",
    "Select_speed_and_accuracy": "Select speed and accuracy",
    "Default_precision": "Fast and precise, but experimental",
    "Translation_selection":'Select: Should the text be translated into English?',
    "Default_translation": "No",
    "Transcription_not_started_yet":"Transcription has not yet been started.",
    "Start_transcription":'Start transcription',
    "Close_program": "Close program",
    "Whisper_words_to_text": "Whisper converts spoken words into text.",
    "Record_something":'Record something you say:',
    "Choose_file":'Or select a file to be transcribed:',
    'Voice_recording_started': "Voice recording has started.",
    'folder_name': '/Sound recordings',
    'file_name':"voice_recording",
    "Microphone_not_recognized": "Microphone not recognized. Please try a different microphone or use different software for voice recording.",
    "Stop_recording": "Stop voice recording",
    "Recording_message_1":"Voice recording has ended.\n The recording has been saved under the name ",
    "Recording_message_2": " in the 'Sound recordings' folder. \n You can convert it directly to text by clicking on 'Start transcription', start a new recording or select another file to transcribe.",
    "Choose_file_button":  "Choose a file",
    "Choosen_file": "Choosen file:",
    "Option_fast":"Fastest, low precision",
    "Option_medium":"Medium speed and precision",
    "Option_slow":"Slow, high precision",
    "Option_very_slow":"Slowest, highest precision",
    "Option_turbo": "Fast, precise, experimental",
    "Setting_fast":"Fast, low precision",
    "Setting_medium":"Medium speed and precision",
    "Setting_slow":"Slow, high precision",
    "Setting_very_slow":"Very slow, very high precision",
    "Setting_turbo": "Fast and precise, but experimental",
    "Transcription_setting":"Choice of precision and speed",
    "Text_transcription_setting":"How precise should the translation be? More precise translations require more time.",
    "No": "No",
    "Yes": "Yes",
    "Translation_setting":  "Should the text be translated?",
    "Diarization_setting": "Should different speakers be recognized?",
    "Transcription_started":"Transcription has started. Please wait...",
    "No_file_selected":"Transcription cannot start yet. Select an audio file or start a new voice recording.",
    "No_file_warning": "You have not selected an audio file yet",
    "No_file_text":"You must select an audio file or make a new voice recording so that Whisper can transcribe it.",
    "No_sound_found": "This file contains no sound. \n The microphone may have been broken. \n Try another one or make a new one.",
    "No_sound_warning": "No speech detected",
    "No_sound_text": "Whisper did not recognize any words. Perhaps the background noise in the recording was too strong, or you selected a recording in which nobody said anything.",
    "Transcription_message_1": "Transcription has been completed. \n The file ",
    "Transcription_message_2":" contains the text and can be opened with any text editor (e.g. an Office program). It can be found in the same folder as the audio file.",
    "Transcription_error": "Unfortunately, an error has occured: "    
}

TEXT_DE = {
    "Window_title": "Transkriptionssoftware Whisper:",
    "Start_voice_recording": "Sprachaufnahme starten",
    "Voice_recording_not_yet_started":"Sprachaufnahme wurde noch nicht gestartet.",
    "Select_a_file": "Datei auswählen",
    "Select_speed_and_accuracy": "Geschwindigkeit und Genauigkeit auswählen",
    "Default_precision": "Schnell und präzise, experimentell",
    "Translation_selection":'Auswählen: Soll der Text auf Englisch übersetzt werden?',
    "Default_translation": "Nein",
    "Transcription_not_started_yet":"Transkription wurde noch nicht gestartet.",
    "Start_transcription":'Transkribieren starten',
    "Close_program": "Programm schließen",
    "Whisper_words_to_text":'Whisper wandelt gesprochene Worte in Text um.',
    "Record_something":'Nimm etwas auf, was du sagst:',
    "Choose_file":'Oder wähle eine Datei aus, die transkribiert werden soll:',
    'Voice_recording_started': "Sprachaufnahme wurde gestartet.",
    'folder_name':'/Soundaufnahmen',
    'file_name':"Sprachaufnahme",
    "Microphone_not_recognized": "Mikrofon nicht erkannt. Bitte versuche ein anderes Mikrofon oder benutze eine andere Software für die Sprachaufnahme.",
    "Stop_recording": "Sprachaufnahme beenden",
    "Recording_message_1":"Sprachaufnahme wurde beendet.\n Die Aufnahme wurde unter dem Namen ",
    "Recording_message_2": " im Ordner 'Soundaufnahmen' gespeichert. \n Du kannst sie mit einem Klick auf 'Transkribieren starten' direkt in Text umwandeln, eine neue Aufnahme starten oder eine andere Datei zum transkribieren auswählen.",
    "Choose_file_button":  "Wähle eine Datei aus",
    "Choosen_file": "Ausgewählte Datei:",
    "Option_fast":"Am schnellsten, geringe Präzision",
    "Option_medium": "Mittlere Geschwindigkeit und Präzision",
    "Option_slow":"Langsam, hohe Präzision",
    "Option_very_slow":  "Am langsamsten, höchste Präzision",
    "Option_turbo": "Schnell und präzise, experimentell",
    "Setting_fast": "Einstellung: Schnell, wenig präzise",
    "Setting_medium":"Einstellung: Mittlere Geschwindigkeit und Präzision",
    "Setting_slow":"Einstellung: Langsam, hohe Präzision",
    "Setting_very_slow":"Einstellung: Sehr langsam, sehr hohe Präzision",
    "Setting_turbo": "Einstellung: Schnell und präzise, experimentell",
    "Transcription_setting":"Wahl der Präzision und Geschwindigkeit",
    "Text_transcription_setting":"Wie präzise soll die Übersetzung sein? Genauere Übersetzungen benötigen mehr Zeit.",
    "No": 'Nein',
    "Yes": "Ja",
    "Translation_setting": "Soll der Text direkt auf Englisch übersetzt werden?",
    "Diarization_setting": "Sollen verschiedene Sprecher erkannt werden?",
    "Transcription_started":"Transkription wurde gestartet. Bitte warten...",
    "No_file_selected":"Transkription kann noch nicht starten. Wähle eine Audiodatei aus oder nimm einige gesprochene Worte auf.",
    "No_file_warning": "Du hast noch keine Audiodatei ausgewählt",
    "No_file_text":"Du musst eine Audiodatei auswählen oder eine neue Sprachaufnahme machen, damit Whisper sie transkribieren kann.",
    "No_sound_found": "Diese Datei enthält keinen Ton. \n Möglicherweise war das Mikrofon kaputt. \n Versuche es mit einer anderen oder fertige eine neue an.",
    "No_sound_warning": "Keine Sprache erkannt",
    "No_sound_text": "Whisper hat keine Worte erkannt. Vielleicht war das Hintergrundrauschen in der Aufnahme zu stark, oder du hast eine Aufnahme ausgewählt, in der niemand etwas gesagt hat.",
    "Transcription_message_1": "Transkription wurde abgeschlossen. \n Die Datei ",
    "Transcription_message_2":" enthält den Text und kann mit einem beliebigen Texteditor (bspw. einem Office-Programm) geöffnet werden. Sie ist im selben Ordner zu finden wie die Audiodatei.",
    "Transcription_error": "Leider ist ein Fehler aufgetreten: "

}

def get_text(key: str):
    """returns a translated text element"""
    if LANG == "EN" and key in TEXT_EN:
        return TEXT_EN[key]
    if LANG == "DE" and key in TEXT_DE:
        return TEXT_DE[key]
    warnings.warn(f"missing translation for key '{key}'")
    return key
