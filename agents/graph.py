"""
ARIA — LangGraph Orchestrator (Phase 2 — Dual Model Architecture)
DeepSeek-R1 (local via Ollama) handles diagnosis.
Gemini handles triage, explainability, and conflict resolution.
"""

from typing import Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
import google.generativeai as genai

from agents.memory import get_patient_history, store_visit
from agents.diagnostic import run_diagnosis, check_ollama_status
from agents.uncertainty import compute_uncertainty
from agents.triage import run_triage
from agents.conflict_resolver import detect_conflict, resolve_conflict
from agents.explainability import run_explainability
from bias.audit import run_bias_audit
from utils.sdg_tracker import increment_triaged, increment_bias_flagged


# 1. Define the Typed State
class AgentState(TypedDict):
    """
    The shared state for the LangGraph. Every node will read/write to this dictionary.
    Keys matching existing state will automatically overwrite/update.
    """
    model: Any
    patient_data: Dict[str, Any]
    status_callback: Any
    
    # Outputs that get filled in as graph progresses
    memory_summary: Optional[str]
    diagnosis_result: Optional[Dict[str, Any]]
    triage_result: Optional[Dict[str, Any]]
    bias_result: Optional[Dict[str, Any]]
    doctor_summary: Optional[str]
    
    # Internal metrics
    reanalyzed: bool
    conflict_detected: bool
    model_used: Optional[str]


# 2. Define the Nodes
def fetch_memory_node(state: AgentState):
    """Node 1: Fetches temporal memory for the patient."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Temporal Memory Agent", "scanning")
        
    patient_id = state["patient_data"].get("patient_id", "UNKNOWN")
    current_symptoms = state["patient_data"].get("symptoms", "")
    memory_summary = get_patient_history(patient_id, current_symptoms)
    
    if status_callback:
        status_callback("Temporal Memory Agent", "done")
        
    return {"memory_summary": memory_summary}


def initial_diagnostic_node(state: AgentState):
    """Node 2: Runs the initial diagnostic assessment using local DeepSeek-R1."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Diagnostic Agent", "analyzing via DeepSeek-R1 (local)")
        
    patient_data = state["patient_data"]
    
    # Diagnosis runs on LOCAL DeepSeek-R1 model via Ollama — zero API calls
    diagnosis_result = compute_uncertainty(
        model=None,  # Not needed — uses local DeepSeek-R1
        symptoms=patient_data.get("symptoms", ""),
        vitals=patient_data.get("vitals", ""),
        labs=patient_data.get("labs", ""),
        history=patient_data.get("history", "None"),
        age=patient_data.get("age", 0),
        gender=patient_data.get("gender", "")
    )
    
    model_used = diagnosis_result.get("model_used", "DeepSeek-R1:8b (Local)")
    
    if status_callback:
        status_callback("Diagnostic Agent", "done")
        
    return {"diagnosis_result": diagnosis_result, "reanalyzed": False, "model_used": model_used}


def reanalyze_diagnostic_node(state: AgentState):
    """Node 3 (Conditional): Re-runs diagnosis IF confidence was < 60%, incorporating temporal memory."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Diagnostic Agent", "re-analyzing via DeepSeek-R1 (low confidence)")
        
    patient_data = state["patient_data"]
    memory_summary = state.get("memory_summary", "No previous visits found for this patient.")
    
    # Combine history + memory for a better attempt
    combined_history = patient_data.get("history", "None")
    if memory_summary != "No previous visits found for this patient.":
        combined_history += f"\n\nPrevious Visits:\n{memory_summary}"
        
    # Re-run on LOCAL DeepSeek-R1 with enriched history
    diagnosis_result = compute_uncertainty(
        model=None,  # Not needed — uses local DeepSeek-R1
        symptoms=patient_data.get("symptoms", ""),
        vitals=patient_data.get("vitals", ""),
        labs=patient_data.get("labs", ""),
        history=combined_history,
        age=patient_data.get("age", 0),
        gender=patient_data.get("gender", "")
    )
    
    model_used = diagnosis_result.get("model_used", "DeepSeek-R1:8b (Local)")
    
    if status_callback:
        status_callback("Diagnostic Agent", "done")
        
    return {"diagnosis_result": diagnosis_result, "reanalyzed": True, "model_used": model_used}


def triage_node(state: AgentState):
    """Node 4: Assesses triage level based on final diagnosis and memory."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Triage Agent", "scoring")
        
    patient_data = state["patient_data"]
    diagnosis_result = state["diagnosis_result"]
    memory_summary = state.get("memory_summary", "")
    
    combined_history = patient_data.get("history", "None")
    if memory_summary and memory_summary != "No previous visits found for this patient.":
        combined_history += f"\n\nPrevious Visits:\n{memory_summary}"
    
    triage_result = run_triage(
        model=state["model"],
        diagnosis=diagnosis_result["diagnosis"],
        confidence=diagnosis_result["confidence"],
        age=patient_data.get("age", 0),
        vitals=patient_data.get("vitals", ""),
        history=combined_history
    )
    
    if status_callback:
        status_callback("Triage Agent", "done")
        
    return {"triage_result": triage_result, "conflict_detected": False}


def conflict_resolver_node(state: AgentState):
    """Node 4b (Conditional): Resolves conflict between diagnosis and triage."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Conflict Resolver", "resolving mismatch")
        
    adjusted_triage = resolve_conflict(
        diagnosis_result=state["diagnosis_result"],
        triage_result=state["triage_result"]
    )
    
    if status_callback:
        status_callback("Conflict Resolver", "done")
        
    return {"triage_result": adjusted_triage, "conflict_detected": True}


def bias_audit_node(state: AgentState):
    """Node 5: Scans the decisions thus far for bias."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Bias Monitor", "auditing")
        
    bias_result = run_bias_audit(
        patient_data=state["patient_data"],
        diagnosis_result=state["diagnosis_result"],
        triage_result=state["triage_result"]
    )
    
    if status_callback:
        status_callback("Bias Monitor", "done")
        
    return {"bias_result": bias_result}


