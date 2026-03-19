"""
ARIA — Pipeline Orchestrator
Connects all 4 agents + bias audit in sequence.
Memory → Diagnostic → Triage → Bias Audit → Explainability
"""

import google.generativeai as genai
from agents.memory import get_patient_history, store_visit
from agents.diagnostic import run_diagnosis
from agents.triage import run_triage
from agents.explainability import run_explainability
from bias.audit import run_bias_audit
from utils.sdg_tracker import increment_triaged, increment_bias_flagged


def run_pipeline(model: genai.GenerativeModel, patient_data: dict, status_callback=None) -> dict:
    """
    Run the full ARIA agent pipeline.

    Args:
        model: Google Gemini GenerativeModel instance
        patient_data: dict with keys: patient_id, name, age, gender, symptoms, vitals, labs, history, income_bracket
        status_callback: optional function(agent_name, status) for live UI updates

    Returns:
        dict with all agent outputs combined
    """

    def update_status(agent, status):
        if status_callback:
            status_callback(agent, status)

    results = {}

    # ──────────────────────────────────────────
    # STEP 1: Temporal Memory Agent
    # ──────────────────────────────────────────
    update_status("Temporal Memory Agent", "scanning")
    patient_id = patient_data.get("patient_id", "UNKNOWN")
    memory_summary = get_patient_history(patient_id)
    results["memory_summary"] = memory_summary
    update_status("Temporal Memory Agent", "done")

    # ──────────────────────────────────────────
    # STEP 2: Diagnostic Agent
    # ──────────────────────────────────────────
    update_status("Diagnostic Agent", "analyzing")

    # Combine stored history with current medical history
    combined_history = patient_data.get("history", "None")
    if memory_summary != "No previous visits found for this patient.":
        combined_history += f"\n\nPrevious Visits:\n{memory_summary}"

    diagnosis_result = run_diagnosis(
        model=model,
        symptoms=patient_data.get("symptoms", ""),
        vitals=patient_data.get("vitals", ""),
        labs=patient_data.get("labs", ""),
        history=combined_history,
        age=patient_data.get("age", 0),
        gender=patient_data.get("gender", "")
    )
    results["diagnosis"] = diagnosis_result
    update_status("Diagnostic Agent", "done")

    # ──────────────────────────────────────────
    # STEP 3: Triage Agent
    # ──────────────────────────────────────────
    update_status("Triage Agent", "scoring")
    triage_result = run_triage(
        model=model,
        diagnosis=diagnosis_result["diagnosis"],
        confidence=diagnosis_result["confidence"],
        age=patient_data.get("age", 0),
        vitals=patient_data.get("vitals", ""),
        history=combined_history
    )
    results["triage"] = triage_result
    update_status("Triage Agent", "done")

    # ──────────────────────────────────────────
    # STEP 4: Bias Audit
    # ──────────────────────────────────────────
    update_status("Bias Monitor", "auditing")
    bias_result = run_bias_audit(
        patient_data=patient_data,
        diagnosis=diagnosis_result["diagnosis"],
        triage_level=triage_result["triage_level"],
        urgency_score=triage_result["urgency_score"]
    )
    results["bias_report"] = bias_result
    update_status("Bias Monitor", "done")

    # ──────────────────────────────────────────
    # STEP 5: Explainability Agent
    # ──────────────────────────────────────────
    update_status("Explainability Agent", "writing")
    summary = run_explainability(
        model=model,
        diagnosis=diagnosis_result["diagnosis"],
        confidence=diagnosis_result["confidence"],
        triage_level=triage_result["triage_level"],
        indicators=diagnosis_result["indicators"],
        memory_summary=memory_summary
    )
    results["doctor_summary"] = summary
    update_status("Explainability Agent", "done")

    # ──────────────────────────────────────────
    # STEP 6: Save visit + update SDG counters
    # ──────────────────────────────────────────
    store_visit(
        patient_id=patient_id,
        patient_name=patient_data.get("name", "Unknown"),
        symptoms=patient_data.get("symptoms", ""),
        diagnosis=diagnosis_result["diagnosis"],
        confidence=diagnosis_result["confidence"],
        triage_level=triage_result["triage_level"],
        urgency_score=triage_result["urgency_score"],
        notes=summary
    )

    # Update SDG impact counters
    increment_triaged()
    if bias_result["overall_flag"]:
        increment_bias_flagged()

    return results
