"""
ARIA — Diagnostic Agent
Takes patient symptoms, vitals, labs, history → returns diagnosis + confidence score.
Uses Google Gemini with a clinical diagnostic prompt.
"""

import json
import google.generativeai as genai


def run_diagnosis(model: genai.GenerativeModel, symptoms: str, vitals: str, labs: str,
                  history: str, age: int, gender: str) -> dict:
    """
    Run the Diagnostic Agent.

    Returns dict with:
        - diagnosis: most likely diagnosis
        - confidence: confidence score (0-100)
        - alternatives: list of top 2 alternative diagnoses
        - indicators: key clinical indicators
    """

    prompt = f"""You are a clinical diagnostic AI assistant.

Given the following patient information:
- Symptoms: {symptoms}
- Vitals: {vitals}
- Lab Results: {labs}
- Medical History: {history}
- Age: {age}, Gender: {gender}

Perform a differential diagnosis. Return your response as a JSON object with these exact keys:
{{
    "diagnosis": "Most likely diagnosis",
    "confidence": 85,
    "alternatives": ["Alternative 1", "Alternative 2"],
    "indicators": "Key clinical indicators that led to this conclusion"
}}

Be concise. Use clinical language. Return ONLY the JSON object, nothing else."""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Clean up markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # Remove first line (```json)
        raw = raw.rsplit("```", 1)[0]  # Remove last ```
        raw = raw.strip()

    result = json.loads(raw)

    # Ensure all expected keys exist
    return {
        "diagnosis": result.get("diagnosis", "Unknown"),
        "confidence": result.get("confidence", 0),
        "alternatives": result.get("alternatives", []),
        "indicators": result.get("indicators", "")
    }
