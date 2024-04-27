"""
language switch module.

Provides the TEXT dictionary containing the translation
for all text elements in the GUI.
"""
import os
import warnings


# get language setting from environment variable
LANG = os.getenv("LANG").upper() or "EN"
LANG = "EN" if "EN" in LANG else "DE"

TEXT_EN = {
    "window_title": "Transcription software Whisper:",
}

TEXT_DE = {
    "window_title": "Transkriptionssoftware Whisper:",
}

def get_text(key: str):
    """returns a translated text element"""
    if LANG == "EN" and key in TEXT_EN:
        return TEXT_EN[key]
    if LANG == "DE" and key in TEXT_DE:
        return TEXT_DE[key]
    warnings.warn(f"missing translation for key '{key}'")
    return key
