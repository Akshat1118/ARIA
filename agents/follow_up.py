"""
ARIA — Follow-Up Agent
Generates structured follow-up timelines and care schedules for the patient
based on diagnosis, treatment, and referral decisions.
Uses Google Gemini with a clinical follow-up planning prompt.
Includes retry logic for rate limit errors.
"""

import json
import time
import google.generativeai as genai


def run_follow_up(model: genai.GenerativeModel, diagnosis: str, triage_level: str,
                  treatment_plan: dict, referral: dict, age: int, history: str,
                  max_retries: int = 3) -> dict:
    """
    Run the Follow-Up Agent with automatic retry on rate limits.

    Returns dict with:
        - discharge_instructions: key instructions for patient discharge
        - follow_up_timeline: list of follow-up steps with timeframes
        - red_flags: warning signs that should trigger immediate return to ED
        - lifestyle_advice: relevant lifestyle modifications
    """

    # Format treatment info for the prompt
    medications_str = ""
    if treatment_plan.get("medications"):
        meds = treatment_plan["medications"]
        if isinstance(meds, list):
            medications_str = ", ".join(
                m.get("name", "medication") if isinstance(m, dict) else str(m)
                for m in meds
            )
        else:
            medications_str = str(meds)

    referral_depts = ", ".join(referral.get("departments", [])) if referral.get("referral_needed") else "None"

    prompt = f"""You are a clinical follow-up care planning AI assistant.

Given the following clinical context:
- Diagnosis: {diagnosis}
- Triage Level: {triage_level}
- Current Medications: {medications_str or 'None specified'}
- Specialist Referrals: {referral_depts}
- Patient Age: {age}
- Medical History: {history}

Create a structured follow-up care plan. Return your response as a JSON object with these exact keys:
{{
    "discharge_instructions": "Clear, concise discharge instructions",
    "follow_up_timeline": [
        {{"timeframe": "24-48 hours", "action": "Follow-up with primary care physician"}},
        {{"timeframe": "1 week", "action": "Repeat lab work"}},
        {{"timeframe": "1 month", "action": "Specialist follow-up"}}
    ],
    "red_flags": ["Warning sign 1 that requires immediate ED return", "Warning sign 2"],
    "lifestyle_advice": "Relevant lifestyle modifications for recovery"
}}

Be specific and evidence-based. Tailor advice to the patient's age and history.
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
                "discharge_instructions": result.get("discharge_instructions", ""),
                "follow_up_timeline": result.get("follow_up_timeline", []),
                "red_flags": result.get("red_flags", []),
                "lifestyle_advice": result.get("lifestyle_advice", "")
            }

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                wait_time = (attempt + 1) * 15
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            raise
