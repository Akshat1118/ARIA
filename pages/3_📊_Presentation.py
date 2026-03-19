"""
ARIA — Presentation Slides Page
Interactive Streamlit-based slides for hackathon presentation.
"""

import streamlit as st

st.set_page_config(
    page_title="ARIA — Presentation",
    page_icon="🏥",
    layout="wide"
)

# ── CSS Theme ──
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
    .stApp, .stApp * { color: #e6edf3; }

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
    p, span, label, div, li, td, th, dt, dd, figcaption, strong, em {
        color: #c9d1d9 !important;
    }

    /* ── Radio Buttons in Sidebar ── */
    .stRadio label span, .stRadio > label, [data-testid="stRadio"] * {
        color: #c9d1d9 !important;
    }

    /* ── Presentation Cards ── */
    .slide-card {
        background: rgba(13, 27, 62, 0.6); border: 1px solid rgba(56, 139, 253, 0.2);
        border-radius: 16px; padding: 2rem; margin: 0.5rem 0;
        backdrop-filter: blur(10px); min-height: 400px;
    }
    .stat-big {
        font-size: 3rem; font-weight: 700; color: #58a6ff !important;
        text-align: center; margin: 0; line-height: 1.2;
    }
    .stat-label {
        font-size: 1rem; color: #8b949e !important; text-align: center; margin: 0;
    }

    /* ── Special colors ── */
    .slide-card span, .slide-card strong { color: inherit; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0e27; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #484f58; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────
# Slide Navigation
# ──────────────────────────────────────────
slides = [
    "Title",
    "The Problem",
    "What is ARIA",
    "Agent Architecture",
    "How It Works",
    "Key Differentiators",
    "SDG 3 Impact",
    "Tech Stack",
    "Feasibility",
    "Thank You"
]

with st.sidebar:
    st.markdown("### 📊 Presentation")
    slide_idx = st.radio("Navigate Slides", range(len(slides)),
                         format_func=lambda i: f"{i+1}. {slides[i]}")

# ──────────────────────────────────────────
# SLIDES
# ──────────────────────────────────────────

if slide_idx == 0:
    # ── SLIDE 1: Title ──
    st.markdown("""
    <div class="slide-card" style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
        <p style="font-size: 4rem; margin: 0;">🏥</p>
        <h1 style="font-size: 3.5rem; margin: 0.5rem 0;">ARIA</h1>
        <p style="color: #8b949e; font-size: 1.3rem; margin: 0.5rem 0;">
            Autonomous Real-time Intelligence for Clinical Action
        </p>
        <p style="color: #484f58; font-size: 1rem; margin: 1rem 0 0 0;">
            A Multi-Agent AI Clinical Decision Support System
        </p>
        <div style="margin-top: 2rem;">
            <span style="color: #58a6ff;">🤖 4 AI Agents</span> &nbsp;•&nbsp;
            <span style="color: #3fb950;">⚖️ Bias Detection</span> &nbsp;•&nbsp;
            <span style="color: #d29922;">🌍 SDG 3 Aligned</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 1:
    # ── SLIDE 2: The Problem ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">😰 The Problem</h2>
        <div style="display: flex; gap: 2rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                <p class="stat-big" style="color: #f85149;">250K+</p>
                <p class="stat-label">Deaths/year from diagnostic errors (US alone)</p>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <p class="stat-big" style="color: #d29922;">4.5 hrs</p>
                <p class="stat-label">Average ED wait time in overcrowded hospitals</p>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <p class="stat-big" style="color: #58a6ff;">40%</p>
                <p class="stat-label">Of triage decisions show demographic bias</p>
            </div>
        </div>
        <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(248, 81, 73, 0.08); border-left: 4px solid #f85149; border-radius: 8px;">
            <p style="font-size: 1.2rem; margin: 0; color: #e6edf3;">
                <strong>Emergency departments need AI that is fast, accurate, explainable, and fair.</strong>
            </p>
            <p style="color: #8b949e; margin: 0.5rem 0 0 0;">
                Current clinical AI tools are single-model black boxes with no memory, no bias checks, and no explainability.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 2:
    # ── SLIDE 3: What is ARIA ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">🎯 What is ARIA?</h2>
        <p style="font-size: 1.2rem; line-height: 1.7; color: #e6edf3;">
            ARIA is a <strong style="color: #58a6ff;">Multi-Agent AI System</strong> where
            <strong>4 specialized agents collaborate in a pipeline</strong> to:
        </p>
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; background: rgba(56, 139, 253, 0.1); border: 1px solid rgba(56, 139, 253, 0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 2rem; margin: 0;">🧠</p>
                <p style="color: #58a6ff; font-weight: 600; margin: 0.3rem 0;">Remember</p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Patient history across visits</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(88, 166, 255, 0.1); border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 2rem; margin: 0;">🔬</p>
                <p style="color: #58a6ff; font-weight: 600; margin: 0.3rem 0;">Diagnose</p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Differential diagnosis + confidence</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(210, 153, 34, 0.1); border: 1px solid rgba(210, 153, 34, 0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 2rem; margin: 0;">🚨</p>
                <p style="color: #d29922; font-weight: 600; margin: 0.3rem 0;">Triage</p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Urgency scoring (Critical → Low)</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: rgba(63, 185, 80, 0.1); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 1rem; text-align: center;">
                <p style="font-size: 2rem; margin: 0;">💡</p>
                <p style="color: #3fb950; font-weight: 600; margin: 0.3rem 0;">Explain</p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Plain English doctor summary</p>
            </div>
        </div>
        <p style="color: #3fb950; font-size: 1.1rem; text-align: center; margin-top: 1.5rem;">
            + Built-in ⚖️ <strong>Bias Detection</strong> after every decision
        </p>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 3:
    # ── SLIDE 4: Agent Architecture ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">🤖 Agent Architecture</h2>
        <div style="text-align: center; padding: 1rem; font-size: 1.1rem;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; flex-wrap: wrap;">
                <div style="background: rgba(56, 139, 253, 0.15); border: 1px solid #58a6ff; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    📋 <strong>Patient Input</strong><br><span style="color: #8b949e; font-size: 0.8rem;">Voice 🎙️ or Text</span>
                </div>
                <span style="color: #58a6ff; font-size: 1.5rem;">→</span>
                <div style="background: rgba(56, 139, 253, 0.15); border: 1px solid #58a6ff; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    🧠 <strong>Memory</strong><br><span style="color: #8b949e; font-size: 0.8rem;">SQLite history</span>
                </div>
                <span style="color: #58a6ff; font-size: 1.5rem;">→</span>
                <div style="background: rgba(88, 166, 255, 0.15); border: 1px solid #58a6ff; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    🔬 <strong>Diagnosis</strong><br><span style="color: #8b949e; font-size: 0.8rem;">Gemini LLM</span>
                </div>
                <span style="color: #d29922; font-size: 1.5rem;">→</span>
                <div style="background: rgba(210, 153, 34, 0.15); border: 1px solid #d29922; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    🚨 <strong>Triage</strong><br><span style="color: #8b949e; font-size: 0.8rem;">Gemini LLM</span>
                </div>
                <span style="color: #f85149; font-size: 1.5rem;">→</span>
                <div style="background: rgba(248, 81, 73, 0.15); border: 1px solid #f85149; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    ⚖️ <strong>Bias Check</strong><br><span style="color: #8b949e; font-size: 0.8rem;">Rule-based</span>
                </div>
                <span style="color: #3fb950; font-size: 1.5rem;">→</span>
                <div style="background: rgba(63, 185, 80, 0.15); border: 1px solid #3fb950; border-radius: 12px; padding: 0.8rem 1.2rem;">
                    💡 <strong>Explain</strong><br><span style="color: #8b949e; font-size: 0.8rem;">Gemini LLM</span>
                </div>
            </div>
        </div>
        <div style="margin-top: 1.5rem; display: flex; gap: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; padding: 1rem; background: rgba(13, 27, 62, 0.8); border-radius: 8px;">
                <p style="color: #58a6ff; margin: 0;"><strong>3 LLM Agents</strong></p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Diagnostic, Triage, Explainability — powered by Gemini</p>
            </div>
            <div style="flex: 1; padding: 1rem; background: rgba(13, 27, 62, 0.8); border-radius: 8px;">
                <p style="color: #3fb950; margin: 0;"><strong>2 Non-LLM Agents</strong></p>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Memory (SQLite) + Bias Monitor (rule-based) — deterministic & auditable</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 4:
    # ── SLIDE 5: How It Works ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">⚡ How It Works (5 Seconds)</h2>
        <div style="display: flex; flex-direction: column; gap: 0.8rem;">
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(56, 139, 253, 0.08); border-left: 3px solid #58a6ff; border-radius: 8px;">
                <span style="font-size: 1.5rem; min-width: 40px;">1️⃣</span>
                <div>
                    <strong style="color: #58a6ff;">Doctor inputs patient data</strong> (text or voice 🎙️)
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Symptoms, vitals, labs, history — or speak naturally</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(56, 139, 253, 0.08); border-left: 3px solid #58a6ff; border-radius: 8px;">
                <span style="font-size: 1.5rem; min-width: 40px;">2️⃣</span>
                <div>
                    <strong style="color: #58a6ff;">ARIA checks past visits</strong> (Temporal Memory)
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">SQLite lookup — has this patient been here before?</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(88, 166, 255, 0.08); border-left: 3px solid #58a6ff; border-radius: 8px;">
                <span style="font-size: 1.5rem; min-width: 40px;">3️⃣</span>
                <div>
                    <strong style="color: #58a6ff;">AI diagnoses + triages</strong> with confidence score
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Gemini generates diagnosis, alternatives, urgency level</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(248, 81, 73, 0.08); border-left: 3px solid #f85149; border-radius: 8px;">
                <span style="font-size: 1.5rem; min-width: 40px;">4️⃣</span>
                <div>
                    <strong style="color: #f85149;">Bias audit runs automatically</strong>
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Checks gender, age, income bias — flags issues</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(63, 185, 80, 0.08); border-left: 3px solid #3fb950; border-radius: 8px;">
                <span style="font-size: 1.5rem; min-width: 40px;">5️⃣</span>
                <div>
                    <strong style="color: #3fb950;">Doctor gets a clear dashboard</strong>
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">Diagnosis + triage + timeline + bias report + downloadable summary</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 5:
    # ── SLIDE 6: Key Differentiators ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">🏆 Why ARIA is Different</h2>
        <table style="width: 100%; border-collapse: collapse; color: #c9d1d9;">
            <tr style="border-bottom: 2px solid rgba(56, 139, 253, 0.3);">
                <th style="padding: 0.8rem; text-align: left; color: #8b949e;">Feature</th>
                <th style="padding: 0.8rem; text-align: center; color: #8b949e;">ChatGPT / Claude</th>
                <th style="padding: 0.8rem; text-align: center; color: #8b949e;">Existing Clinical AI</th>
                <th style="padding: 0.8rem; text-align: center; color: #58a6ff;">ARIA ★</th>
            </tr>
            <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.1);">
                <td style="padding: 0.8rem;">Multi-Agent Pipeline</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ Single model</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ Single model</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅ 4 specialized agents</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.1);">
                <td style="padding: 0.8rem;">Temporal Memory</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ No persistence</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ No cross-visit memory</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅ SQLite history</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.1);">
                <td style="padding: 0.8rem;">Bias Detection</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ None</td>
                <td style="padding: 0.8rem; text-align: center; color: #d29922;">⚠️ Limited</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅ Built-in auditor</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(56, 139, 253, 0.1);">
                <td style="padding: 0.8rem;">Explainability</td>
                <td style="padding: 0.8rem; text-align: center; color: #d29922;">⚠️ Verbose</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ Black box</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅ 3-sentence summary</td>
            </tr>
            <tr>
                <td style="padding: 0.8rem;">Structured Clinical Output</td>
                <td style="padding: 0.8rem; text-align: center; color: #f85149;">❌ Free text</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅</td>
                <td style="padding: 0.8rem; text-align: center; color: #3fb950;">✅ JSON → Dashboard</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 6:
    # ── SLIDE 7: SDG 3 Impact ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">🌍 SDG 3 — Good Health and Well-being</h2>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; background: linear-gradient(135deg, rgba(76, 159, 56, 0.15), rgba(63, 185, 80, 0.05)); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 1.5rem;">
                <h3 style="margin: 0; color: #3fb950;">Target 3.1</h3>
                <p style="color: #e6edf3; font-weight: 600;">Reduce Maternal Mortality</p>
                <p style="color: #8b949e; font-size: 0.85rem;">Preeclampsia detection in diagnostic pipeline</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: linear-gradient(135deg, rgba(76, 159, 56, 0.15), rgba(63, 185, 80, 0.05)); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 1.5rem;">
                <h3 style="margin: 0; color: #3fb950;">Target 3.4</h3>
                <p style="color: #e6edf3; font-weight: 600;">Reduce NCD Mortality</p>
                <p style="color: #8b949e; font-size: 0.85rem;">Cardiac, stroke, respiratory triage</p>
            </div>
            <div style="flex: 1; min-width: 200px; background: linear-gradient(135deg, rgba(76, 159, 56, 0.15), rgba(63, 185, 80, 0.05)); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; padding: 1.5rem;">
                <h3 style="margin: 0; color: #3fb950;">Target 3.8</h3>
                <p style="color: #e6edf3; font-weight: 600;">Universal Health Coverage</p>
                <p style="color: #8b949e; font-size: 0.85rem;">Bias-free triage for all demographics</p>
            </div>
        </div>
        <div style="margin-top: 1.5rem; text-align: center; padding: 1rem; background: rgba(63, 185, 80, 0.08); border-radius: 12px; border: 1px solid rgba(63, 185, 80, 0.2);">
            <p style="font-size: 1.2rem; color: #3fb950; margin: 0;">
                📊 Live SDG Dashboard tracks <strong>patients triaged fairly</strong> and <strong>bias cases flagged</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 7:
    # ── SLIDE 8: Tech Stack ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">🛠️ Tech Stack</h2>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px; padding: 1.5rem; background: rgba(13, 27, 62, 0.8); border: 1px solid rgba(56, 139, 253, 0.2); border-radius: 12px;">
                <h4 style="margin: 0 0 0.5rem 0; color: #58a6ff;">🧠 AI Layer</h4>
                <p style="margin: 0.3rem 0;">Google Gemini 2.5 Flash — Free tier LLM</p>
                <p style="margin: 0.3rem 0;">SpeechRecognition — Free voice input</p>
                <p style="margin: 0.3rem 0;">Rule-based bias engine</p>
            </div>
            <div style="flex: 1; min-width: 250px; padding: 1.5rem; background: rgba(13, 27, 62, 0.8); border: 1px solid rgba(56, 139, 253, 0.2); border-radius: 12px;">
                <h4 style="margin: 0 0 0.5rem 0; color: #58a6ff;">💻 App Layer</h4>
                <p style="margin: 0.3rem 0;">Streamlit — Python web framework</p>
                <p style="margin: 0.3rem 0;">Python 3.10+ — Simple, no frameworks</p>
                <p style="margin: 0.3rem 0;">Custom CSS — Dark premium theme</p>
            </div>
            <div style="flex: 1; min-width: 250px; padding: 1.5rem; background: rgba(13, 27, 62, 0.8); border: 1px solid rgba(56, 139, 253, 0.2); border-radius: 12px;">
                <h4 style="margin: 0 0 0.5rem 0; color: #58a6ff;">💾 Data Layer</h4>
                <p style="margin: 0.3rem 0;">SQLite — Zero-setup database</p>
                <p style="margin: 0.3rem 0;">100% local — No cloud dependency</p>
                <p style="margin: 0.3rem 0;">MIMIC-III compatible format</p>
            </div>
        </div>
        <div style="margin-top: 1.5rem; text-align: center;">
            <p style="color: #8b949e; font-size: 1rem;">
                <strong style="color: #58a6ff;">No LangChain</strong> · <strong style="color: #58a6ff;">No custom training</strong> · <strong style="color: #58a6ff;">No cloud database</strong>
            </p>
            <p style="color: #484f58;">Simple Python functions as agents — easy to audit, debug, and explain.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 8:
    # ── SLIDE 9: Feasibility ──
    st.markdown("""
    <div class="slide-card">
        <h2 style="margin: 0 0 1.5rem 0;">✅ Feasibility — Buildable Today. Scalable Tomorrow.</h2>
        <div style="display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                <div style="padding: 1rem; background: rgba(63, 185, 80, 0.08); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: #3fb950;">✅ Technical Viability</h4>
                    <p style="color: #c9d1d9; font-size: 0.9rem; margin: 0.3rem 0 0 0;">All agents use existing LLM APIs — no custom model training required.</p>
                </div>
                <div style="padding: 1rem; background: rgba(63, 185, 80, 0.08); border: 1px solid rgba(63, 185, 80, 0.3); border-radius: 12px;">
                    <h4 style="margin: 0; color: #3fb950;">✅ Scoped MVP</h4>
                    <p style="color: #c9d1d9; font-size: 0.9rem; margin: 0.3rem 0 0 0;">Working end-to-end pipeline — input → diagnosis → triage → explanation.</p>
                </div>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <h4 style="margin: 0 0 0.5rem 0;">⚠️ Risks & Mitigations</h4>
                <div style="padding: 0.8rem; background: rgba(210, 153, 34, 0.08); border-left: 3px solid #d29922; border-radius: 4px; margin-bottom: 0.5rem;">
                    <strong style="color: #d29922;">LLM Hallucinations</strong>
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">→ Confidence scores + explainability agent as check</p>
                </div>
                <div style="padding: 0.8rem; background: rgba(210, 153, 34, 0.08); border-left: 3px solid #d29922; border-radius: 4px; margin-bottom: 0.5rem;">
                    <strong style="color: #d29922;">No Real Patient Data</strong>
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">→ Sample data; MIMIC-III compatible</p>
                </div>
                <div style="padding: 0.8rem; background: rgba(210, 153, 34, 0.08); border-left: 3px solid #d29922; border-radius: 4px;">
                    <strong style="color: #d29922;">Agent Latency</strong>
                    <p style="color: #8b949e; font-size: 0.85rem; margin: 0;">→ Pipeline runs in ~5-10 seconds</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif slide_idx == 9:
    # ── SLIDE 10: Thank You ──
    st.markdown("""
    <div class="slide-card" style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
        <p style="font-size: 4rem; margin: 0;">🏥</p>
        <h1 style="font-size: 3rem; margin: 0.5rem 0;">Thank You</h1>
        <p style="color: #8b949e; font-size: 1.3rem; margin: 1rem 0;">
            ARIA doesn't replace doctors —<br>
            it gives them a <strong style="color: #58a6ff;">second opinion in 5 seconds</strong>,<br>
            with <strong style="color: #3fb950;">built-in bias checks</strong> and <strong style="color: #d29922;">no one left behind</strong>.
        </p>
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(56, 139, 253, 0.08); border: 1px solid rgba(56, 139, 253, 0.3); border-radius: 12px;">
            <p style="color: #58a6ff; font-size: 1rem; font-style: italic; margin: 0;">
                "Every component uses production-ready tech — the innovation is in how we connect them."
            </p>
        </div>
        <div style="margin-top: 2rem;">
            <span style="color: #58a6ff;">🤖 Multi-Agent AI</span> &nbsp;•&nbsp;
            <span style="color: #3fb950;">⚖️ Bias-Free</span> &nbsp;•&nbsp;
            <span style="color: #d29922;">🌍 SDG 3</span> &nbsp;•&nbsp;
            <span style="color: #f85149;">📄 Research-Backed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
