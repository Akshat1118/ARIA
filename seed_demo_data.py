"""
ARIA — Seed Demo Data
Pre-populates the SQLite database with past visits for demo patients.
Run this once before demo to make the patient timeline work immediately.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.memory import init_db, store_visit


def seed_demo_data():
    """Pre-populate the database with realistic past visit data for demo."""
    init_db()

    demo_visits = [
        # ── Rajesh Kumar (P001) — 2 past visits before the critical cardiac event ──
        {
            "patient_id": "P001",
            "patient_name": "Rajesh Kumar",
            "symptoms": "mild chest discomfort, occasional breathlessness",
            "diagnosis": "Stable Angina",
            "confidence": 72,
            "triage_level": "LOW",
            "urgency_score": 3,
            "notes": "Patient presents with exertional chest discomfort. ECG shows no acute changes. Advised stress test follow-up."
        },
        {
            "patient_id": "P001",
            "patient_name": "Rajesh Kumar",
            "symptoms": "increased chest pain on exertion, fatigue, dizziness",
            "diagnosis": "Unstable Angina",
            "confidence": 78,
            "triage_level": "MODERATE",
            "urgency_score": 6,
            "notes": "Worsening angina pattern noted. Troponin borderline. Started on dual antiplatelet therapy. Cardiology consult recommended."
        },

        # ── Ankit Mehta (P003) — 1 past visit before severe pneumonia ──
        {
            "patient_id": "P003",
            "patient_name": "Ankit Mehta",
            "symptoms": "chronic cough, mild wheeze, fatigue",
            "diagnosis": "COPD Exacerbation",
            "confidence": 80,
            "triage_level": "MODERATE",
            "urgency_score": 5,
            "notes": "Known COPD patient with mild exacerbation. Nebulization given. Oral steroids prescribed. Advised smoking cessation."
        },

        # ── Lakshmi Devi (P006) — 1 past TIA visit before stroke ──
        {
            "patient_id": "P006",
            "patient_name": "Lakshmi Devi",
            "symptoms": "brief episode of right arm numbness, resolved in 20 minutes",
            "diagnosis": "Transient Ischemic Attack (TIA)",
            "confidence": 70,
            "triage_level": "HIGH",
            "urgency_score": 7,
            "notes": "Suspected TIA. Symptoms resolved. CT head normal. Started aspirin. AF noted but anticoagulation not started — needs cardiology review."
        },

        # ── Aisha Khan (P008) — 2 past visits for asthma ──
        {
            "patient_id": "P008",
            "patient_name": "Aisha Khan",
            "symptoms": "mild wheeze after exercise, cough at night",
            "diagnosis": "Exercise-Induced Asthma",
            "confidence": 85,
            "triage_level": "LOW",
            "urgency_score": 2,
            "notes": "Mild asthma symptoms. Peak flow 80% predicted. Inhaler technique reviewed. Controller medication continued."
        },
        {
            "patient_id": "P008",
            "patient_name": "Aisha Khan",
            "symptoms": "increased wheeze, chest tightness, using rescue inhaler 4x daily",
            "diagnosis": "Moderate Asthma Exacerbation",
            "confidence": 82,
            "triage_level": "MODERATE",
            "urgency_score": 5,
            "notes": "Worsening asthma control. Peak flow 60% predicted. Oral prednisolone started. Step-up therapy advised. Follow-up in 48 hours."
        },

        # ── Vikram Singh (P007) — 1 past GI visit ──
        {
            "patient_id": "P007",
            "patient_name": "Vikram Singh",
            "symptoms": "epigastric pain, nausea, dark stools",
            "diagnosis": "Peptic Ulcer Disease",
            "confidence": 75,
            "triage_level": "MODERATE",
            "urgency_score": 5,
            "notes": "Known alcohol use. H. pylori positive. Started triple therapy. Endoscopy scheduled. Advised alcohol cessation."
        },
    ]

    print("🌱 Seeding demo patient data...")
    for visit in demo_visits:
        store_visit(
            patient_id=visit["patient_id"],
            patient_name=visit["patient_name"],
            symptoms=visit["symptoms"],
            diagnosis=visit["diagnosis"],
            confidence=visit["confidence"],
            triage_level=visit["triage_level"],
            urgency_score=visit["urgency_score"],
            notes=visit["notes"]
        )
        print(f"  ✅ {visit['patient_name']} — {visit['diagnosis']}")

    print(f"\n🎉 Seeded {len(demo_visits)} past visits for {len(set(v['patient_id'] for v in demo_visits))} patients!")
    print("Timeline will now show past visits when you run these patients through ARIA.")


if __name__ == "__main__":
    seed_demo_data()
