"""
ARIA — Sarvam AI Multilingual Translation Module
Translates patient-facing content into Hindi (and other Indian languages).
Uses Sarvam AI's Mayura translation model.
"""

import os
import requests

SARVAM_API_URL = "https://api.sarvam.ai/translate"
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")

SUPPORTED_LANGUAGES = {
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Bengali": "bn-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Punjabi": "pa-IN",
}


def translate_text(text, target_language="hi-IN", source_language="en-IN"):
    """
    Translate text using Sarvam AI Mayura model.
    
    Args:
        text: English text to translate
        target_language: Target language code (e.g., 'hi-IN' for Hindi)
        source_language: Source language code (default: 'en-IN')
    
    Returns:
        Translated text string, or original text if translation fails.
    """
    if not SARVAM_API_KEY:
        return text  # Graceful fallback
    
    if not text or len(text.strip()) < 2:
        return text

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    # Sarvam API has a character limit per request — split if needed
    MAX_CHARS = 900
    if len(text) <= MAX_CHARS:
        chunks = [text]
    else:
        # Split by sentences
        sentences = text.replace('. ', '.|').replace('? ', '?|').replace('! ', '!|').split('|')
        chunks = []
        current = ""
        for s in sentences:
            if len(current) + len(s) < MAX_CHARS:
                current += s + " "
            else:
                if current: chunks.append(current.strip())
                current = s + " "
        if current: chunks.append(current.strip())

    translated_parts = []
    for chunk in chunks:
        try:
            payload = {
                "input": chunk,
                "source_language_code": source_language,
                "target_language_code": target_language,
                "speaker_gender": "Male",
                "mode": "formal",
                "model": "mayura:v1",
                "enable_preprocessing": True
            }
            resp = requests.post(SARVAM_API_URL, json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                translated_parts.append(data.get("translated_text", chunk))
            else:
                translated_parts.append(chunk)  # Fallback to original
        except Exception:
            translated_parts.append(chunk)  # Fallback to original

    return " ".join(translated_parts)


def translate_patient_report(patient_data, results, target_language="hi-IN"):
    """
    Translate all patient-facing content for the report.
    Returns a dict of translated strings.
    """
    from report_gen import _get_kb

    diagnosis = str(results.get('diagnosis', {}).get('diagnosis', 'Unknown'))
    kb = _get_kb(diagnosis)

    translated = {}

    # Translate patient summary
    translated['patient_summary'] = translate_text(kb.get('patient_summary', ''), target_language)

    # Translate "what to expect" items
    translated['what_to_expect'] = [
        translate_text(item, target_language) for item in kb.get('what_to_expect', [])
    ]

    # Translate red flags
    translated['red_flags'] = [
        translate_text(item, target_language) for item in kb.get('red_flags', [])[:4]
    ]

    # Translate doctor summary for patient
    doctor_summary = str(results.get('doctor_summary', ''))
    if doctor_summary and doctor_summary != 'N/A':
        translated['doctor_summary'] = translate_text(doctor_summary, target_language)
    
    # Static labels
    translated['title'] = translate_text('Your Health Report', target_language)
    translated['what_found'] = translate_text('What We Found', target_language)
    translated['what_expect'] = translate_text('What to Expect Next', target_language)
    translated['when_help'] = translate_text('When to Get Help Immediately', target_language)
    translated['disclaimer'] = translate_text(
        'This page is written in simple language to help you understand your results. '
        'For detailed medical information, speak with your doctor.', target_language
    )

    return translated
