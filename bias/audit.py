"""
ARIA — Cascading Bias Detection Module (Phase 4)
Moves beyond simple if/else rules to compute quantitative bias scores at each pipeline stage.
Detects if bias is amplifying (cascading) across agents.
"""

class CascadingBiasDetector:
    def __init__(self, patient_data):
        self.patient_data = patient_data
        self.gender = patient_data.get("gender", "").lower()
        self.age = patient_data.get("age", 0)
        self.income = patient_data.get("income_bracket", "").lower()
        self.symptoms = patient_data.get("symptoms", "").lower()
        
        self.bias_scores_per_agent = {}
        self.reports = {}
        
    def check_diagnostic_bias(self, diagnostic_result):
        """Check for bias specifically in the diagnostic agent's output"""
        score = 0
        detail = []
        
        diagnosis = diagnostic_result.get("diagnosis", "")
        confidence = diagnostic_result.get("confidence", 100)
        
        cardiac_keywords = ["chest pain", "shortness of breath", "palpitations", "chest tightness"]
        has_cardiac = any(kw in self.symptoms for kw in cardiac_keywords)
        
        # Gender bias in diagnosis: e.g. female cardiac symptoms misdiagnosed as anxiety
        if self.gender == "female" and has_cardiac:
            if "anxiety" in diagnosis.lower() or "stress" in diagnosis.lower():
                score += 0.4
                detail.append("⚠️ Potential gender bias: Cardiac symptoms diagnosed as anxiety in female patient.")
                
        # Age bias: underdiagnosing older adults
        if self.age >= 65 and confidence < 75:
            score += 0.2
            detail.append("⚠️ Potential age bias: Low diagnostic confidence in elderly patient; may need more rigorous evaluation.")
            
        self.bias_scores_per_agent["Diagnostic"] = score
        self.reports["Diagnostic"] = detail
        return score

    def check_triage_bias(self, triage_result):
        """Check for bias specifically in the triage agent's output"""
        score = 0
        detail = []
        
        triage_level = triage_result.get("triage_level", "UNKNOWN")
        urgency_score = int(triage_result.get("urgency_score", 0))
        
        cardiac_keywords = ["chest pain", "shortness of breath", "palpitations"]
        has_cardiac = any(kw in self.symptoms for kw in cardiac_keywords)
        
        # Gender bias in triage: Undertriaging female cardiac patients
        if self.gender == "female" and has_cardiac and triage_level in ["LOW", "MODERATE"]:
            score += 0.5
            detail.append("⚠️ Gender bias: Female cardiac symptoms undertriaged.")
            
        # Age bias: Undertriaging elderly
        if self.age >= 65 and urgency_score <= 4:
            score += 0.3
            detail.append(f"⚠️ Age bias: Elderly patient ({self.age}y) assigned low urgency ({urgency_score}/10).")
            
        # Income bias: Lower triage based on socioeconomic status
        if self.income in ["low", "below poverty line"] and triage_level in ["LOW", "MODERATE"]:
            score += 0.3
            detail.append("⚠️ Socioeconomic bias: Low-income patient assigned low urgency without clear justification.")
            
        self.bias_scores_per_agent["Triage"] = score
        self.reports["Triage"] = detail
        return score
        
    def compute_cascade_score(self):
        """Calculate if bias is amplifying across the pipeline"""
        diag_score = self.bias_scores_per_agent.get("Diagnostic", 0)
        triage_score = self.bias_scores_per_agent.get("Triage", 0)
        
        cascade_detected = False
        amplification_factor = 0
        
        if diag_score > 0 and triage_score > diag_score:
            cascade_detected = True
            amplification_factor = triage_score / diag_score
            
        return {
            "cascade_detected": cascade_detected,
            "amplification_factor": round(amplification_factor, 2),
            "total_bias_score": round(diag_score + triage_score, 2)
        }


def run_bias_audit(patient_data: dict, diagnosis_result: dict, triage_result: dict) -> dict:
    """
    Runs the Cascading Bias Detector and formats the report for UI.
    """
    detector = CascadingBiasDetector(patient_data)
    
    detector.check_diagnostic_bias(diagnosis_result)
    detector.check_triage_bias(triage_result)
    
    cascade_metrics = detector.compute_cascade_score()
    
    report = {
        "gender_bias": {"status": "✅ None Detected", "detail": "No gender-related bias patterns found."},
        "age_bias": {"status": "✅ None Detected", "detail": "No age-related bias patterns found."},
        "income_bias": {"status": "✅ None Detected", "detail": "No income-related bias patterns found."},
        "cascading_amplification": cascade_metrics["cascade_detected"],
        "total_bias_score": cascade_metrics["total_bias_score"],
        "overall_flag": cascade_metrics["total_bias_score"] > 0
    }
    
    all_details = detector.reports["Diagnostic"] + detector.reports["Triage"]
    
    for detail in all_details:
        if "gender" in detail.lower():
            report["gender_bias"] = {"status": "⚠️ Flagged", "detail": detail}
        elif "age" in detail.lower():
            report["age_bias"] = {"status": "⚠️ Flagged", "detail": detail}
        elif "socioeconomic" in detail.lower() or "income" in detail.lower():
            report["income_bias"] = {"status": "⚠️ Flagged", "detail": detail}
            
    if cascade_metrics["cascade_detected"]:
        if report["gender_bias"]["status"] == "⚠️ Flagged":
            report["gender_bias"]["detail"] += f" [CASCADING BIAS: Amplified by {cascade_metrics['amplification_factor']}x]"
        elif report["age_bias"]["status"] == "⚠️ Flagged":
            report["age_bias"]["detail"] += f" [CASCADING BIAS: Amplified by {cascade_metrics['amplification_factor']}x]"
            
    return report
