"""
ARIA — Temporal Memory Agent
Stores and retrieves patient visit history using SQLite.
No LLM call needed — pure Python + SQLite.
"""

import sqlite3
import os
from datetime import datetime


# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "patients.db")


def init_db():
    """Create the database and visits table if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT,
            visit_date TEXT NOT NULL,
            symptoms TEXT,
            diagnosis TEXT,
            confidence TEXT,
            triage_level TEXT,
            urgency_score TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


def store_visit(patient_id, patient_name, symptoms, diagnosis, confidence, triage_level, urgency_score, notes=""):
    """Save a new visit record after the pipeline runs."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO visits (patient_id, patient_name, visit_date, symptoms, diagnosis, confidence, triage_level, urgency_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        patient_name,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        symptoms,
        diagnosis,
        str(confidence),
        triage_level,
        str(urgency_score),
        notes
    ))
    conn.commit()
    conn.close()


def get_patient_history(patient_id):
    """Retrieve all past visits for a patient. Returns a formatted string."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT visit_date, symptoms, diagnosis, confidence, triage_level, urgency_score
        FROM visits
        WHERE patient_id = ?
        ORDER BY visit_date ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No previous visits found for this patient."

    history_lines = []
    for row in rows:
        date, symptoms, diagnosis, confidence, triage, urgency = row
        history_lines.append(
            f"• {date} — Diagnosis: {diagnosis} ({confidence}% confidence), "
            f"Triage: {triage} (Urgency: {urgency}/10), Symptoms: {symptoms}"
        )

    return f"Found {len(rows)} previous visit(s):\n" + "\n".join(history_lines)


def get_patient_timeline(patient_id):
    """Get visits as a list of dicts for the timeline visualization."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT visit_date, diagnosis, triage_level, urgency_score
        FROM visits
        WHERE patient_id = ?
        ORDER BY visit_date ASC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()

    timeline = []
    for row in rows:
        timeline.append({
            "date": row[0],
            "diagnosis": row[1],
            "triage_level": row[2],
            "urgency_score": row[3]
        })
    return timeline
