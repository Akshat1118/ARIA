"""
ARIA — Bias Audit Module
Rule-based checks to detect if triage/diagnosis might be biased
based on patient demographics (gender, age, income).
No LLM call — pure Python logic.
"""


def run_bias_audit(patient_data: dict, diagnosis: str, triage_level: str, urgency_score: int) -> dict:
    """
    Run bias checks on the clinical decision.

    Returns dict with:
        - gender_bias: {status, detail}
        - age_bias: {status, detail}
        - income_bias: {status, detail}
        - overall_flag: True if any bias was flagged
    """

    gender = patient_data.get("gender", "").lower()
    age = patient_data.get("age", 0)
    income = patient_data.get("income_bracket", "").lower()
    symptoms = patient_data.get("symptoms", "").lower()

    report = {
        "gender_bias": {"status": "✅ None Detected", "detail": "No gender-related bias patterns found."},
        "age_bias": {"status": "✅ None Detected", "detail": "No age-related bias patterns found."},
        "income_bias": {"status": "✅ None Detected", "detail": "No income-related bias patterns found."},
        "overall_flag": False
    }

    # --- Gender Bias Checks ---
    # Flag if cardiac symptoms downgraded for female patients
    cardiac_keywords = ["chest pain", "shortness of breath", "palpitations", "chest tightness"]
    has_cardiac = any(kw in symptoms for kw in cardiac_keywords)

    if gender == "female" and has_cardiac and triage_level in ["LOW", "MODERATE"]:
        report["gender_bias"] = {
            "status": "⚠️ Flagged",
            "detail": "Cardiac symptoms in female patient triaged below HIGH. Studies show women's cardiac symptoms are often undertriaged."
        }
        report["overall_flag"] = True

    # --- Age Bias Checks ---
    # Flag if elderly patient with serious symptoms gets low triage
    if age >= 65 and urgency_score <= 4:
        report["age_bias"] = {
            "status": "⚠️ Flagged",
            "detail": f"Patient is {age} years old with urgency score {urgency_score}/10. Elderly patients may have atypical presentations — consider upgrading triage."
        }
        report["overall_flag"] = True

    # Flag if young patient gets high triage without strong indicators
    if age < 25 and urgency_score >= 8 and triage_level == "CRITICAL":
        report["age_bias"] = {
            "status": "⚠️ Review Suggested",
            "detail": f"Young patient ({age}y) assigned CRITICAL. Verify this isn't over-triage based on age anxiety."
        }
        # Don't set overall_flag for review suggestions, only for clear flags

    # --- Income Bias Checks ---
    # Flag if low-income patients consistently get lower urgency
    if income in ["low", "below poverty line", "bpl"] and triage_level in ["LOW", "MODERATE"]:
        report["income_bias"] = {
            "status": "⚠️ Flagged",
            "detail": "Low-income patient received lower triage priority. Ensure socioeconomic status doesn't influence clinical urgency assessment."
        }
        report["overall_flag"] = True

    return report
