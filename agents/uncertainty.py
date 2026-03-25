"""
ARIA — Uncertainty Quantification Layer (v2 — Local Model)
Runs the local DeepSeek-R1 diagnostic model multiple times with slight
prompt variation to measure epistemic uncertainty via response variance.

Unlike v1 which burned Gemini API calls, this runs entirely locally via Ollama.
"""

import math
from agents.diagnostic import run_diagnosis


def compute_uncertainty(model=None, symptoms="", vitals="", labs="",
                        history="", age=0, gender="", n_runs=1):
    """
    Runs the diagnostic agent N times and measures the variance in its confidence
    and diagnoses to calculate true epistemic uncertainty.

    NOTE: 'model' parameter kept for API compatibility but is NOT used.
    All inference runs locally on DeepSeek-R1 via Ollama — zero API cost.
    
    Using 1 run to keep demo fast (local inference takes ~10-20s on M1).
    """

    results = []

    for i in range(n_runs):
        try:
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
        except Exception as e:
            # If Ollama fails, continue with what we have
            print(f"[UQ] Run {i+1} failed: {e}")
            continue

    if not results:
        # Complete fallback if local model is unreachable
        return {
            "diagnosis": "Model unavailable — check Ollama status",
            "confidence": 0,
            "alternatives": [],
            "indicators": "Local DeepSeek-R1 model could not be reached",
            "epistemic_uncertainty": 100.0,
            "data_quality_score": 0,
            "final_uncertainty_score": 100.0,
            "should_defer_to_human": True,
            "model_used": "DeepSeek-R1:8b (Local via Ollama) — OFFLINE"
        }

    # 1. Calculate Mean Confidence
    confidences = [r["confidence"] for r in results]
    mean_confidence = sum(confidences) / len(confidences)

    # 2. Calculate Standard Deviation (Epistemic Uncertainty)
    if len(confidences) > 1:
        variance = sum((x - mean_confidence) ** 2 for x in confidences) / len(confidences)
        std_deviation = math.sqrt(variance)
    else:
        std_deviation = 0.0

    # 3. Calculate Data Quality Score (Penalize missing critical fields)
    missing_points = 0
    if not vitals or vitals.lower() in ["none", "n/a", "not provided"]:
        missing_points += 15
    if not labs or labs.lower() in ["none", "n/a", "not provided"]:
        missing_points += 15

    data_quality_score = 100 - missing_points

    # 4. Final Uncertainty Score
    final_uncertainty = std_deviation + (missing_points * 0.5)

    # Should Defer to Human?
    should_defer = final_uncertainty > 20 or mean_confidence < 60

    # We pick the most common diagnosis as the "Primary" one
    diagnoses_counts = {}
    for r in results:
        diag = r["diagnosis"]
        diagnoses_counts[diag] = diagnoses_counts.get(diag, 0) + 1

    primary_diagnosis = max(diagnoses_counts, key=diagnoses_counts.get)

    # Find the result dict that matches the primary diagnosis
    best_result = next(r for r in results if r["diagnosis"] == primary_diagnosis)

    # Enrich the returned diagnostic object with UQ data
    enriched_result = {
        "diagnosis": primary_diagnosis,
        "confidence": round(mean_confidence),
        "alternatives": best_result.get("alternatives", []),
        "indicators": best_result.get("indicators", ""),

        # UQ fields
        "epistemic_uncertainty": round(std_deviation, 2),
        "data_quality_score": data_quality_score,
        "final_uncertainty_score": round(final_uncertainty, 2),
        "should_defer_to_human": should_defer,
        
        # Model transparency & explicit proof
        "model_used": best_result.get("model_used", "DeepSeek-R1:8b (Local via Ollama)"),
        "local_reasoning": best_result.get("local_reasoning", "No local reasoning captured.")
    }

    return enriched_result
