"""
ARIA — Explainability Agent
Takes all agent outputs → returns one clean, readable summary for the doctor.
Uses Google Gemini to translate clinical AI outputs into plain English.
"""

import google.generativeai as genai


def run_explainability(model: genai.GenerativeModel, diagnosis: str, confidence: int,
                       triage_level: str, indicators: str, memory_summary: str) -> str:
    """
    Run the Explainability Agent.

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

    response = model.generate_content(prompt)
    return response.text.strip()
