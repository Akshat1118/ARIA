"""
ARIA — Triage Agent
Takes diagnosis + patient info → returns urgency level + reasoning.
Uses Google Gemini with a clinical triage prompt.
"""

import json
import google.generativeai as genai


def run_triage(model: genai.GenerativeModel, diagnosis: str, confidence: int,
               age: int, vitals: str, history: str) -> dict:
    """
    Run the Triage Agent.

    Returns dict with:
        - triage_level: CRITICAL / HIGH / MODERATE / LOW
        - urgency_score: 1-10
        - reasoning: one-line explanation
    """

    prompt = f"""You are a clinical triage AI assistant.

Given:
- Diagnosis: {diagnosis} (Confidence: {confidence}%)
- Patient Age: {age}
- Vitals: {vitals}
- Medical History / Comorbidities: {history}

Assign a triage priority:
- CRITICAL (treat within 10 minutes)
- HIGH (treat within 30 minutes)
- MODERATE (treat within 1 hour)
- LOW (treat within 4 hours)

Return your response as a JSON object with these exact keys:
{{
    "triage_level": "CRITICAL",
    "urgency_score": 9,
    "reasoning": "One-line reasoning for the triage decision"
}}

Return ONLY the JSON object, nothing else."""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Clean up markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    result = json.loads(raw)

    return {
        "triage_level": result.get("triage_level", "MODERATE"),
        "urgency_score": result.get("urgency_score", 5),
        "reasoning": result.get("reasoning", "")
    }
