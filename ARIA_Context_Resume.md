# 🏥 ARIA (Autonomous Real-time Intelligence for Clinical Action) - Developer Context

## 🎯 Current Project Goal
ARIA has evolved from a simple Python prototype into a research-grade **Multi-Agent Clinical Decision Support System** using Google Gemini AI APIs. We recently refactored the sequential backend into a LangGraph parallel state orchestrator.

## 🧱 Architecture Overview (Current State)
The application runs on a Streamlit frontend (`app.py`), orchestrating a multi-agent backend (`agents/graph.py`).

### 1. Agents Built
- **Temporal Memory Agent (`agents/memory.py`)**: Uses local `ChromaDB` (via `sentence-transformers`) for fast semantic search of past patient visits.
- **Diagnostic Agent (`agents/diagnostic.py`)**: Consumes all patient vitals/symptoms/memory to deduce a diagnosis.
- **Uncertainty Layer (`agents/uncertainty.py`)**: Runs the Diagnostic Agent multiple times (currently restricted to **2 runs** to save API quota on Free Tier) to quantify Epistemic Uncertainty via standard deviation plotting.
- **Triage Agent (`agents/triage.py`)**: Assigns a medical Urgency Score (1-10) and Level.
- **Conflict Resolver Agent (`agents/conflict_resolver.py`)**: Detects critical mismatches (e.g., Low Triage for Stroke) and forcefully overwrites the previous triage level by adding a `conflict_audit`.
- **Bias Auditing Agent (`bias/audit.py`)**: Analyzes the Triage/Diagnosis trace to detect whether Demographic Variables (Age, Gender, Income) improperly amplified the result (Cascading Bias Detection).
- **Explainability Agent (`agents/explainability.py`)**: Dims the complex internal traces into a simple, clinician-facing summary.

### 2. Frontend & Export (`app.py` & `report_gen.py`)
- **UI:** A completely customized dark-navy theme. Contains visual queues (Warnings, Confetti) when conflicts are resolved.
- **PDF Report Generation:** Uses `fpdf2` and `matplotlib` to export visually appealing, rich patient PDFs with bar charts showing Confidence, Urgency, and Data Quality. It features a text sanitizer (`safetext`) to strip unsupported Unicode Emojis from confusing the un-extended Helsinki default font in `fpdf2`.
- **Session Caching:** Streamlit now hashes the `patient_data` input. If a user presses the "Run" button repeatedly, it pulls from `st.session_state` rather than burning API calls to prevent 429 Rate Limit exhaustion.

## 🛑 Known Limitations & Mitigation
- **Google Gemini Rate Limits:** The Free Tier restricts us to **15 Requests Per Minute (RPM)**. 
- *Mitigation Active:* A pipeline run consumes 7 calls total right now. Duplicate inputs are heavily cached.

## 🚀 Next Steps Roadmap (For New Session)
1. **Human-in-the-Loop Override Dashboard:** Build a structured workflow where clinicians can review and explicitly approve or override the Agent's Conflict Resolver before final record storing.
2. **Pinecone / Cloud DB Migration:** Migrate away from the local ChromaDB `chroma.sqlite3` environment into a robust, cloud-based vector store (e.g., Pinecone or Weaviate) for scalability.
3. **Real-time Vitals API Integrations:** (Optional) Mock actual websocket data coming from an ICU monitor to feed into ARIA periodically without manual UI inputs.

---
*Note to next Antigravity Session:* Read `app.py`, `agents/graph.py`, and `report_gen.py` individually if you need to recall syntax. Everything is fully functional and committed to GitHub (`https://github.com/Akshat1118/ARIA.git`).
