"""
ARIA — Patient Communicator Agent
Translates complex clinical reports into compassionate, accessible summaries
for the patient and their family members to understand.
Uses Google Gemini with an empathetic communication prompt.
Includes retry logic for rate limit errors.
"""

import time
import google.generativeai as genai


def run_patient_communication(model: genai.GenerativeModel, diagnosis: str, confidence: int,
                              triage_level: str, treatment_plan: dict, referral: dict,
                              patient_name: str, age: int, max_retries: int = 3) -> str:
    """
    Run the Patient Communicator Agent with automatic retry on rate limits.

    Returns a compassionate, jargon-free summary that a patient or their family
    can understand. Written at a 6th-grade reading level.
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

    referral_str = "No specialist referral needed."
    if referral.get("referral_needed"):
        depts = ", ".join(referral.get("departments", []))
        referral_str = f"You will be seen by: {depts} ({referral.get('urgency', 'ROUTINE')})"

    prompt = f"""You are a compassionate hospital communication assistant.

Write a short, clear message for the patient (or their family) explaining what is happening.

Clinical Context (DO NOT use medical jargon):
- Patient Name: {patient_name} (Age: {age})
- What was found: {diagnosis}
- How urgent: {triage_level}
- Medications being given: {medications_str or 'To be determined'}
- Next steps: {referral_str}

Rules:
1. Write at a 6th-grade reading level
2. Be warm, reassuring, and honest
3. Start by addressing the patient by first name
4. Explain what is happening in simple terms
5. Explain what the medical team is doing to help
6. End with one reassuring line
7. Keep it to 4-5 sentences maximum
8. Do NOT use medical terminology — translate everything

Return ONLY the patient message, nothing else."""

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
