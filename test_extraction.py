import json
from agents.diagnostic import _extract_json_from_response

# Simulated DeepSeek-R1 response
raw_response = """
<think>
The patient is presenting with acute chest pain, radiating to the left arm. 
Vitals indicate high blood pressure (180/110) and tachycardia (110 bpm).
The ECG shows ST-segment elevation.
Most likely diagnosis is Acute Coronary Syndrome (ACS).
I will recommend immediate intervention.
</think>

{
    "diagnosis": "Acute Coronary Syndrome",
    "confidence": 95,
    "alternatives": ["Myocardial Infarction", "Angina"],
    "indicators": "ST-segment elevation, radiating chest pain, hypertensive crisis"
}
"""

print("--- Testing JSON Extraction ---")
result = _extract_json_from_response(raw_response)
print(f"Diagnosis: {result['diagnosis']}")
print(f"Conf: {result['confidence']}")
print(f"Reasoning length: {len(result['local_reasoning'])}")
print(f"Reasoning snippet: {result['local_reasoning'][:50]}...")

assert "Acute Coronary Syndrome" in result['diagnosis']
assert "ST-segment elevation" in result['local_reasoning']
assert "local_reasoning" in result

print("\n--- TEST PASSED: Extraction is robust! ---")
