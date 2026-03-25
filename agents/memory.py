"""
ARIA — Temporal Memory Agent (Phase 2)
Stores and retrieves patient visit history using ChromaDB vector semantic search.
"""

import os
import time
from datetime import datetime
import chromadb

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "chroma_db")

def init_db():
    """No-op for backwards compatibility with seed_demo_data.py"""
    pass

def get_collection():
    """Initialize ChromaDB client and get/create collection."""
    os.makedirs(DB_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(name="patient_visits")
    return collection


def store_visit(patient_id, patient_name, symptoms, diagnosis, confidence, triage_level, urgency_score, notes=""):
    """Save a new visit record into ChromaDB. We embed the symptoms & diagnosis."""
    collection = get_collection()
    
    document = f"Patient presented with symptoms: {symptoms}. Diagnosis was: {diagnosis}."
    # Use time.time() to ensure unique visit IDs even if processing is fast
    visit_id = f"visit_{patient_id}_{int(time.time() * 1000)}"
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    metadata = {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "visit_date": date_str,
        "symptoms": symptoms,
        "diagnosis": diagnosis,
        "confidence": str(confidence),
        "triage_level": triage_level,
        "urgency_score": str(urgency_score),
        "notes": notes
    }
    
    collection.add(
        documents=[document],
        metadatas=[metadata],
        ids=[visit_id]
    )


def get_patient_history(patient_id, current_symptoms=""):
    """Retrieve past visits via semantic search using ChromaDB."""
    collection = get_collection()
    
    results = collection.get(where={"patient_id": patient_id})
    if not results['metadatas']:
        return "No previous visits found for this patient."
        
    if current_symptoms:
        query_text = f"Patient presented with symptoms: {current_symptoms}"
        # We query for the top 5 semantically similar visits for THIS patient
        search_results = collection.query(
            query_texts=[query_text],
            where={"patient_id": patient_id},
            n_results=min(5, len(results['metadatas']))
        )
        
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]
        
        history_lines = []
        for meta, dist in zip(metadatas, distances):
            date = meta.get('visit_date', 'Unknown')
            diagnosis = meta.get('diagnosis', 'Unknown')
            confidence = meta.get('confidence', '0')
            triage = meta.get('triage_level', 'UNKNOWN')
            urgency = meta.get('urgency_score', '0')
            symp = meta.get('symptoms', 'None')
            
            history_lines.append(
                f"• {date} — Diagnosis: {diagnosis} ({confidence}% confidence), "
                f"Triage: {triage} (Urgency: {urgency}/10), Symptoms: {symp} [Semantic Dist: {dist:.2f}]"
            )
        return f"Found {len(history_lines)} semantically relevant past visit(s):\n" + "\n".join(history_lines)
        
    else:
        metadatas = results['metadatas']
        metadatas.sort(key=lambda x: x.get('visit_date', ''))
        
        history_lines = []
        for meta in metadatas:
            date = meta.get('visit_date', 'Unknown')
            diagnosis = meta.get('diagnosis', 'Unknown')
            confidence = meta.get('confidence', '0')
            triage = meta.get('triage_level', 'UNKNOWN')
            urgency = meta.get('urgency_score', '0')
            symp = meta.get('symptoms', 'None')
            
            history_lines.append(
                f"• {date} — Diagnosis: {diagnosis} ({confidence}% confidence), "
                f"Triage: {triage} (Urgency: {urgency}/10), Symptoms: {symp}"
            )
        return f"Found {len(history_lines)} previous visit(s):\n" + "\n".join(history_lines)


def get_patient_timeline(patient_id):
    """Get visits as a list of dicts for the timeline visualization."""
    collection = get_collection()
    results = collection.get(where={"patient_id": patient_id})
    metadatas = results.get('metadatas', [])
    
    metadatas.sort(key=lambda x: x.get('visit_date', ''))
    
    timeline = []
    for meta in metadatas:
        timeline.append({
            "date": meta.get('visit_date', 'Unknown'),
            "diagnosis": meta.get('diagnosis', 'Unknown'),
            "triage_level": meta.get('triage_level', 'UNKNOWN'),
            "urgency_score": meta.get('urgency_score', '0')
        })
    return timeline
