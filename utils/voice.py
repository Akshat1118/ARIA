"""
ARIA — Voice Input Utility
Uses Google's free Speech Recognition to transcribe doctor's voice into text.
No API key needed for voice — uses SpeechRecognition library.
"""

import tempfile
import os
import speech_recognition as sr


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes using Google's free Speech Recognition.

    Args:
        audio_bytes: raw audio bytes from Streamlit's audio_input

    Returns:
        Transcribed text string
    """
    # Save audio bytes to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)

        # Use Google's free speech recognition (no API key needed)
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except sr.UnknownValueError:
        return "[Could not understand the audio. Please try again.]"
    except sr.RequestError as e:
        return f"[Speech recognition error: {e}]"
    finally:
        # Clean up temp file
        os.unlink(tmp_path)
