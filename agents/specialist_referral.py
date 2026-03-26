"""
ARIA — Specialist Referral Agent
Determines whether a patient case requires specialist consultation,
and identifies which department(s) should be involved.
Uses Google Gemini with a clinical referral prompt.
Includes retry logic for rate limit errors.
"""

import json
import time
import google.generativeai as genai


def run_specialist_referral(model: genai.GenerativeModel, diagnosis: str, confidence: int,
                            triage_level: str, age: int, gender: str, history: str,
                            indicators: str, max_retries: int = 3) -> dict:
    """
    Run the Specialist Referral Agent with automatic retry on rate limits.

    Returns dict with:
        - referral_needed: bool — whether specialist consultation is recommended
        - departments: list of recommended departments
        - urgency: IMMEDIATE / WITHIN_24H / ROUTINE
        - reasoning: one-line rationale for referral
    """

    prompt = f"""You are a clinical specialist referral AI assistant in an Emergency Department.

Given the following clinical assessment:
- Diagnosis: {diagnosis} (Confidence: {confidence}%)
- Triage Level: {triage_level}
- Patient Age: {age}, Gender: {gender}
- Medical History: {history}
- Key Clinical Indicators: {indicators}

Determine whether this patient requires specialist consultation beyond the ED.
Return your response as a JSON object with these exact keys:
{{
    "referral_needed": true,
    "departments": ["Cardiology", "Internal Medicine"],
    "urgency": "IMMEDIATE",
    "reasoning": "One-line rationale for the referral decision"
}}

The urgency levels are:
- IMMEDIATE: Specialist needed within minutes (e.g., cardiac catheterization, stroke team)
- WITHIN_24H: Specialist consultation within 24 hours
- ROUTINE: Outpatient follow-up appointment

If no specialist referral is needed, set referral_needed to false and departments to an empty list.
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
                "referral_needed": result.get("referral_needed", False),
                "departments": result.get("departments", []),
                "urgency": result.get("urgency", "ROUTINE"),
                "reasoning": result.get("reasoning", "")
            }

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 15
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise
