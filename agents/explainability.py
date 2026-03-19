"""
ARIA — Explainability Agent
Takes all agent outputs → returns one clean, readable summary for the doctor.
Uses Google Gemini to translate clinical AI outputs into plain English.
Includes retry logic for rate limit errors.
"""

import time
import google.generativeai as genai


def run_explainability(model: genai.GenerativeModel, diagnosis: str, confidence: int,
                       triage_level: str, indicators: str, memory_summary: str,
                       max_retries: int = 3) -> str:
    """
    Run the Explainability Agent with automatic retry on rate limits.

    Returns a 3-sentence plain English summary that a busy doctor can read in 15 seconds.
    """

    prompt = f"""You are a medical explainability assistant.

Translate the following AI clinical outputs into a clear, 3-sentence summary
that a busy attending physician can read in under 15 seconds:

Diagnosis: {diagnosis} ({confidence}% confidence)
Triage Level: {triage_level}
Key Indicators: {indicators}
Past History Context: {memory_summary}

Write in plain English. No jargon. Start with the most critical finding.
Return ONLY the summary paragraph, nothing else."""

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 15
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise
