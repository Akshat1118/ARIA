import sys
import os
import google.generativeai as genai
from agents.graph import run_pipeline

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("gemini-1.5-flash") # free tier

patient_data = {
    "patient_id": "P001",
    "name": "Test",
    "age": 55,
    "gender": "Male",
    "symptoms": "chest pain",
    "vitals": "BP 180/110",
    "labs": "elevated troponin",
    "history": "Hypertension",
    "income_bracket": "Middle"
}

def mock_status_callback(agent_name, status):
    print(f"[{agent_name}] -> {status}")

try:
    res = run_pipeline(model, patient_data, mock_status_callback)
    print("SUCCESS")
    print(res.keys())
except Exception as e:
    import traceback
    traceback.print_exc()
