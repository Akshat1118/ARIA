"""
ARIA — Diagnostic Agent (v3 — Reverted to Gemini Cloud)
Uses Google Gemini API for fast clinical differential diagnosis.
This replaces the local DeepSeek model which was causing 5-10 minute lockups.
"""

import json
import time

def extract_json_from_response(text: str) -> dict:
    """Robustly extracts JSON from Gemini response."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[-1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
        
    try:
        return json.loads(text)
    except Exception:
        # Fallback if structure is broken
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
                
    return {
        "diagnosis": "Unable to parse diagnosis",
        "confidence": 0,
        "alternatives": [],
        "indicators": "Raw model output missing JSON."
    }

def run_diagnosis(model=None, symptoms: str = "", vitals: str = "",
                  labs: str = "", history: str = "", age: int = 0,
                  gender: str = "", max_retries: int = 2) -> dict:
    """
    Run the Diagnostic Agent using the provided Gemini model.
    """
    if not model:
        return {"diagnosis": "Error: Setup failed, AI Model not loaded.", "confidence": 0}

    prompt = f"""You are ARIA-Dx, an expert clinical diagnostic reasoning engine.
Your task: Given patient symptoms, vitals, lab results, and medical history, perform a rigorous differential diagnosis.

PATIENT INFORMATION:
- Age: {age}
- Gender: {gender}
- Presenting Symptoms: {symptoms}
- Vitals: {vitals}
- Lab Results: {labs}
- Medical History: {history}

STRICT RULES:
1. Use evidence-based clinical reasoning.
2. Provide a confidence score (0-100) based on how well the evidence supports the diagnosis.
3. Identify the KEY clinical indicators that drove your decision.

You MUST return ONLY a valid JSON object in this exact format:
{{
    "diagnosis": "Most likely diagnosis",
    "confidence": 85,
    "alternatives": ["Alternative 1", "Alternative 2"],
    "indicators": "Key clinical indicators that led to this conclusion"
}}
Return ONLY JSON."""

    # Implement quick retries
    last_error = None
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            result = extract_json_from_response(response.text)
            
            return {
                "diagnosis": result.get("diagnosis", "Unknown"),
                "confidence": min(max(int(result.get("confidence", 0)), 0), 100),
                "alternatives": result.get("alternatives", []),
                "indicators": result.get("indicators", ""),
                "model_used": "Gemini 2.5 Flash (Cloud)",
                "local_reasoning": "Reasoning handled natively in Gemini backend."
            }
        except Exception as e:
            last_error = e
            time.sleep(2)
            
    return {
        "diagnosis": f"Error communicating with AI: {str(last_error)}",
        "confidence": 0,
        "alternatives": [],
        "indicators": "Failed to generate diagnosis.",
        "model_used": "Failure",
        "local_reasoning": ""
    }

def check_ollama_status() -> dict:
    """Mock status return since we rely on Gemini now."""
    return {"ollama_running": False, "model_available": False}
