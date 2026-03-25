"""
ARIA — Conflict Resolver Agent (Phase 5)
Detects and resolves contradictions between the Diagnostic Agent
and the Triage Agent.
"""

def detect_conflict(diagnosis_result: dict, triage_result: dict) -> bool:
    """
    Returns True if there is a clinical conflict between diagnostic
    certainty and triage urgency.
    """
    confidence = diagnosis_result.get("confidence", 100)
    urgency = int(triage_result.get("urgency_score", 0))
    
    # Conflict 1: High urgency but low confidence
    if confidence < 70 and urgency >= 7:
        return True
        
    # Conflict 2: Low urgency but critical diagnosis
    triage_level = triage_result.get("triage_level", "LOW")
    critical_keywords = ["infarction", "stroke", "sepsis", "embolism", "failure"]
    diagnosis = diagnosis_result.get("diagnosis", "").lower()
    
    has_critical_diag = any(kw in diagnosis for kw in critical_keywords)
    if has_critical_diag and triage_level in ["LOW", "MODERATE"]:
        return True
        
    return False


def resolve_conflict(diagnosis_result: dict, triage_result: dict) -> dict:
    """
    Intelligently resolves the conflict and provides an adjusted
    triage recommendation with an audit trail.
    """
    confidence = diagnosis_result.get("confidence", 100)
    urgency = int(triage_result.get("urgency_score", 0))
    triage_level = triage_result.get("triage_level", "UNKNOWN")
    
    adjusted_triage = triage_result.copy()
    audit_trail = []
    
    # Uncertainty-adjusted weighting
    if confidence < 70 and urgency >= 7:
        audit_trail.append(f"Conflict Detected: High urgency ({urgency}/10) but low diagnostic confidence ({confidence}%).")
        audit_trail.append("Resolution: Erring on the side of caution. Maintaining high triage but flagging for immediate HUMAN REVIEW.")
        
        adjusted_triage["triage_level"] = "CRITICAL" if urgency >= 8 else "HIGH"
        adjusted_triage["urgency_score"] = min(10, urgency + 1)
        adjusted_triage["reasoning"] = "[CONFLICT RESOLVED: Up-triaged due to diagnostic uncertainty] " + adjusted_triage.get("reasoning", "")
        
    critical_keywords = ["infarction", "stroke", "sepsis", "embolism", "failure"]
    diagnosis = diagnosis_result.get("diagnosis", "").lower()
    has_critical_diag = any(kw in diagnosis for kw in critical_keywords)
    
    if has_critical_diag and triage_level in ["LOW", "MODERATE"]:
        audit_trail.append(f"Conflict Detected: Critical diagnosis '{diagnosis}' but assigned {triage_level} triage.")
        audit_trail.append("Resolution: Diagnostic severity overrides initial triage. Up-triaging to HIGH.")
        
        adjusted_triage["triage_level"] = "HIGH"
        adjusted_triage["urgency_score"] = max(8, urgency)
        adjusted_triage["reasoning"] = "[CONFLICT RESOLVED: Up-triaged due to critical diagnosis] " + adjusted_triage.get("reasoning", "")

    adjusted_triage["conflict_audit"] = audit_trail
    adjusted_triage["human_review_required"] = True
    
    return adjusted_triage
