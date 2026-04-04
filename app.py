"""
ARIA — Autonomous Real-time Intelligence for Clinical Action
Main Streamlit Application — Week 2 (Upgraded)
Features: Model selector, confidence gauge, export report, better animations
"""

import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime
from report_gen import generate_pdf_report
from sarvam_translate import translate_patient_report, SUPPORTED_LANGUAGES
import requests
from streamlit_lottie import st_lottie

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass  # In production (Streamlit Cloud), env vars are set in the UI, so dotenv isn't needed.
import google.generativeai as genai

# Explicitly configure using the env variable so we immediately catch any `.env` file updates
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

from agents.graph import run_pipeline
from agents.memory import get_patient_timeline
from utils.voice import transcribe_audio
from utils.sdg_tracker import get_stats


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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ══════════════════════════════════════════
       GLOBAL — Clear Light Theme (Premium)
       ══════════════════════════════════════════ */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }

    /* Force default text to dark slate */
    .stApp, .stApp * {
        color: #0f172a;
    }
    .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #334155 !important;
        line-height: 1.6;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2 {
        color: #0f172a !important;
        font-weight: 800 !important;
    }

    /* ── Headers ── */
    h1, h2, h3, h4, h5, h6 {
        color: #0f172a !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    h1 {
        background: linear-gradient(90deg, #2563eb, #0284c7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* ── Form Labels & Small Text ── */
    .stCaption, [data-testid="stCaptionContainer"] *, label {
        color: #64748b !important;
    }
    label { font-weight: 500 !important; }

    /* ── Input Fields ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }

    /* Dropdown Menus */
    [data-baseweb="popover"] *, [role="listbox"] * { color: #0f172a !important; }
    [role="option"]:hover { background-color: #f1f5f9 !important; }

    /* ── Buttons ── */
    .stButton > button {
        background: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
    }
    .stButton > button:hover {
        background: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3) !important;
    }

    /* ══════════════════════════════════════════
       CUSTOM COMPONENT STYLES
       ══════════════════════════════════════════ */

    /* ── Beautiful Premium Cards ── */
    .aria-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .aria-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .aria-card-critical { border-top: 4px solid #ef4444; }
    .aria-card-high { border-top: 4px solid #f59e0b; }
    .aria-card-moderate { border-top: 4px solid #3b82f6; }
    .aria-card-low { border-top: 4px solid #10b981; }

    /* ── Triage Badges (Soft Pastel with Vibrant Text) ── */
    .triage-badge {
        display: inline-block; padding: 0.35rem 1.2rem; border-radius: 9999px;
        font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px; text-transform: uppercase;
    }
    .triage-critical { background: #fee2e2; color: #b91c1c !important; border: 1px solid #fca5a5; }
    .triage-high { background: #fef3c7; color: #b45309 !important; border: 1px solid #fcd34d; }
    .triage-moderate { background: #dbeafe; color: #1d4ed8 !important; border: 1px solid #bfdbfe; }
    .triage-low { background: #d1fae5; color: #047857 !important; border: 1px solid #a7f3d0; }

    /* ── Agent Status Indicators ── */
    .agent-status {
        padding: 0.75rem 1rem; margin: 0.4rem 0; border-radius: 8px;
        font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 500;
        background: #ffffff; border: 1px solid #e2e8f0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }
    .agent-running {
        border-left: 4px solid #3b82f6; color: #1e40af !important; background: #eff6ff;
    }
    .agent-done {
        border-left: 4px solid #10b981; color: #065f46 !important; background: #f0fdf4;
    }

    .bias-pass { color: #059669 !important; font-weight: 600; }
    .bias-flag { color: #dc2626 !important; font-weight: 600; }

    /* ── Dashboard Top Bars ── */
    .sdg-bar {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px; padding: 1rem 1.5rem; text-align: center;
        box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
    }

    /* ── Timeline ── */
    .timeline-item {
        display: inline-block; text-align: center; padding: 0.5rem 1rem;
        margin: 0 0.25rem; border-radius: 8px;
        background: #ffffff; border: 1px solid #e2e8f0;
        min-width: 120px; transition: all 0.3s ease;
    }
    .timeline-item:hover { border-color: #cbd5e1; transform: translateY(-2px); }

    /* ── Critical Alerts ── */
    .critical-alert {
        background: #fef2f2; border: 2px solid #ef4444; border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
    }

    /* ── General UI Wrappers ── */
    div[data-testid="stExpander"] { background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 12px !important; }
    div[data-testid="stExpander"] * { color: #334155 !important; }
    [data-testid="stDataFrame"] { background-color: #ffffff !important; border-radius: 12px; }
    .stAlert { border-radius: 12px !important; }

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

@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None


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
    """Generate a downloadable markdown report of the ARIA Multi-Agent analysis."""
    
    # Extract new uncertainty fields if available
    epistemic_unc = results['diagnosis'].get('epistemic_uncertainty', 'N/A')
    data_qual = results['diagnosis'].get('data_quality_score', 'N/A')
    
    # Extract conflict reporting if available
    conflict_detected = results.get('conflict', False)
    conflict_text = f"⚔️ **CONFLICT DETECTED & RESOLVED**\n{chr(10).join(results['triage'].get('conflict_audit', ['Triage adjusted by Conflict Resolver Agent.']))}" if conflict_detected else "✅ No conflicts between Diagnostic & Triage agents."
    
    # Extract cascade bias reporting
    cascade_flag = results['bias_report'].get('cascading_amplification', False)
    cascade_text = "⚠️ **CASCADING BIAS FLAG: Bias amplified across the pipeline!**" if cascade_flag else "✅ No cascading amplification detected."
    
    report = f"""# ARIA — Clinical Decision Support Report
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 🧑‍⚕️ PATIENT INFORMATION
* **Name:** {patient_data.get('name', 'N/A')}
* **Patient ID:** {patient_data.get('patient_id', 'N/A')}
* **Age:** {patient_data.get('age', 'N/A')}
* **Gender:** {patient_data.get('gender', 'N/A')}
* **Symptoms:** {patient_data.get('symptoms', 'N/A')}
* **Vitals:** {patient_data.get('vitals', 'N/A')}
* **Lab Results:** {patient_data.get('labs', 'N/A')}
* **Medical History:** {patient_data.get('history', 'N/A')}

---

## 🔬 DIAGNOSIS (Multi-Agent Run)
* **Primary:** {results['diagnosis']['diagnosis']}
* **Mean Confidence:** {results['diagnosis']['confidence']}%
* **Epistemic Uncertainty:** {epistemic_unc} *(Lower is better)*
* **Data Quality Score:** {data_qual}/100
* **Alternatives:** {', '.join(results['diagnosis']['alternatives'])}
* **Key Indicators:** {results['diagnosis']['indicators']}

---

## 🚨 TRIAGE & CONFLICT RESOLUTION
* **Triage Level:** {results['triage']['triage_level']}
* **Urgency Score:** {results['triage']['urgency_score']}/10
* **Reasoning:** {results['triage']['reasoning']}

{conflict_text}

---

## 💡 DOCTOR SUMMARY (Explainability Agent)
{results['doctor_summary']}

---

## ⚖️ FAIRNESS & CASCADING BIAS AUDIT
* **Gender Bias:** {results['bias_report']['gender_bias']['status']} ({results['bias_report']['gender_bias']['detail']})
* **Age Bias:** {results['bias_report']['age_bias']['status']} ({results['bias_report']['age_bias']['detail']})
* **Income Bias:** {results['bias_report']['income_bias']['status']} ({results['bias_report']['income_bias']['detail']})

{cascade_text}

---

## 🧠 TEMPORAL MEMORY (Vector Semantic Search)
```text
{results['memory_summary']}
```

---

## 💊 TREATMENT PLAN
{chr(10).join('- ' + a for a in results.get('treatment_plan', {}).get('immediate_actions', ['N/A']))}

**Monitoring:** {results.get('treatment_plan', {}).get('monitoring', 'N/A')}
**Precautions:** {results.get('treatment_plan', {}).get('precautions', 'N/A')}

---

## 🏥 SPECIALIST REFERRAL
* **Referral Needed:** {"Yes" if results.get('referral', {}).get('referral_needed') else "No"}
* **Departments:** {', '.join(results.get('referral', {}).get('departments', ['None']))}
* **Urgency:** {results.get('referral', {}).get('urgency', 'N/A')}
* **Reasoning:** {results.get('referral', {}).get('reasoning', 'N/A')}

---

## 💬 PATIENT-FRIENDLY SUMMARY
{results.get('patient_message', 'N/A')}

---

## 📋 FOLLOW-UP CARE PLAN
**Discharge Instructions:** {results.get('follow_up', {}).get('discharge_instructions', 'N/A')}

**Red Flags (Return to ED if):**
{chr(10).join('- ⚠️ ' + f for f in results.get('follow_up', {}).get('red_flags', ['None']))}

**Lifestyle Advice:** {results.get('follow_up', {}).get('lifestyle_advice', 'N/A')}
"""
    return report




# ──────────────────────────────────────────
# Sidebar — Patient Input + Settings
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 ARIA")
    st.markdown("*Autonomous Real-time Intelligence for Clinical Action*")
    st.markdown("---")

    st.markdown("### ⚙️ Settings")
    # Model Selection mappings
    model_configs = {
        "Hybrid (Local DeepSeek-R1 + Gemini Flash)": "gemini-2.5-flash",
        "Hybrid (Local DeepSeek-R1 + Gemini Pro)": "gemini-2.5-pro",
        "Hybrid (Local DeepSeek-R1 + Gemini 2.0)": "gemini-2.0-flash-exp"
    }
    
    selected_model_name = st.selectbox(
        label="🤖 Architecture Mode",
        options=list(model_configs.keys()),
        index=0
    )
    selected_model = model_configs[selected_model_name]
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
    
    # ── Medical Scan Input ──
    st.markdown("### 👁️ Medical Scan (Vision)")
    scan_upload = st.file_uploader("Upload X-Ray, MRI, or Dermoscopy", type=["png", "jpg", "jpeg"], key="scan_upload")

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

    st.markdown("---")
    st.markdown("### 🌐 Multilingual Report")
    report_lang = st.selectbox(
        "Patient Summary Language",
        ["English"] + list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        help="Translate the patient-facing summary using Sarvam AI"
    )


# ──────────────────────────────────────────
# Main Area — Header
# ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_spacer1, col_lottie, col_spacer2 = st.columns([1, 2, 1])
with col_lottie:
    # A beautiful, clean health/pulse lottie animation
    lottie_anim = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_5njp3vgg.json")
    if lottie_anim:
        st_lottie(lottie_anim, height=140, key="header_anim")

st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1.5rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 0.2rem; letter-spacing: -1px;">🏥 ARIA</h1>
        <p style="color: #2563eb; font-weight: 700; letter-spacing: 0.15em; font-size: 1.15rem; margin-top: 0; text-transform: uppercase;">
            Autonomous Real-time Intelligence for Clinical Action
        </p>
        <p style="color: #64748b; font-size: 0.95rem; font-weight: 500;">
            Powered by Google Gemini AI &nbsp;•&nbsp; Premium Clinical Decision Support
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

    # ── Process Vision Sub-Agent ──
    vision_findings = ""
    if scan_upload is not None:
        with st.spinner("👁️ Analyzing medical scan with Gemini Vision..."):
            try:
                from utils.vision_parser import analyze_medical_image
                vision_text = analyze_medical_image(scan_upload.getvalue(), selected_model)
                vision_findings = f"\n\n[Visual Scan Findings]:\n{vision_text}"
            except Exception as e:
                st.error(f"⚠️ Medical Scan Parsing Failed: {e}")

    final_symptoms = symptoms + vision_findings if vision_findings else symptoms

    patient_data = {
        "patient_id": patient_id or f"P-{int(time.time())}",
        "name": patient_name or "Unknown Patient",
        "age": age,
        "gender": gender,
        "symptoms": final_symptoms,
        "vitals": vitals or "Not provided",
        "labs": labs or "Not provided",
        "history": history or "Not provided",
        "income_bracket": income
    }
    
    # Simple hash to avoid re-running unchanged inputs (saves API quota)
    import hashlib
    data_str = json.dumps(patient_data, sort_keys=True)
    current_hash = hashlib.md5(data_str.encode()).hexdigest()
    
    if "last_run_hash" in st.session_state and st.session_state["last_run_hash"] == current_hash and "results" in st.session_state:
        st.success("✅ Output loaded from cache (No API quota used). Change patient details to re-run.")
        st.stop()

    # ── Live Agent Thinking Screen ──
    st.markdown("### 🧠 Agent Pipeline")
    st.caption(f"Model: `{selected_model}` — Retry enabled (3 attempts with backoff)")

    agent_statuses = {}
    status_container = st.container()

    agent_icons = {
        "Temporal Memory Agent": "🧠",
        "Diagnostic Agent": "🔬",
        "Triage Agent": "🚨",
        "Conflict Resolver": "⚔️",
        "Bias Monitor": "⚖️",
        "Explainability Agent": "💡",
        "Treatment Planner": "💊",
        "Specialist Referral": "🏥",
        "Patient Communicator": "💬",
        "Follow-Up Planner": "📋"
    }
    agent_actions = {
        "Temporal Memory Agent": "scanning patient history...",
        "Diagnostic Agent": "analyzing via local DeepSeek-R1 (takes 1-2 mins)...",
        "Triage Agent": "scoring clinical urgency...",
        "Conflict Resolver": "resolving clinical mismatch...",
        "Bias Monitor": "auditing for demographic bias...",
        "Explainability Agent": "writing doctor-friendly summary...",
        "Treatment Planner": "generating evidence-based treatment plan...",
        "Specialist Referral": "evaluating specialist department needs...",
        "Patient Communicator": "composing patient-friendly message...",
        "Follow-Up Planner": "scheduling follow-up care timeline..."
    }

    with status_container:
        progress_placeholder = st.empty()
        progress_bar = st.progress(0, text="Initializing agents...")

    from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx
    import threading
    
    ctx = get_script_run_ctx()

    def update_agent_status(agent_name, status):
        # LangGraph runs nodes in a ThreadPoolExecutor. Streamlit UI calls require context.
        if get_script_run_ctx() is None and ctx is not None:
            add_script_run_ctx(threading.current_thread(), ctx)
            
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
        st.session_state["last_run_hash"] = current_hash
        if scan_upload is not None:
            st.session_state["scan_image_bytes"] = scan_upload.getvalue()
        else:
            st.session_state.pop("scan_image_bytes", None)
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        if "429" in error_msg or "quota" in error_msg.lower():
            st.error(f"⚠️ **Rate limit hit** even after retries. Your Gemini free tier daily quota is exhausted.\n\n"
                     f"**Options:**\n"
                     f"- Wait for quota reset (midnight US Pacific / ~1:30 PM IST)\n"
                     f"- Try a different model from the dropdown\n"
                     f"- Use a new API key from a different Google account")
        else:
            st.error(f"❌ Pipeline error: {repr(e)}\n\nTraceback:\n{error_msg}")
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

    if "scan_image_bytes" in st.session_state:
        st.image(st.session_state["scan_image_bytes"], caption="Uploaded Medical Scan Used for Analysis", width=350)

    # ── Row 1: Diagnosis + Confidence Gauge + Triage ──
    res_col1, res_col2, res_col3 = st.columns([3, 1.5, 2.5])

    with res_col1:
        diag = results["diagnosis"]
        card_class = get_card_class(triage_level)
        model_used = st.session_state.get('pipeline_results', {}).get('model_used', 'DeepSeek-R1:8b (Local via Ollama)')
        st.markdown(f"""
            <div class="{card_class}">
                <h4 style="margin: 0 0 0.5rem 0;">🔬 Diagnosis</h4>
                <p style="font-size: 1.3rem; color: #e6edf3; font-weight: 600; margin: 0;">
                    {diag['diagnosis']}
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0.5rem 0 0.3rem 0;">
                    <strong>🤖 Model Used:</strong> `{model_used}`
                </p>
                <p style="color: #58a6ff; font-size: 0.85rem; margin: 0.5rem 0 0.3rem 0;">
                    <strong>Epistemic Uncertainty:</strong> {diag.get('epistemic_uncertainty', 'N/A')} | 
                    <strong>Data Quality:</strong> {diag.get('data_quality_score', 'N/A')}/100
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0.5rem 0 0.3rem 0;">
                    <strong>Key Indicators:</strong> {diag.get('indicators', '')}
                </p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">
                    <strong>Alternatives:</strong> {', '.join(diag['alternatives'])}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # PROOF FOR HACKATHON
        if "local_reasoning" in diag:
            with st.expander("👀 View Local Model's Reasoning (DeepSeek-R1 <think> block)"):
                st.code(diag["local_reasoning"], language="text")

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

    st.markdown("")

    # ── Row 4: Treatment Plan + Specialist Referral ──
    treat_col, ref_col = st.columns([1, 1])

    with treat_col:
        treatment = results.get("treatment_plan", {})
        st.markdown('<div class="aria-card">', unsafe_allow_html=True)
        st.markdown("#### 💊 Treatment Plan")
        if treatment.get("immediate_actions"):
            st.markdown("**Immediate Actions:**")
            for action in treatment["immediate_actions"]:
                st.markdown(f"- {action}")
        if treatment.get("medications"):
            st.markdown("**Medications:**")
            for med in treatment["medications"]:
                if isinstance(med, dict):
                    st.markdown(f"- **{med.get('name', 'N/A')}** — {med.get('dosage', '')} {med.get('route', '')} {med.get('frequency', '')}")
                else:
                    st.markdown(f"- {med}")
        if treatment.get("monitoring"):
            st.markdown(f"**Monitoring:** {treatment['monitoring']}")
        if treatment.get("precautions"):
            st.warning(f"⚠️ {treatment['precautions']}")
        if not treatment:
            st.markdown("*No treatment plan generated.*")
        st.markdown('</div>', unsafe_allow_html=True)

    with ref_col:
        referral = results.get("referral", {})
        st.markdown('<div class="aria-card">', unsafe_allow_html=True)
        st.markdown("#### 🏥 Specialist Referral")
        if referral.get("referral_needed"):
            urgency_colors = {"IMMEDIATE": "#f85149", "WITHIN_24H": "#d29922", "ROUTINE": "#3fb950"}
            urg = referral.get("urgency", "ROUTINE")
            urg_color = urgency_colors.get(urg, "#8b949e")
            depts = ", ".join(referral.get("departments", []))
            st.markdown(f"""
                <p style="margin: 0.3rem 0;"><strong>Departments:</strong> {depts}</p>
                <p style="margin: 0.3rem 0;"><strong>Urgency:</strong> <span style="color: {urg_color}; font-weight: 700;">{urg}</span></p>
                <p style="margin: 0.3rem 0; color: #8b949e;"><strong>Reasoning:</strong> {referral.get('reasoning', '')}</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("✅ No specialist referral needed at this time.")
            if referral.get("reasoning"):
                st.caption(referral["reasoning"])
        if not referral:
            st.markdown("*No referral data generated.*")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Row 5: Patient Message ──
    patient_msg = results.get("patient_message", "")
    if patient_msg:
        st.markdown(f"""
            <div class="aria-card" style="border-left: 4px solid #58a6ff;">
                <h4 style="margin: 0 0 0.5rem 0;">💬 Patient-Friendly Summary</h4>
                <p style="color: #e6edf3; font-size: 1.05rem; line-height: 1.6; font-style: italic;">
                    "{patient_msg}"
                </p>
                <p style="color: #484f58; font-size: 0.8rem; margin: 0.5rem 0 0 0;">This message is written for the patient and their family in simple, compassionate language.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 6: Follow-Up Plan ──
    follow_up = results.get("follow_up", {})
    if follow_up:
        st.markdown('<div class="aria-card">', unsafe_allow_html=True)
        st.markdown("#### 📋 Follow-Up Care Plan")
        if follow_up.get("discharge_instructions"):
            st.markdown(f"**Discharge Instructions:** {follow_up['discharge_instructions']}")
        if follow_up.get("follow_up_timeline"):
            st.markdown("**Follow-Up Timeline:**")
            timeline_html = '<div style="display: flex; align-items: center; overflow-x: auto; gap: 0.25rem; padding: 0.5rem 0;">'
            for i, step in enumerate(follow_up["follow_up_timeline"]):
                if isinstance(step, dict):
                    tf = step.get("timeframe", "")
                    act = step.get("action", "")
                else:
                    tf = ""
                    act = str(step)
                timeline_html += f"""
                    <div class="timeline-item" style="border-top: 3px solid #58a6ff;">
                        <div style="color: #58a6ff; font-size: 0.75rem; font-weight: 700;">{tf}</div>
                        <div style="color: #e6edf3; font-size: 0.8rem;">{act}</div>
                    </div>
                """
                if i < len(follow_up["follow_up_timeline"]) - 1:
                    timeline_html += '<span style="color: #30363d; font-size: 1.2rem;">→</span>'
            timeline_html += '</div>'
            st.markdown(timeline_html, unsafe_allow_html=True)
        if follow_up.get("red_flags"):
            st.markdown("**🚩 Red Flags (Return to ED immediately if):**")
            for flag in follow_up["red_flags"]:
                st.markdown(f"- ⚠️ {flag}")
        if follow_up.get("lifestyle_advice"):
            st.markdown(f"**🌿 Lifestyle Advice:** {follow_up['lifestyle_advice']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 4: Memory + Export ──
    mem_col, export_col = st.columns([2, 1])

    with mem_col:
        with st.expander("🧠 Temporal Memory — Past Visit Data"):
            st.markdown(f"```\n{results['memory_summary']}\n```")

    with export_col:
        try:
            translated_content = None
            target_language = None

            if report_lang != "English":
                with st.spinner(f"Translating to {report_lang} via Sarvam AI..."):
                    lang_code = SUPPORTED_LANGUAGES[report_lang]
                    translated_content = translate_patient_report(
                        patient_data, results, target_language=lang_code
                    )
                    target_language = report_lang

            pdf_bytes = generate_pdf_report(
                patient_data, results,
                translated_content=translated_content,
                target_language=target_language
            )

            lang_tag = f"_{report_lang}" if report_lang != "English" else ""
            dl_label = "Download PDF Report"
            if report_lang != "English":
                dl_label += f" ({report_lang})"

            st.download_button(
                label=dl_label,
                data=pdf_bytes,
                file_name=f"ARIA_Report_{patient_data.get('patient_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M')}{lang_tag}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            if report_lang != "English":
                st.success(f"Includes {report_lang} patient summary (Sarvam AI)")
        except Exception as e:
            st.error(f"PDF Generation Error: {str(e)}")
            report_text = generate_report(patient_data, results)
            st.download_button(
                label="Download Report (Markdown)",
                data=report_text,
                file_name=f"ARIA_Report_{patient_data.get('patient_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
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
