"""
ARIA — Autonomous Real-time Intelligence for Clinical Action
Main Streamlit Application
Uses Google Gemini API (free tier)
"""

import streamlit as st
import pandas as pd
import os
import time
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
# Custom CSS — Dark Navy + Electric Blue Theme
# ──────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global Theme ── */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3e 50%, #0a1628 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b3e 0%, #0a1628 100%);
        border-right: 1px solid rgba(56, 139, 253, 0.2);
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #c9d1d9;
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

    /* ── Text ── */
    .stMarkdown, p, span, label {
        color: #c9d1d9;
    }

    /* ── Input Fields ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #161b33 !important;
        color: #e6edf3 !important;
        border: 1px solid rgba(56, 139, 253, 0.3) !important;
        border-radius: 8px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 12px rgba(56, 139, 253, 0.3) !important;
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

    /* ── Cards / Containers ── */
    div[data-testid="stExpander"] {
        background-color: rgba(13, 27, 62, 0.8) !important;
        border: 1px solid rgba(56, 139, 253, 0.15) !important;
        border-radius: 12px !important;
    }

    /* ── Metric Cards ── */
    div[data-testid="stMetric"] {
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
    }

    /* ── Custom Card Styles ── */
    .aria-card {
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    .aria-card-critical {
        border-left: 4px solid #f85149;
        background: rgba(248, 81, 73, 0.08);
    }
    .aria-card-high {
        border-left: 4px solid #d29922;
        background: rgba(210, 153, 34, 0.08);
    }
    .aria-card-moderate {
        border-left: 4px solid #58a6ff;
        background: rgba(88, 166, 255, 0.08);
    }
    .aria-card-low {
        border-left: 4px solid #3fb950;
        background: rgba(63, 185, 80, 0.08);
    }

    /* ── Triage Badges ── */
    .triage-badge {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 1px;
    }
    .triage-critical { background: linear-gradient(135deg, #da3633, #f85149); color: white; }
    .triage-high { background: linear-gradient(135deg, #9e6a03, #d29922); color: white; }
    .triage-moderate { background: linear-gradient(135deg, #1a5fb4, #58a6ff); color: white; }
    .triage-low { background: linear-gradient(135deg, #238636, #3fb950); color: white; }

    /* ── Agent Status ── */
    .agent-status {
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 8px;
        font-family: 'Inter', monospace;
        font-size: 0.9rem;
    }
    .agent-running {
        background: rgba(56, 139, 253, 0.1);
        border-left: 3px solid #58a6ff;
        color: #58a6ff;
    }
    .agent-done {
        background: rgba(63, 185, 80, 0.1);
        border-left: 3px solid #3fb950;
        color: #3fb950;
    }

    /* ── Bias Report ── */
    .bias-pass { color: #3fb950; }
    .bias-flag { color: #f85149; }

    /* ── SDG Counter ── */
    .sdg-bar {
        background: linear-gradient(135deg, rgba(13, 27, 62, 0.8), rgba(35, 116, 212, 0.2));
        border: 1px solid rgba(56, 139, 253, 0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
    }

    /* ── Timeline ── */
    .timeline-item {
        display: inline-block;
        text-align: center;
        padding: 0.5rem 1rem;
        margin: 0 0.25rem;
        border-radius: 8px;
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        min-width: 120px;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(56, 139, 253, 0.2) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 8px 8px 0 0;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(56, 139, 253, 0.15) !important;
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }
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


# ──────────────────────────────────────────
# Sidebar — Patient Input
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 ARIA")
    st.markdown("*Autonomous Real-time Intelligence for Clinical Action*")
    st.markdown("---")

    # Voice Input
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

    # Load sample patients for quick demo
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

    # Patient form
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

# ── SDG Impact Counter — Always visible ──
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
    # Validate inputs
    if not symptoms.strip():
        st.error("⚠️ Please enter patient symptoms before running the pipeline.")
        st.stop()

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "PASTE-YOUR-GEMINI-KEY-HERE":
        st.error("⚠️ Please add your Gemini API key in the `.env` file. Get it free at https://aistudio.google.com/apikey")
        st.stop()

    # Configure Gemini
    genai.configure(api_key=api_key)
    # Using gemini-2.5-flash (newest model, separate rate limits)
    model = genai.GenerativeModel("gemini-2.5-flash")

    patient_data = {
        "patient_id": patient_id or f"P-{int(time.time())}",
        "name": patient_name or "Unknown Patient",
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "vitals": vitals,
        "labs": labs,
        "history": history,
        "income_bracket": income
    }

    # ── Live Agent Thinking Screen ──
    st.markdown("### 🧠 Agent Pipeline")

    agent_statuses = {}
    status_container = st.container()

    agent_icons = {
        "Temporal Memory Agent": "🧠",
        "Diagnostic Agent": "🔵",
        "Triage Agent": "🟢",
        "Bias Monitor": "⚖️",
        "Explainability Agent": "💡"
    }

    agent_actions = {
        "Temporal Memory Agent": "scanning patient history...",
        "Diagnostic Agent": "analyzing symptoms...",
        "Triage Agent": "scoring urgency...",
        "Bias Monitor": "auditing for bias...",
        "Explainability Agent": "writing doctor summary..."
    }

    # Show initial status
    with status_container:
        progress_placeholder = st.empty()

    def update_agent_status(agent_name, status):
        agent_statuses[agent_name] = status
        lines = []
        for name in agent_icons:
            icon = agent_icons[name]
            if name in agent_statuses:
                if agent_statuses[name] == "done":
                    lines.append(f'<div class="agent-status agent-done">{icon} {name} — ✅ Complete</div>')
                else:
                    lines.append(f'<div class="agent-status agent-running">{icon} {name} — ⏳ {agent_actions.get(name, "processing...")}</div>')
            else:
                lines.append(f'<div class="agent-status" style="color: #484f58; border-left: 3px solid #30363d; padding: 0.5rem 1rem; margin: 0.3rem 0; border-radius: 8px;">{icon} {name} — ⬜ Waiting</div>')
        progress_placeholder.markdown("".join(lines), unsafe_allow_html=True)

    # Initialize all as waiting
    update_agent_status("__init__", "")
    del agent_statuses["__init__"]

    # Run the pipeline!
    try:
        results = run_pipeline(model, patient_data, status_callback=update_agent_status)
        # Store results in session state so they persist
        st.session_state["results"] = results
        st.session_state["patient_data"] = patient_data
    except Exception as e:
        st.error(f"❌ Pipeline error: {str(e)}")
        st.stop()

# ──────────────────────────────────────────
# Display Results (from session state)
# ──────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    patient_data = st.session_state["patient_data"]

    st.markdown("---")
    st.markdown("### 📊 Results Dashboard")

    # ── Row 1: Diagnosis + Triage ──
    res_col1, res_col2 = st.columns([3, 2])

    with res_col1:
        diag = results["diagnosis"]
        card_class = get_card_class(results["triage"]["triage_level"])
        st.markdown(f"""
            <div class="{card_class}">
                <h4 style="margin: 0 0 0.5rem 0;">🔬 Diagnosis</h4>
                <p style="font-size: 1.3rem; color: #e6edf3; font-weight: 600; margin: 0;">
                    {diag['diagnosis']}
                </p>
                <p style="color: #58a6ff; font-size: 1rem; margin: 0.3rem 0;">
                    Confidence: <strong>{diag['confidence']}%</strong>
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
                color, _ = get_triage_color(level)
                timeline_html += f"""
                    <div class="timeline-item" style="border-top: 3px solid {color};">
                        <div style="color: #8b949e; font-size: 0.75rem;">{visit['date']}</div>
                        <div style="color: #e6edf3; font-size: 0.85rem; font-weight: 600;">{visit['diagnosis'][:20]}</div>
                        <div style="color: {color}; font-size: 0.75rem; font-weight: 700;">{level}</div>
                    </div>
                """
                if i < len(timeline) - 1:
                    timeline_html += '<span style="color: #30363d; font-size: 1.2rem;">──</span>'
            timeline_html += '</div>'
            st.markdown(timeline_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 4: Memory Context ──
    with st.expander("🧠 Temporal Memory — Past Visit Data"):
        st.markdown(f"```\n{results['memory_summary']}\n```")

    # Clear results button
    if st.button("🔄 New Patient", use_container_width=True):
        del st.session_state["results"]
        del st.session_state["patient_data"]
        st.rerun()

# ──────────────────────────────────────────
# Default State — No pipeline run yet
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

    # Show sample data preview
    sample_csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_patients.csv")
    if os.path.exists(sample_csv_path):
        with st.expander("📂 Preview Sample Patients"):
            df = pd.read_csv(sample_csv_path)
            st.dataframe(df[["patient_id", "name", "age", "gender", "symptoms"]],
                         use_container_width=True, hide_index=True)