def explainability_node(state: AgentState):
    """Node 6: Writes the final clinical summary."""
    status_callback = state.get("status_callback")
    if status_callback:
        status_callback("Explainability Agent", "writing")
        
    summary = run_explainability(
        model=state["model"],
        diagnosis=state["diagnosis_result"]["diagnosis"],
        confidence=state["diagnosis_result"]["confidence"],
        triage_level=state["triage_result"]["triage_level"],
        indicators=state["diagnosis_result"]["indicators"],
        memory_summary=state.get("memory_summary", "")
    )
    
    if status_callback:
        status_callback("Explainability Agent", "done")
        
    return {"doctor_summary": summary}


def save_visit_node(state: AgentState):
    """Node 7: Saves the visit to memory and updates counters."""
    patient_data = state["patient_data"]
    diagnosis_result = state["diagnosis_result"]
    triage_result = state["triage_result"]
    
    store_visit(
        patient_id=patient_data.get("patient_id", "UNKNOWN"),
        patient_name=patient_data.get("name", "Unknown"),
        symptoms=patient_data.get("symptoms", ""),
        diagnosis=diagnosis_result["diagnosis"],
        confidence=diagnosis_result["confidence"],
        triage_level=triage_result["triage_level"],
        urgency_score=triage_result["urgency_score"],
        notes=state["doctor_summary"]
    )
    
    increment_triaged()
    if state["bias_result"].get("overall_flag"):
        increment_bias_flagged()
        
    return {} # No state updates needed here


# 3. Define Routing Logic
def route_after_initial_diagnosis(state: AgentState) -> str:
    """
    Conditional logic: If confidence < 60%, route to reanalyze_diagnostic.
    Otherwise, proceed to triage.
    """
    confidence = state["diagnosis_result"].get("confidence", 0)
    if confidence < 60:
        return "reanalyze"
    return "proceed"


def route_after_triage(state: AgentState) -> str:
    """
    Conditional logic: If conflict detected, route to conflict_resolver.
    Otherwise, proceed to bias_audit.
    """
    if detect_conflict(state["diagnosis_result"], state["triage_result"]):
        return "resolve_conflict"
    return "proceed"


# 4. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("fetch_memory", fetch_memory_node)
workflow.add_node("initial_diagnostic", initial_diagnostic_node)
workflow.add_node("reanalyze_diagnostic", reanalyze_diagnostic_node)
workflow.add_node("triage", triage_node)
workflow.add_node("conflict_resolver", conflict_resolver_node)
workflow.add_node("bias_audit", bias_audit_node)
workflow.add_node("explainability", explainability_node)
workflow.add_node("save_visit", save_visit_node)

# PARALLEL EXECUTION: Both memory and initial diagnosis start off simultaneously
workflow.add_edge(START, "fetch_memory")
workflow.add_edge(START, "initial_diagnostic")

# Memory node has no downstream edge because it just populates `memory_summary`.
# The main flow continues from the diagnostic node:
workflow.add_conditional_edges(
    "initial_diagnostic",
    route_after_initial_diagnosis,
    {
        "reanalyze": "reanalyze_diagnostic",
        "proceed": "triage"
    }
)

# If re-analyzed, it goes straight to Triage afterwards
workflow.add_edge("reanalyze_diagnostic", "triage")

# Check for contradictions after triage
workflow.add_conditional_edges(
    "triage",
    route_after_triage,
    {
        "resolve_conflict": "conflict_resolver",
        "proceed": "bias_audit"
    }
)

# Conflict resolver goes back into the main flow
workflow.add_edge("conflict_resolver", "bias_audit")

# Linear flow for the rest
workflow.add_edge("bias_audit", "explainability")
workflow.add_edge("explainability", "save_visit")
workflow.add_edge("save_visit", END)

# Compile graph
aria_app = workflow.compile()


# 5. Pipeline Entry Point Wrapper (replaces `run_pipeline` from pipeline.py)
def run_pipeline(model: genai.GenerativeModel, patient_data: dict, status_callback=None) -> dict:
    """
    Drop-in replacement for the Streamlit app.
    Translates standard arguments into Graph State and triggers the run.
    """
    initial_state = {
        "model": model,
        "patient_data": patient_data,
        "status_callback": status_callback,
        "memory_summary": None,
        "diagnosis_result": None,
        "triage_result": None,
        "bias_result": None,
        "doctor_summary": None,
        "reanalyzed": False,
        "conflict_detected": False,
        "model_used": None
    }
    
    # Run the graph (using synchronous invoke, but it resolves the DAG)
    final_state = aria_app.invoke(initial_state)
    
    # Repackage the typed state back into the flat dictionary the UI expects
    return {
        "memory_summary": final_state.get("memory_summary", ""),
        "diagnosis": final_state.get("diagnosis_result", {}),
        "triage": final_state.get("triage_result", {}),
        "bias_report": final_state.get("bias_result", {}),
        "doctor_summary": final_state.get("doctor_summary", ""),
        "reanalyzed": final_state.get("reanalyzed", False),
        "conflict": final_state.get("conflict_detected", False),
        "model_used": final_state.get("model_used", "DeepSeek-R1:8b (Local)")
    }
