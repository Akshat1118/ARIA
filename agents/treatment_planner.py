"""
ARIA — Treatment Planner Agent
Takes diagnosis, triage level, patient data → returns evidence-based treatment plan.
Uses Google Gemini with a clinical treatment planning prompt.
Includes retry logic for rate limit errors.
"""

import json
import time
import google.generativeai as genai


def run_treatment_plan(model: genai.GenerativeModel, diagnosis: str, confidence: int,
                       triage_level: str, age: int, gender: str, history: str,
                       vitals: str, labs: str, max_retries: int = 3) -> dict:
    """
    Run the Treatment Planner Agent with automatic retry on rate limits.

    Returns dict with:
        - immediate_actions: list of urgent steps to take right now
        - medications: list of recommended medications with dosage
        - monitoring: what to monitor and how often
        - precautions: warnings or contraindications
    """

    prompt = f"""You are a clinical treatment planning AI assistant.

Given the following clinical assessment:
- Diagnosis: {diagnosis} (Confidence: {confidence}%)
- Triage Level: {triage_level}
- Patient Age: {age}, Gender: {gender}
- Vitals: {vitals}
- Lab Results: {labs}
- Medical History / Comorbidities: {history}

Create an evidence-based treatment plan. Return your response as a JSON object with these exact keys:
{{
    "immediate_actions": ["Action 1", "Action 2", "Action 3"],
    "medications": [
        {{"name": "Drug Name", "dosage": "Dosage", "route": "IV/Oral/etc", "frequency": "Frequency"}}
    ],
    "monitoring": "What vitals/labs to monitor and how frequently",
    "precautions": "Key warnings, contraindications, or drug interactions to watch for"
}}

Use evidence-based clinical guidelines. Be specific with dosages appropriate for the patient's age.
Return ONLY the JSON object, nothing else."""

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
                "immediate_actions": result.get("immediate_actions", []),
                "medications": result.get("medications", []),
                "monitoring": result.get("monitoring", ""),
                "precautions": result.get("precautions", "")
            }

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 15
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise
