"""
ARIA — Uncertainty Quantification Layer (Phase 3)
Instead of trusting a single LLM output, this runs the Diagnostic Agent
multiple times to measure variance (epistemic uncertainty).
"""

import math
from agents.diagnostic import run_diagnosis

def compute_uncertainty(model, symptoms, vitals, labs, history, age, gender, n_runs=2):
    """
    Runs the diagnostic agent N times and measures the variance in its confidence
    and diagnoses to calculate true epistemic uncertainty.
    
    (Note: Using 2 runs instead of 3 to save Gemini API quota on Free Tier,
     while still allowing basic variance calculation.)
    """
    
    results = []
    
    # Run slightly varied calls (we can simulate prompt variation by just calling it N times,
    # because Gemini responses inherently have slight temperature/variance differences)
    for i in range(n_runs):
        res = run_diagnosis(
            model=model,
            symptoms=symptoms,
            vitals=vitals,
            labs=labs,
            history=history,
            age=age,
            gender=gender
        )
        if res and "confidence" in res:
            results.append(res)

    if not results:
         return None
         
    # 1. Calculate Mean Confidence
    confidences = [r["confidence"] for r in results]
    mean_confidence = sum(confidences) / len(confidences)
    
    # 2. Calculate Standard Deviation (Epistemic Uncertainty)
    variance = sum((x - mean_confidence) ** 2 for x in confidences) / len(confidences)
    std_deviation = math.sqrt(variance)
    
    # 3. Calculate Data Quality Score (Penalize missing critical fields)
    missing_points = 0
    if not vitals or vitals.lower() in ["none", "n/a", "not provided"]:
        missing_points += 15
    if not labs or labs.lower() in ["none", "n/a", "not provided"]:
        missing_points += 15
        
    data_quality_score = 100 - missing_points
    
    # 4. Final Uncertainty Score
    # High standard deviation = High epistemic uncertainty.
    # We combine STD and data quality penalty.
    final_uncertainty = std_deviation + (missing_points * 0.5)
    
    # Should Defer to Human?
    should_defer = final_uncertainty > 20 or mean_confidence < 60
    
    # We pick the most common diagnosis as the "Primary" one
    diagnoses_counts = {}
    for r in results:
        diag = r["diagnosis"]
        diagnoses_counts[diag] = diagnoses_counts.get(diag, 0) + 1
    
    primary_diagnosis = max(diagnoses_counts, key=diagnoses_counts.get)
    
    # Find the result dict that matches the primary diagnosis best to return its indicators
    best_result = next(r for r in results if r["diagnosis"] == primary_diagnosis)
    
    # Enrich the returned diagnostic object with our UQ layer data
    enriched_result = {
        "diagnosis": primary_diagnosis,
        "confidence": round(mean_confidence),
        "alternatives": best_result["alternatives"],
        "indicators": best_result["indicators"],
        
        # New UQ fields
        "epistemic_uncertainty": round(std_deviation, 2),
        "data_quality_score": data_quality_score,
        "final_uncertainty_score": round(final_uncertainty, 2),
        "should_defer_to_human": should_defer
    }
    
    return enriched_result
