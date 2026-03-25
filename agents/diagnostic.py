"""
ARIA — Diagnostic Agent (v2 — DeepSeek-R1 Local Model)
Uses a locally-hosted DeepSeek-R1 medical reasoning model via Ollama
for clinical differential diagnosis. Zero cloud API calls.

Architecture:
  Patient data → DeepSeek-R1 (local via Ollama) → Structured diagnosis JSON
  This replaces the previous Gemini API wrapper with genuine local ML inference.
"""

import json
import time
import requests

# ── Ollama Configuration ──
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:8b"

# ── Clinical System Prompt (Domain-Specific Prompt Engineering) ──
CLINICAL_SYSTEM_PROMPT = """You are ARIA-Dx, an expert clinical diagnostic reasoning engine.
You are embedded inside a multi-agent clinical decision support system used in hospitals.

Your task: Given patient symptoms, vitals, lab results, and medical history, perform
a rigorous differential diagnosis using clinical reasoning.

STRICT RULES:
1. Use evidence-based clinical reasoning (not guessing)
2. Consider the patient's age, gender, and history for risk stratification
3. Provide a confidence score based on how well the evidence supports the diagnosis
4. Always list differential diagnoses ranked by likelihood
5. Identify the KEY clinical indicators that drove your decision

You MUST return ONLY a valid JSON object in this exact format, nothing else:
{
    "diagnosis": "Most likely diagnosis",
    "confidence": 85,
    "alternatives": ["Alternative 1", "Alternative 2"],
    "indicators": "Key clinical indicators that led to this conclusion"
}

Return ONLY the JSON. No markdown, no explanation, no code fences."""


def _call_ollama(prompt: str, max_retries: int = 2) -> str:
    """
    Calls the local Ollama DeepSeek-R1 model.
    Returns raw text response.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "system": CLINICAL_SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 2048,
        }
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise ConnectionError(
                "Cannot connect to Ollama. Make sure Ollama is running: "
                "open -a Ollama  (or)  ollama serve"
            )
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise


def _extract_json_from_response(raw: str) -> dict:
    """
    Robustly extracts JSON from DeepSeek-R1 response.
    Handles: raw JSON, markdown fences, <think> tags, mixed text.
    Also extracts the <think> block to show the model's reasoning.
    """
    text = raw.strip()
    reasoning = "Reasoning block not found in local model output."

    # Extract <think> block for hackathon proof
    if "<think>" in text:
        try:
            think_start = text.index("<think>") + len("<think>")
            think_end = text.index("</think>")
            reasoning = text[think_start:think_end].strip()
        except ValueError:
            pass
            
        # Get everything after the last </think> tag for JSON parsing
        parts = text.split("</think>")
        if len(parts) > 1:
            text = parts[-1].strip()

    # Remove markdown code fences if present
    if "```json" in text:
        text = text.split("```json")[-1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    parsed_json = None
    # Try direct JSON parse
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    if not parsed_json:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                parsed_json = json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

    if not parsed_json:
        # Last resort: return a structured fallback
        parsed_json = {
            "diagnosis": "Unable to parse diagnosis",
            "confidence": 0,
            "alternatives": [],
            "indicators": f"Raw model output missing JSON."
        }
        
    parsed_json["local_reasoning"] = reasoning
    return parsed_json


def run_diagnosis(model=None, symptoms: str = "", vitals: str = "",
                  labs: str = "", history: str = "", age: int = 0,
                  gender: str = "", max_retries: int = 2) -> dict:
    """
    Run the Diagnostic Agent using local DeepSeek-R1 model via Ollama.

    NOTE: The 'model' parameter is kept for API compatibility with the
    existing pipeline but is NOT used — diagnosis runs on local DeepSeek-R1.

    Returns dict with:
        - diagnosis: most likely diagnosis
        - confidence: confidence score (0-100)
        - alternatives: list of alternative diagnoses
        - indicators: key clinical indicators
        - model_used: identifier of the model used (for transparency)
    """

    prompt = f"""Analyze this patient case and provide a differential diagnosis:

PATIENT INFORMATION:
- Age: {age}
- Gender: {gender}
- Presenting Symptoms: {symptoms}
- Vitals: {vitals}
- Lab Results: {labs}
- Medical History: {history}

Perform a systematic differential diagnosis. Consider:
1. Most likely diagnosis given ALL the evidence
2. Risk factors based on age, gender, and history
3. Whether the vitals and labs support or contradict the diagnosis
4. Alternative diagnoses to consider

Return ONLY a JSON object with keys: diagnosis, confidence (0-100), alternatives (list), indicators (string)."""

    raw_response = _call_ollama(prompt, max_retries=max_retries)
    result = _extract_json_from_response(raw_response)

    return {
        "diagnosis": result.get("diagnosis", "Unknown"),
        "confidence": min(max(int(result.get("confidence", 0)), 0), 100),
        "alternatives": result.get("alternatives", []),
        "indicators": result.get("indicators", ""),
        "model_used": f"DeepSeek-R1:8b (Local via Ollama)",
        "local_reasoning": result.get("local_reasoning", "")
    }


def check_ollama_status() -> dict:
    """
    Health check for the Ollama service and model availability.
    Returns status dict for UI display.
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            has_model = any(OLLAMA_MODEL.split(":")[0] in name for name in model_names)
            return {
                "ollama_running": True,
                "model_available": has_model,
                "model_name": OLLAMA_MODEL,
                "available_models": model_names
            }
        return {"ollama_running": False, "model_available": False}
    except Exception:
        return {"ollama_running": False, "model_available": False}
