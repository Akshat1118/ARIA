"""
ARIA — About Page
Architecture diagram, SDG 3 info, team info, and project background.
"""

import streamlit as st

st.set_page_config(
    page_title="ARIA — About",
    page_icon="🏥",
    layout="wide"
)

# ── CSS Theme (same as main app) ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3e 50%, #0a1628 100%);
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #e6edf3 !important;
        font-family: 'Inter', sans-serif !important;
    }
    h1 {
        background: linear-gradient(90deg, #58a6ff, #3fb950, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    .stMarkdown, p, span, label, li { color: #c9d1d9; }
    .info-card {
        background: rgba(13, 27, 62, 0.6);
        border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .info-card:hover {
        border-color: rgba(56, 139, 253, 0.5);
        box-shadow: 0 4px 20px rgba(56, 139, 253, 0.15);
        transform: translateY(-2px);
    }
    .sdg-card {
        background: linear-gradient(135deg, rgba(76, 159, 56, 0.15), rgba(63, 185, 80, 0.05));
        border: 1px solid rgba(63, 185, 80, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    .agent-card {
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.3rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    .agent-card:hover { transform: translateY(-3px); }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b3e 0%, #0a1628 100%);
        border-right: 1px solid rgba(56, 139, 253, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# Header
# ──────────────────────────────────────────
st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.5rem; margin-bottom: 0.2rem;">🏥 About ARIA</h1>
        <p style="color: #8b949e; font-size: 1.1rem;">
            Autonomous Real-time Intelligence for Clinical Action
        </p>
    </div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# What is ARIA
# ──────────────────────────────────────────
st.markdown("""
<div class="info-card">
    <h3 style="margin: 0 0 0.8rem 0;">🎯 What is ARIA?</h3>
    <p style="font-size: 1.05rem; line-height: 1.7;">
        ARIA is a <strong style="color: #58a6ff;">Multi-Agent AI Clinical Decision Support System</strong>
        built for emergency departments. Instead of one AI doing everything, ARIA uses
        <strong>4 specialized agents</strong> that collaborate in a pipeline to diagnose, triage,
        detect bias, and explain — all in seconds.
    </p>
    <p style="color: #8b949e; margin-top: 0.5rem;">
        <em>Core Philosophy: Simple on the inside, powerful on the outside.</em>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Agent Architecture
# ──────────────────────────────────────────
st.markdown("### 🤖 Agent Architecture")
st.markdown("")

a1, a2, a3, a4, a5 = st.columns(5)

with a1:
    st.markdown("""
        <div class="agent-card" style="background: rgba(56, 139, 253, 0.1); border: 1px solid rgba(56, 139, 253, 0.3);">
            <div style="font-size: 2rem;">🧠</div>
            <h4 style="font-size: 0.9rem; margin: 0.5rem 0 0.3rem 0;">Memory Agent</h4>
            <p style="color: #8b949e; font-size: 0.75rem; margin: 0;">SQLite-based patient history across visits</p>
        </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown("""
        <div class="agent-card" style="background: rgba(88, 166, 255, 0.1); border: 1px solid rgba(88, 166, 255, 0.3);">
            <div style="font-size: 2rem;">🔬</div>
            <h4 style="font-size: 0.9rem; margin: 0.5rem 0 0.3rem 0;">Diagnostic Agent</h4>
            <p style="color: #8b949e; font-size: 0.75rem; margin: 0;">Differential diagnosis + confidence scoring</p>
        </div>
    """, unsafe_allow_html=True)

with a3:
    st.markdown("""
        <div class="agent-card" style="background: rgba(210, 153, 34, 0.1); border: 1px solid rgba(210, 153, 34, 0.3);">
            <div style="font-size: 2rem;">🚨</div>
            <h4 style="font-size: 0.9rem; margin: 0.5rem 0 0.3rem 0;">Triage Agent</h4>
            <p style="color: #8b949e; font-size: 0.75rem; margin: 0;">Urgency scoring (Critical → Low)</p>
        </div>
    """, unsafe_allow_html=True)

with a4:
    st.markdown("""
        <div class="agent-card" style="background: rgba(248, 81, 73, 0.1); border: 1px solid rgba(248, 81, 73, 0.3);">
            <div style="font-size: 2rem;">⚖️</div>
            <h4 style="font-size: 0.9rem; margin: 0.5rem 0 0.3rem 0;">Bias Monitor</h4>
            <p style="color: #8b949e; font-size: 0.75rem; margin: 0;">Gender, age & income fairness checks</p>
        </div>
    """, unsafe_allow_html=True)

with a5:
    st.markdown("""
        <div class="agent-card" style="background: rgba(63, 185, 80, 0.1); border: 1px solid rgba(63, 185, 80, 0.3);">
            <div style="font-size: 2rem;">💡</div>
            <h4 style="font-size: 0.9rem; margin: 0.5rem 0 0.3rem 0;">Explainability Agent</h4>
            <p style="color: #8b949e; font-size: 0.75rem; margin: 0;">3-sentence plain English summary</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ── Pipeline Flow ──
st.markdown("""
<div class="info-card">
    <h4 style="margin: 0 0 0.5rem 0;">🔄 Pipeline Flow</h4>
    <div style="text-align: center; padding: 1rem; font-family: monospace; font-size: 0.95rem;">
        <span style="color: #58a6ff;">📋 Patient Input</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #58a6ff;">🧠 Memory</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #58a6ff;">🔬 Diagnosis</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #d29922;">🚨 Triage</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #f85149;">⚖️ Bias Check</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #3fb950;">💡 Summary</span>
        <span style="color: #484f58;"> ──→ </span>
        <span style="color: #3fb950;">📊 Dashboard</span>
    </div>
    <p style="color: #8b949e; font-size: 0.85rem; text-align: center; margin: 0;">
        Each agent runs sequentially, passing its output to the next. Total time: ~5-10 seconds.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Feasibility
# ──────────────────────────────────────────
st.markdown("### ✅ Feasibility")
st.markdown("*Buildable Today. Scalable Tomorrow.*")
st.markdown("")

f1, f2 = st.columns(2)

with f1:
    st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0;">🔧 Technical Viability</h4>
            <p style="color: #c9d1d9; font-size: 0.9rem;">
                All agents use existing LLM APIs (Google Gemini) — <strong style="color: #58a6ff;">no custom model training required.</strong>
                Simple Python function-based agents, no LangChain or complex frameworks.
            </p>
            <h4 style="margin: 1rem 0 0.5rem 0;">🎯 Scoped MVP</h4>
            <p style="color: #c9d1d9; font-size: 0.9rem;">
                Working pipeline: doctor inputs symptoms → gets diagnosis, triage level,
                and explanation in one flow. Temporal Memory with seeded patient visits.
            </p>
        </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0;">⚠️ Risks & Mitigations</h4>
            <table style="width: 100%; color: #c9d1d9; font-size: 0.85rem;">
                <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.15);">
                    <td style="padding: 0.4rem; color: #d29922;"><strong>LLM Hallucinations</strong></td>
                    <td style="padding: 0.4rem;">Confidence scores + explainability agent as check</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.15);">
                    <td style="padding: 0.4rem; color: #d29922;"><strong>No Real Patient Data</strong></td>
                    <td style="padding: 0.4rem;">Sample data; compatible with MIMIC-III format</td>
                </tr>
                <tr>
                    <td style="padding: 0.4rem; color: #d29922;"><strong>Agent Latency</strong></td>
                    <td style="padding: 0.4rem;">Sequential pipeline runs in ~5-10 seconds</td>
                </tr>
            </table>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="info-card" style="text-align: center; border-color: rgba(63, 185, 80, 0.3);">
    <p style="color: #3fb950; font-size: 1rem; font-style: italic; margin: 0;">
        "Every component uses production-ready tech — the innovation is in how we connect them."
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# SDG 3 Alignment
# ──────────────────────────────────────────
st.markdown("### 🌍 SDG 3 — Good Health and Well-being")
st.markdown("")

sdg1, sdg2, sdg3 = st.columns(3)

with sdg1:
    st.markdown("""
        <div class="sdg-card">
            <h4 style="margin: 0 0 0.3rem 0;">🎯 Target 3.1</h4>
            <p style="color: #3fb950; font-weight: 600; margin: 0;">Reduce Maternal Mortality</p>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0.3rem 0 0 0;">
                ARIA detects preeclampsia and pregnancy complications through its diagnostic pipeline,
                ensuring timely triage of high-risk maternal cases.
            </p>
        </div>
    """, unsafe_allow_html=True)

with sdg2:
    st.markdown("""
        <div class="sdg-card">
            <h4 style="margin: 0 0 0.3rem 0;">🎯 Target 3.4</h4>
            <p style="color: #3fb950; font-weight: 600; margin: 0;">Reduce NCD Mortality</p>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0.3rem 0 0 0;">
                Cardiac events, strokes, and respiratory emergencies are accurately triaged
                with urgency scoring to prevent delayed treatment of critical NCDs.
            </p>
        </div>
    """, unsafe_allow_html=True)

with sdg3:
    st.markdown("""
        <div class="sdg-card">
            <h4 style="margin: 0 0 0.3rem 0;">🎯 Target 3.8</h4>
            <p style="color: #3fb950; font-weight: 600; margin: 0;">Universal Health Coverage</p>
            <p style="color: #8b949e; font-size: 0.85rem; margin: 0.3rem 0 0 0;">
                Built-in bias detection ensures fair triage regardless of gender, age, or income —
                no patient is deprioritized due to demographics.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Technology Stack
# ──────────────────────────────────────────
st.markdown("### 🛠️ Technology Stack")
st.markdown("")

t1, t2, t3 = st.columns(3)

with t1:
    st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0;">🧠 AI Layer</h4>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">Google Gemini</strong> — LLM for diagnosis, triage, and explainability</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">SpeechRecognition</strong> — Free voice transcription</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">Rule-based</strong> — Bias detection engine</p>
        </div>
    """, unsafe_allow_html=True)

with t2:
    st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0;">💻 Application Layer</h4>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">Streamlit</strong> — Python-native web framework</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">Python</strong> — Simple function-based agents</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">Custom CSS</strong> — Premium dark UI theme</p>
        </div>
    """, unsafe_allow_html=True)

with t3:
    st.markdown("""
        <div class="info-card">
            <h4 style="margin: 0 0 0.5rem 0;">💾 Data Layer</h4>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">SQLite</strong> — Patient history & SDG counters</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">CSV</strong> — 10 sample patient records</p>
            <p style="margin: 0.2rem 0;"><strong style="color: #58a6ff;">No Cloud</strong> — 100% local, zero setup</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# AI in Healthcare Evolution
# ──────────────────────────────────────────
st.markdown("### 📈 Evolution of AI in Healthcare")
st.markdown("")

st.markdown("""
<div class="info-card">
    <div style="display: flex; justify-content: space-around; text-align: center; padding: 1rem 0; flex-wrap: wrap; gap: 1rem;">
        <div style="flex: 1; min-width: 150px;">
            <div style="color: #8b949e; font-size: 0.8rem;">GENERATION 1</div>
            <div style="color: #d29922; font-size: 1.5rem; font-weight: 700;">Rule-Based</div>
            <div style="color: #8b949e; font-size: 0.8rem;">IF-THEN expert systems</div>
            <div style="color: #484f58; font-size: 0.75rem;">1970s-2000s</div>
        </div>
        <div style="color: #30363d; font-size: 2rem; display: flex; align-items: center;">→</div>
        <div style="flex: 1; min-width: 150px;">
            <div style="color: #8b949e; font-size: 0.8rem;">GENERATION 2</div>
            <div style="color: #58a6ff; font-size: 1.5rem; font-weight: 700;">ML-Based</div>
            <div style="color: #8b949e; font-size: 0.8rem;">Prediction & classification</div>
            <div style="color: #484f58; font-size: 0.75rem;">2010s-2020s</div>
        </div>
        <div style="color: #30363d; font-size: 2rem; display: flex; align-items: center;">→</div>
        <div style="flex: 1; min-width: 150px; border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 0.5rem;">
            <div style="color: #3fb950; font-size: 0.8rem;">GENERATION 3 ★</div>
            <div style="color: #3fb950; font-size: 1.5rem; font-weight: 700;">Agentic AI</div>
            <div style="color: #3fb950; font-size: 0.8rem;">Reason, plan & act autonomously</div>
            <div style="color: #3fb950; font-size: 0.75rem;">2024+ (ARIA)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Research Background
# ──────────────────────────────────────────
st.markdown("""
<div class="info-card">
    <h3 style="margin: 0 0 0.5rem 0;">📄 Research Background</h3>
    <p style="font-size: 1rem; line-height: 1.6;">
        ARIA is the working implementation of a <strong style="color: #58a6ff;">published research framework</strong>
        from a book chapter submitted to <strong>CRC Press</strong>:
    </p>
    <blockquote style="border-left: 3px solid #58a6ff; padding-left: 1rem; margin: 1rem 0; color: #8b949e; font-style: italic;">
        "A SDG 3-Aligned Agentic AI Framework for Explainable Clinical Decision Automation:
        From Diagnostics to Triage"
    </blockquote>
    <p style="color: #8b949e; font-size: 0.9rem;">
        The full framework describes an 8-agent system. ARIA implements the 4 core agents essential for a working MVP.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ──────────────────────────────────────────
# Team
# ──────────────────────────────────────────
st.markdown("""
<div class="info-card" style="text-align: center;">
    <h3 style="margin: 0 0 0.5rem 0;">👨‍💻 Team</h3>
    <p style="font-size: 1rem;">
        Built by two undergraduate students<br>
        <strong style="color: #58a6ff;">CSE — AI & Data Science, 1st Year</strong>
    </p>
    <p style="color: #8b949e; font-size: 0.9rem; margin-top: 0.5rem;">
        🏆 Built for hackathon &nbsp;•&nbsp; 📄 Research-backed &nbsp;•&nbsp; 🌍 SDG 3 aligned
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("""
<p style="text-align: center; color: #484f58; font-size: 0.8rem;">
    ⚕️ Disclaimer: ARIA is an AI-assisted tool for clinical decision support only.
    Not a substitute for professional medical judgment.
</p>
""", unsafe_allow_html=True)
