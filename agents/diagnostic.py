"""
ARIA — Diagnostic Agent
Takes patient symptoms, vitals, labs, history → returns diagnosis + confidence score.
Uses Google Gemini with a clinical diagnostic prompt.
Includes retry logic for rate limit errors.
"""

import json
import time
import google.generativeai as genai


def run_diagnosis(model: genai.GenerativeModel, symptoms: str, vitals: str, labs: str,
                  history: str, age: int, gender: str, max_retries: int = 3) -> dict:
    """
    Run the Diagnostic Agent with automatic retry on rate limits.

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

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()

            # Clean up markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1]
                raw = raw.rsplit("```", 1)[0]
                raw = raw.strip()

            result = json.loads(raw)

            return {
                "diagnosis": result.get("diagnosis", "Unknown"),
                "confidence": result.get("confidence", 0),
                "alternatives": result.get("alternatives", []),
                "indicators": result.get("indicators", "")
            }

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 15  # 15s, 30s, 45s
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise  # Re-raise non-retryable errors or if all retries exhausted
