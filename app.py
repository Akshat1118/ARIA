"""
ARIA — Autonomous Real-time Intelligence for Clinical Action
Main Streamlit Application — Week 2 (Upgraded)
Features: Model selector, confidence gauge, export report, better animations
"""

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

from agents.pipeline import run_pipeline
from agents.memory import get_patient_timeline
from utils.voice import transcribe_audio
from utils.sdg_tracker import get_stats

# ──────────────────────────────────────────
# Load environment
# ──────────────────────────────────────────
load_dotenv()

# ──────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────
st.set_page_config(
    page_title="ARIA — Clinical Decision Support",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────
# Custom CSS — Dark Navy + Electric Blue Theme (Full Visibility Fix)
# ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ══════════════════════════════════════════
       GLOBAL — Force all text to light colors
       ══════════════════════════════════════════ */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3e 50%, #0a1628 100%);
        font-family: 'Inter', sans-serif;
        color: #e6edf3;
    }

    /* Force ALL text white/light */
    .stApp, .stApp * {
        color: #e6edf3;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b3e 0%, #0a1628 100%);
        border-right: 1px solid rgba(56, 139, 253, 0.2);
    }
    section[data-testid="stSidebar"] * { color: #c9d1d9; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 {
        color: #e6edf3 !important;
    }

    /* ── Headers ── */
    h1, h2, h3, h4, h5, h6 {
        color: #e6edf3 !important;
        font-family: 'Inter', sans-serif !important;
    }
    h1 {
        background: linear-gradient(90deg, #58a6ff, #3fb950, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }

    /* ── All text elements ── */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li,
    .stMarkdown td, .stMarkdown th,
    p, span, label, div, li, td, th, dt, dd, figcaption {
        color: #c9d1d9 !important;
    }

    /* ── Captions ── */
    .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] * {
        color: #8b949e !important;
    }

    /* ── Form Labels ── */
    .stTextInput label, .stTextArea label, .stNumberInput label,
    .stSelectbox label, .stCheckbox label, .stRadio label,
    .stSlider label, .stDateInput label, .stTimeInput label,
    .stFileUploader label, .stMultiSelect label,
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {
        color: #c9d1d9 !important;
    }

    /* ── Input Fields ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background-color: #161b33 !important;
        color: #e6edf3 !important;
        border: 1px solid rgba(56, 139, 253, 0.3) !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #484f58 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 12px rgba(56, 139, 253, 0.3) !important;
    }

    /* ── Selectbox / Dropdown ── */
    .stSelectbox > div > div > div,
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] * {
        background-color: #161b33 !important;
        color: #e6edf3 !important;
        border-color: rgba(56, 139, 253, 0.3) !important;
    }
    /* Dropdown menu items */
    [data-baseweb="popover"], [data-baseweb="popover"] *,
    [data-baseweb="menu"], [data-baseweb="menu"] *,
    [role="listbox"], [role="listbox"] *,
    [role="option"], [role="option"] * {
        background-color: #161b33 !important;
        color: #e6edf3 !important;
    }
    [role="option"]:hover {
        background-color: #1a2744 !important;
    }

    /* ── Checkbox / Radio ── */
    .stCheckbox label span, .stRadio label span,
    .stCheckbox > label, .stRadio > label,
    [data-testid="stCheckbox"] *, [data-testid="stRadio"] * {
        color: #c9d1d9 !important;
    }

    /* ── Number Input Buttons ── */
    .stNumberInput button {
        color: #e6edf3 !important;
        background-color: #1a2744 !important;
        border-color: rgba(56, 139, 253, 0.3) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #1a5fb4, #2374d4) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(35, 116, 212, 0.3) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2374d4, #58a6ff) !important;
        box-shadow: 0 6px 25px rgba(56, 139, 253, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Expander ── */
    div[data-testid="stExpander"] {
        background-color: rgba(13, 27, 62, 0.8) !important;
        border: 1px solid rgba(56, 139, 253, 0.15) !important;
        border-radius: 12px !important;
    }
    div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] * {
        color: #c9d1d9 !important;
    }
    div[data-testid="stExpander"] summary svg {
        fill: #58a6ff !important;
    }

    /* ── Alert Messages (warning, error, success, info) ── */
    .stAlert, .stAlert * {
        color: #e6edf3 !important;
    }
    div[data-testid="stNotification"] * {
        color: #e6edf3 !important;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div > div {
        background-color: #58a6ff !important;
    }
    .stProgress [data-testid="stMarkdownContainer"] * {
        color: #c9d1d9 !important;
    }

    /* ── Dataframe / Table ── */
    .stDataFrame, .stDataFrame * {
        color: #e6edf3 !important;
    }
    [data-testid="stDataFrame"] {
        background-color: rgba(13, 27, 62, 0.6) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(13, 27, 62, 0.6) !important;
        border: 1px solid rgba(56, 139, 253, 0.2) !important;
        border-radius: 8px 8px 0 0 !important;
        color: #8b949e !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 139, 253, 0.15) !important;
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 12px; padding: 1rem;
    }
    div[data-testid="stMetric"] label { color: #8b949e !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #58a6ff !important; }

    /* ── Audio Input ── */
    [data-testid="stAudioInput"] *, .stAudioInput * {
        color: #c9d1d9 !important;
    }

    /* ══════════════════════════════════════════
       CUSTOM COMPONENT STYLES
       ══════════════════════════════════════════ */

    /* ── Card Styles ── */
    .aria-card {
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .aria-card:hover {
        border-color: rgba(56, 139, 253, 0.5);
        box-shadow: 0 4px 20px rgba(56, 139, 253, 0.15);
        transform: translateY(-2px);
    }
    .aria-card-critical { border-left: 4px solid #f85149; background: rgba(248, 81, 73, 0.08); }
    .aria-card-high { border-left: 4px solid #d29922; background: rgba(210, 153, 34, 0.08); }
    .aria-card-moderate { border-left: 4px solid #58a6ff; background: rgba(88, 166, 255, 0.08); }
    .aria-card-low { border-left: 4px solid #3fb950; background: rgba(63, 185, 80, 0.08); }

    /* ── Triage Badges ── */
    .triage-badge {
        display: inline-block; padding: 0.4rem 1.2rem; border-radius: 20px;
        font-weight: 700; font-size: 1rem; letter-spacing: 1px;
        animation: badge-pulse 2s infinite;
    }
    @keyframes badge-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    .triage-critical { background: linear-gradient(135deg, #da3633, #f85149); color: white !important; }
    .triage-high { background: linear-gradient(135deg, #9e6a03, #d29922); color: white !important; }
    .triage-moderate { background: linear-gradient(135deg, #1a5fb4, #58a6ff); color: white !important; }
    .triage-low { background: linear-gradient(135deg, #238636, #3fb950); color: white !important; }

    /* ── Agent Status ── */
    .agent-status {
        padding: 0.6rem 1rem; margin: 0.3rem 0; border-radius: 8px;
        font-family: 'Inter', monospace; font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    .agent-running {
        background: rgba(56, 139, 253, 0.1); border-left: 3px solid #58a6ff;
        color: #58a6ff !important; animation: agent-glow 1.5s ease-in-out infinite;
    }
    @keyframes agent-glow {
        0%, 100% { box-shadow: 0 0 5px rgba(56, 139, 253, 0.2); }
        50% { box-shadow: 0 0 15px rgba(56, 139, 253, 0.4); }
    }
    .agent-done {
        background: rgba(63, 185, 80, 0.1); border-left: 3px solid #3fb950; color: #3fb950 !important;
    }

    .bias-pass { color: #3fb950 !important; }
    .bias-flag { color: #f85149 !important; }

    .sdg-bar {
        background: linear-gradient(135deg, rgba(13, 27, 62, 0.8), rgba(35, 116, 212, 0.2));
        border: 1px solid rgba(56, 139, 253, 0.3);
        border-radius: 12px; padding: 1rem 1.5rem; text-align: center;
    }

    .timeline-item {
        display: inline-block; text-align: center; padding: 0.5rem 1rem;
        margin: 0 0.25rem; border-radius: 8px;
        background: rgba(13, 27, 62, 0.6); border: 1px solid rgba(56, 139, 253, 0.2);
        min-width: 120px; transition: all 0.3s ease;
    }
    .timeline-item:hover {
        border-color: rgba(56, 139, 253, 0.5);
        transform: translateY(-2px);
    }

    hr { border-color: rgba(56, 139, 253, 0.2) !important; }

    /* ── Confidence Gauge ── */
    .confidence-ring {
        width: 120px; height: 120px; border-radius: 50%; margin: 0 auto;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.8rem; font-weight: 700; color: #e6edf3 !important;
        position: relative;
    }

    /* ── Critical Alert ── */
    .critical-alert {
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.15), rgba(248, 81, 73, 0.05));
        border: 2px solid #f85149;
        border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
        animation: critical-flash 2s ease-in-out infinite;
    }
    @keyframes critical-flash {
        0%, 100% { border-color: #f85149; }
        50% { border-color: #da3633; box-shadow: 0 0 20px rgba(248, 81, 73, 0.3); }
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #238636, #3fb950) !important;
        color: white !important; border: none !important;
        border-radius: 8px !important;
    }

    /* ── Code blocks ── */
    code, pre, .stCodeBlock { color: #e6edf3 !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0e27; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #484f58; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────
def get_triage_color(level):
    colors = {
        "CRITICAL": ("#f85149", "triage-critical"),
        "HIGH": ("#d29922", "triage-high"),
        "MODERATE": ("#58a6ff", "triage-moderate"),
        "LOW": ("#3fb950", "triage-low")
    }
    return colors.get(level, ("#8b949e", "triage-moderate"))


def get_card_class(level):
    return f"aria-card aria-card-{level.lower()}"


def get_confidence_color(confidence):
    if confidence >= 80:
        return "#3fb950"
    elif confidence >= 60:
        return "#58a6ff"
    elif confidence >= 40:
        return "#d29922"
    else:
        return "#f85149"


def generate_report(patient_data, results):
    """Generate a downloadable text report of the ARIA analysis."""
    report = f"""
{'='*60}
  ARIA — Clinical Decision Support Report
  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

PATIENT INFORMATION
{'─'*40}
  Name:           {patient_data.get('name', 'N/A')}
  Patient ID:     {patient_data.get('patient_id', 'N/A')}
  Age:            {patient_data.get('age', 'N/A')}
  Gender:         {patient_data.get('gender', 'N/A')}
  Symptoms:       {patient_data.get('symptoms', 'N/A')}
  Vitals:         {patient_data.get('vitals', 'N/A')}
  Lab Results:    {patient_data.get('labs', 'N/A')}
  Medical History:{patient_data.get('history', 'N/A')}

DIAGNOSIS
{'─'*40}
  Primary:        {results['diagnosis']['diagnosis']}
  Confidence:     {results['diagnosis']['confidence']}%
  Alternatives:   {', '.join(results['diagnosis']['alternatives'])}
  Key Indicators: {results['diagnosis']['indicators']}

TRIAGE ASSESSMENT
{'─'*40}
  Level:          {results['triage']['triage_level']}
  Urgency Score:  {results['triage']['urgency_score']}/10
  Reasoning:      {results['triage']['reasoning']}

DOCTOR SUMMARY
{'─'*40}
  {results['doctor_summary']}

FAIRNESS AUDIT
{'─'*40}
  Gender Bias:    {results['bias_report']['gender_bias']['status']}
                  {results['bias_report']['gender_bias']['detail']}
  Age Bias:       {results['bias_report']['age_bias']['status']}
                  {results['bias_report']['age_bias']['detail']}
  Income Bias:    {results['bias_report']['income_bias']['status']}
                  {results['bias_report']['income_bias']['detail']}

PATIENT HISTORY
{'─'*40}
  {results['memory_summary']}

{'='*60}
  DISCLAIMER: This is an AI-assisted analysis for clinical
  decision support only. Not a substitute for clinical judgment.
{'='*60}
"""
    return report


# ──────────────────────────────────────────
# Sidebar — Patient Input + Settings
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 ARIA")
    st.markdown("*Autonomous Real-time Intelligence for Clinical Action*")
    st.markdown("---")

    # ── Model Selector ──
    st.markdown("### ⚙️ Settings")
    model_options = {
        "Gemini 2.5 Flash (Recommended)": "gemini-2.5-flash",
        "Gemini 2.0 Flash": "gemini-2.0-flash",
        "Gemini 2.0 Flash Lite": "gemini-2.0-flash-lite",
        "Gemini 2.5 Pro (Slower, Smarter)": "gemini-2.5-pro",
    }
    selected_model_name = st.selectbox("🤖 AI Model", list(model_options.keys()))
    selected_model = model_options[selected_model_name]
    st.caption(f"Using: `{selected_model}`")

    st.markdown("---")

    # ── Voice Input ──
    st.markdown("### 🎙️ Voice Input")
    audio_input = st.audio_input("Record patient details", key="voice_input")

    voice_text = ""
    if audio_input is not None:
        try:
            voice_text = transcribe_audio(audio_input.getvalue())
            st.success(f"📝 Transcribed: {voice_text[:100]}...")
        except Exception as e:
            st.error(f"Transcription error: {e}")

    st.markdown("---")
    st.markdown("### 📋 Patient Information")

    # Load sample patients
    sample_csv = os.path.join(os.path.dirname(__file__), "data", "sample_patients.csv")
    sample_patients = None
    if os.path.exists(sample_csv):
        sample_patients = pd.read_csv(sample_csv)

    use_sample = st.checkbox("📂 Load sample patient", value=False)

    selected_sample = None
    if use_sample and sample_patients is not None:
        sample_options = {f"{row['name']} (Age {row['age']}, {row['gender']})": idx
                         for idx, row in sample_patients.iterrows()}
        selected_name = st.selectbox("Choose patient", list(sample_options.keys()))
        selected_sample = sample_patients.iloc[sample_options[selected_name]]

    default_vals = {
        "patient_id": selected_sample["patient_id"] if selected_sample is not None else "",
        "name": selected_sample["name"] if selected_sample is not None else "",
        "age": int(selected_sample["age"]) if selected_sample is not None else 30,
        "gender": selected_sample["gender"] if selected_sample is not None else "Male",
        "symptoms": selected_sample["symptoms"] if selected_sample is not None else (voice_text if voice_text else ""),
        "vitals": selected_sample["vitals"] if selected_sample is not None else "",
        "labs": selected_sample["labs"] if selected_sample is not None else "",
        "history": selected_sample["history"] if selected_sample is not None else "",
        "income_bracket": selected_sample["income_bracket"] if selected_sample is not None else "Middle",
    }

    patient_id = st.text_input("Patient ID", value=default_vals["patient_id"], placeholder="e.g. P001")
    patient_name = st.text_input("Patient Name", value=default_vals["name"], placeholder="e.g. Rajesh Kumar")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=default_vals["age"])
    with col2:
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                              index=["Male", "Female", "Other"].index(default_vals["gender"]) if default_vals["gender"] in ["Male", "Female", "Other"] else 0)

    symptoms = st.text_area("Symptoms", value=default_vals["symptoms"], height=80,
                            placeholder="e.g. chest pain, shortness of breath, sweating")
    vitals = st.text_input("Vitals", value=default_vals["vitals"],
                           placeholder="e.g. BP 180/110, HR 110, SpO2 92%")
    labs = st.text_area("Lab Results", value=default_vals["labs"], height=68,
                        placeholder="e.g. Troponin elevated, BNP 450")
    history = st.text_input("Medical History", value=default_vals["history"],
                            placeholder="e.g. Hypertension, Diabetes")
    income = st.selectbox("Income Bracket", ["Low", "Middle", "High"],
                          index=["Low", "Middle", "High"].index(default_vals["income_bracket"]) if default_vals["income_bracket"] in ["Low", "Middle", "High"] else 1)

    st.markdown("---")
    run_button = st.button("🚀 Run ARIA Pipeline", use_container_width=True, type="primary")


# ──────────────────────────────────────────
# Main Area — Header
# ──────────────────────────────────────────
st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.2rem;">🏥 ARIA</h1>
        <p style="color: #8b949e; font-size: 1.1rem; margin-top: 0;">
            Autonomous Real-time Intelligence for Clinical Action
        </p>
        <p style="color: #484f58; font-size: 0.85rem;">
            Powered by Google Gemini AI &nbsp;•&nbsp; Multi-Agent Clinical Decision Support
        </p>
    </div>
""", unsafe_allow_html=True)

# ── SDG Impact Counter ──
sdg_stats = get_stats()
sdg_col1, sdg_col2, sdg_col3 = st.columns([1, 2, 1])
with sdg_col2:
    st.markdown(f"""
        <div class="sdg-bar">
            🌍 <strong>SDG 3 Impact Dashboard</strong> &nbsp;&nbsp;|&nbsp;&nbsp;
            Patients Triaged Fairly: <strong style="color: #3fb950;">{sdg_stats.get('patients_triaged', 0)}</strong>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Bias Cases Flagged: <strong style="color: #f85149;">{sdg_stats.get('bias_flagged', 0)}</strong>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Run Pipeline
# ──────────────────────────────────────────
if run_button:
    if not symptoms.strip():
        st.error("⚠️ Please enter patient symptoms before running the pipeline.")
        st.stop()

    # ── Edge case warnings (non-blocking) ──
    missing_fields = []
    if not vitals.strip():
        missing_fields.append("Vitals")
    if not labs.strip():
        missing_fields.append("Lab Results")
    if not history.strip():
        missing_fields.append("Medical History")
    if missing_fields:
        st.warning(f"⚠️ Missing: **{', '.join(missing_fields)}** — ARIA will still run but results may be less accurate.")

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "PASTE-YOUR-GEMINI-KEY-HERE":
        st.error("⚠️ Please add your Gemini API key in the `.env` file. Get it free at https://aistudio.google.com/apikey")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(selected_model)

    patient_data = {
        "patient_id": patient_id or f"P-{int(time.time())}",
        "name": patient_name or "Unknown Patient",
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "vitals": vitals or "Not provided",
        "labs": labs or "Not provided",
        "history": history or "Not provided",
        "income_bracket": income
    }

    # ── Live Agent Thinking Screen ──
    st.markdown("### 🧠 Agent Pipeline")
    st.caption(f"Model: `{selected_model}` — Retry enabled (3 attempts with backoff)")

    agent_statuses = {}
    status_container = st.container()

    agent_icons = {
        "Temporal Memory Agent": "🧠",
        "Diagnostic Agent": "🔬",
        "Triage Agent": "🚨",
        "Bias Monitor": "⚖️",
        "Explainability Agent": "💡"
    }
    agent_actions = {
        "Temporal Memory Agent": "scanning patient history...",
        "Diagnostic Agent": "analyzing symptoms & generating diagnosis...",
        "Triage Agent": "scoring clinical urgency...",
        "Bias Monitor": "auditing for demographic bias...",
        "Explainability Agent": "writing doctor-friendly summary..."
    }

    with status_container:
        progress_placeholder = st.empty()
        progress_bar = st.progress(0, text="Initializing agents...")

    def update_agent_status(agent_name, status):
        agent_statuses[agent_name] = status
        # Update progress bar
        done_count = sum(1 for v in agent_statuses.values() if v == "done")
        progress = done_count / len(agent_icons)
        progress_bar.progress(progress, text=f"Processing... ({done_count}/{len(agent_icons)} agents complete)")
        # Update status lines
        lines = []
        for name in agent_icons:
            icon = agent_icons[name]
            if name in agent_statuses:
                if agent_statuses[name] == "done":
                    lines.append(f'<div class="agent-status agent-done">{icon} {name} — ✅ Complete</div>')
                else:
                    lines.append(f'<div class="agent-status agent-running">{icon} {name} — ⏳ {agent_actions.get(name, "processing...")}</div>')
            else:
                lines.append(f'<div class="agent-status" style="color: #484f58; border-left: 3px solid #30363d; padding: 0.6rem 1rem; margin: 0.3rem 0; border-radius: 8px;">{icon} {name} — ⬜ Waiting</div>')
        progress_placeholder.markdown("".join(lines), unsafe_allow_html=True)

    update_agent_status("__init__", "")
    del agent_statuses["__init__"]

    try:
        results = run_pipeline(model, patient_data, status_callback=update_agent_status)
        progress_bar.progress(1.0, text="✅ All agents complete!")
        st.session_state["results"] = results
        st.session_state["patient_data"] = patient_data
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            st.error(f"⚠️ **Rate limit hit** even after retries. Your Gemini free tier daily quota is exhausted.\n\n"
                     f"**Options:**\n"
                     f"- Wait for quota reset (midnight US Pacific / ~1:30 PM IST)\n"
                     f"- Try a different model from the dropdown\n"
                     f"- Use a new API key from a different Google account")
        else:
            st.error(f"❌ Pipeline error: {error_msg}")
        st.stop()

# ──────────────────────────────────────────
# Display Results (from session state)
# ──────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    patient_data = st.session_state["patient_data"]

    st.markdown("---")

    # ── CRITICAL Alert Banner + Sound ──
    triage_level = results["triage"]["triage_level"]
    if triage_level == "CRITICAL":
        st.markdown(f"""
            <div class="critical-alert" style="text-align: center;">
                <span style="font-size: 1.5rem;">🚨</span>
                <strong style="color: #f85149; font-size: 1.2rem;"> CRITICAL ALERT — Immediate attention required</strong>
                <span style="font-size: 1.5rem;">🚨</span>
                <p style="color: #f85149; margin: 0.3rem 0 0 0;">{results['triage']['reasoning']}</p>
            </div>
            <script>
                // Play 3-beep alert sound using Web Audio API
                (function() {{
                    try {{
                        const ctx = new (window.AudioContext || window.webkitAudioContext)();
                        function beep(freq, startTime, duration) {{
                            const osc = ctx.createOscillator();
                            const gain = ctx.createGain();
                            osc.connect(gain);
                            gain.connect(ctx.destination);
                            osc.frequency.value = freq;
                            osc.type = 'sine';
                            gain.gain.setValueAtTime(0.3, startTime);
                            gain.gain.exponentialRampToValueAtTime(0.01, startTime + duration);
                            osc.start(startTime);
                            osc.stop(startTime + duration);
                        }}
                        const now = ctx.currentTime;
                        beep(880, now, 0.2);
                        beep(880, now + 0.3, 0.2);
                        beep(1100, now + 0.6, 0.4);
                    }} catch(e) {{}}
                }})();
            </script>
        """, unsafe_allow_html=True)
    elif triage_level == "HIGH":
        st.markdown(f"""
            <div style="background: rgba(210, 153, 34, 0.1); border: 2px solid #d29922; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; text-align: center;">
                <strong style="color: #d29922; font-size: 1.1rem;">⚠️ HIGH PRIORITY — Attend within 30 minutes</strong>
                <p style="color: #d29922; margin: 0.3rem 0 0 0; font-size: 0.9rem;">{results['triage']['reasoning']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📊 Results Dashboard")
    st.caption(f"Patient: **{patient_data.get('name', 'Unknown')}** (ID: {patient_data.get('patient_id', 'N/A')}) — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ── Row 1: Diagnosis + Confidence Gauge + Triage ──
    res_col1, res_col2, res_col3 = st.columns([3, 1.5, 2.5])

    with res_col1:
        diag = results["diagnosis"]
        card_class = get_card_class(triage_level)
        st.markdown(f"""
            <div class="{card_class}">
                <h4 style="margin: 0 0 0.5rem 0;">🔬 Diagnosis</h4>
                <p style="font-size: 1.3rem; color: #e6edf3; font-weight: 600; margin: 0;">
                    {diag['diagnosis']}
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0.5rem 0 0.3rem 0;">
                    <strong>Key Indicators:</strong> {diag['indicators']}
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">
                    <strong>Alternatives:</strong> {', '.join(diag['alternatives'])}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with res_col2:
        conf = diag['confidence']
        conf_color = get_confidence_color(conf)
        # SVG confidence ring
        radius = 45
        circumference = 2 * 3.14159 * radius
        offset = circumference - (conf / 100) * circumference
        st.markdown(f"""
            <div class="aria-card" style="text-align: center; padding: 1rem;">
                <h4 style="margin: 0 0 0.5rem 0;">📊 Confidence</h4>
                <svg width="110" height="110" viewBox="0 0 110 110" style="margin: 0 auto; display: block;">
                    <circle cx="55" cy="55" r="{radius}" fill="none" stroke="#1a1f36" stroke-width="8"/>
                    <circle cx="55" cy="55" r="{radius}" fill="none" stroke="{conf_color}" stroke-width="8"
                        stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                        stroke-linecap="round" transform="rotate(-90 55 55)"
                        style="transition: stroke-dashoffset 1s ease;"/>
                    <text x="55" y="55" text-anchor="middle" dy="0.35em"
                        fill="{conf_color}" font-size="24" font-weight="700" font-family="Inter">{conf}%</text>
                </svg>
            </div>
        """, unsafe_allow_html=True)

    with res_col3:
        triage = results["triage"]
        color, badge_class = get_triage_color(triage["triage_level"])
        st.markdown(f"""
            <div class="{card_class}" style="text-align: center;">
                <h4 style="margin: 0 0 1rem 0;">🚨 Triage Level</h4>
                <div class="triage-badge {badge_class}" style="font-size: 1.3rem;">
                    {triage['triage_level']}
                </div>
                <p style="color: {color}; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;">
                    {triage['urgency_score']}/10
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">
                    {triage['reasoning']}
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 2: Doctor Summary ──
    st.markdown(f"""
        <div class="aria-card">
            <h4 style="margin: 0 0 0.5rem 0;">💡 Doctor Summary</h4>
            <p style="color: #e6edf3; font-size: 1.05rem; line-height: 1.6;">
                {results['doctor_summary']}
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 3: Bias Report + Timeline ──
    bias_col, timeline_col = st.columns([1, 1])

    with bias_col:
        bias = results["bias_report"]
        st.markdown(f"""
            <div class="aria-card">
                <h4 style="margin: 0 0 0.8rem 0;">⚖️ Fairness Audit</h4>
                <p class="{'bias-flag' if '⚠️' in bias['gender_bias']['status'] else 'bias-pass'}" style="margin: 0.3rem 0;">
                    <strong>Gender Bias:</strong> {bias['gender_bias']['status']}<br>
                    <span style="color: #8b949e; font-size: 0.8rem;">{bias['gender_bias']['detail']}</span>
                </p>
                <p class="{'bias-flag' if '⚠️' in bias['age_bias']['status'] else 'bias-pass'}" style="margin: 0.3rem 0;">
                    <strong>Age Bias:</strong> {bias['age_bias']['status']}<br>
                    <span style="color: #8b949e; font-size: 0.8rem;">{bias['age_bias']['detail']}</span>
                </p>
                <p class="{'bias-flag' if '⚠️' in bias['income_bias']['status'] else 'bias-pass'}" style="margin: 0.3rem 0;">
                    <strong>Income Bias:</strong> {bias['income_bias']['status']}<br>
                    <span style="color: #8b949e; font-size: 0.8rem;">{bias['income_bias']['detail']}</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

    with timeline_col:
        timeline = get_patient_timeline(patient_data["patient_id"])
        st.markdown('<div class="aria-card"><h4 style="margin: 0 0 0.8rem 0;">📅 Patient Timeline</h4>', unsafe_allow_html=True)

        if len(timeline) <= 1:
            st.markdown('<p style="color: #8b949e;">First recorded visit for this patient.</p>', unsafe_allow_html=True)
        else:
            timeline_html = '<div style="display: flex; align-items: center; overflow-x: auto; gap: 0.25rem; padding: 0.5rem 0;">'
            for i, visit in enumerate(timeline):
                level = visit["triage_level"]
                vcolor, _ = get_triage_color(level)
                timeline_html += f"""
                    <div class="timeline-item" style="border-top: 3px solid {vcolor};">
                        <div style="color: #8b949e; font-size: 0.75rem;">{visit['date']}</div>
                        <div style="color: #e6edf3; font-size: 0.85rem; font-weight: 600;">{visit['diagnosis'][:20]}</div>
                        <div style="color: {vcolor}; font-size: 0.75rem; font-weight: 700;">{level}</div>
                    </div>
                """
                if i < len(timeline) - 1:
                    timeline_html += '<span style="color: #30363d; font-size: 1.2rem;">──</span>'
            timeline_html += '</div>'
            st.markdown(timeline_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 4: Memory + Export ──
    mem_col, export_col = st.columns([2, 1])

    with mem_col:
        with st.expander("🧠 Temporal Memory — Past Visit Data"):
            st.markdown(f"```\n{results['memory_summary']}\n```")

    with export_col:
        report_text = generate_report(patient_data, results)
        st.download_button(
            label="📄 Download Report",
            data=report_text,
            file_name=f"ARIA_Report_{patient_data.get('patient_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # ── New Patient Button ──
    st.markdown("")
    if st.button("🔄 Analyze New Patient", use_container_width=True):
        del st.session_state["results"]
        del st.session_state["patient_data"]
        st.rerun()

# ──────────────────────────────────────────
# Default State
# ──────────────────────────────────────────
else:
    st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem;">
            <p style="font-size: 3rem; margin: 0;">🩺</p>
            <h3 style="color: #8b949e; font-weight: 400;">Enter patient details in the sidebar and click
                <span style="color: #58a6ff; font-weight: 600;">Run ARIA Pipeline</span>
            </h3>
            <p style="color: #484f58;">
                ARIA will analyze symptoms, diagnose, triage, check for bias, and provide a clear summary — all in seconds.
            </p>
        </div>
    """, unsafe_allow_html=True)

    sample_csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_patients.csv")
    if os.path.exists(sample_csv_path):
        with st.expander("📂 Preview Sample Patients"):
            df = pd.read_csv(sample_csv_path)
            st.dataframe(df[["patient_id", "name", "age", "gender", "symptoms"]],
                         use_container_width=True, hide_index=True)
