# 🎬 ARIA Demo Script — 3-Minute Walkthrough

> **Goal:** Show judges ARIA's full pipeline in action, highlighting multi-agent collaboration,
> bias detection, and SDG 3 alignment.

---

## ⏱️ Timing Breakdown

| Time | Section | What to Show |
|------|---------|-------------|
| 0:00–0:30 | **Intro** | What is ARIA, why it matters |
| 0:30–1:30 | **Demo Case 1** | Rajesh Kumar — CRITICAL cardiac (shows timeline) |
| 1:30–2:15 | **Demo Case 2** | Priya Sharma — Preeclampsia (shows bias detection) |
| 2:15–2:45 | **About Page** | Architecture, SDG 3 targets, feasibility |
| 2:45–3:00 | **Closing** | Impact statement, one-liner |

---

## 📝 Script

### 0:00 — Intro (30 sec)
> "ARIA stands for Autonomous Real-time Intelligence for Clinical Action.
> It's a multi-agent AI system that helps emergency doctors make faster,
> fairer decisions. Instead of one AI doing everything, ARIA uses 4 specialized
> agents that collaborate in a pipeline — like a team of AI specialists."

### 0:30 — Demo Case 1: Rajesh Kumar (60 sec)
1. Check **"Load sample patient"** in sidebar
2. Select **"Rajesh Kumar (Age 55, Male)"**
3. Point out: *"Notice he's 55, male, with chest pain and elevated troponin"*
4. Click **🚀 Run ARIA Pipeline**
5. Show the **live agent thinking** — *"Watch each agent activate in sequence"*
6. When results appear:
   - **Diagnosis:** *"Acute MI with 90%+ confidence"*
   - **Triage:** *"CRITICAL — immediate attention"* (🔊 alarm beeps!)
   - **Confidence Ring:** Point to the SVG gauge
   - **Timeline:** *"See his 2 past visits — stable angina, then unstable angina, now acute MI. ARIA remembers."*
   - **Download Report:** Click to show export
7. **Key message:** *"4 agents, one pipeline, 5 seconds. And it remembers past visits — no other clinical AI does this."*

### 1:30 — Demo Case 2: Priya Sharma (45 sec)
1. Click **🔄 Analyze New Patient**
2. Select **"Priya Sharma (Age 28, Female)"**
3. Point out: *"She's 28, pregnant, hypertensive — preeclampsia risk"*
4. Click **🚀 Run ARIA Pipeline**
5. When results appear:
   - **Bias Report:** *"Look at the Fairness Audit — ARIA checks if gender, age, or income affected the decision"*
   - **SDG Counter:** *"2 patients triaged fairly now, tracked for SDG 3"*
6. **Key message:** *"Every diagnosis is audited for bias. That's SDG 3.8 in action."*

### 2:15 — About Page (30 sec)
1. Click **"ℹ️ About"** in sidebar
2. Show:
   - **Agent Architecture** — 5 cards at the top
   - **Pipeline Flow** — input to output
   - **Feasibility** — *"All production-ready tech, no custom model training"*
   - **AI Evolution** — *"ARIA is Generation 3: Agentic AI"*

### 2:45 — Closing (15 sec)
> "ARIA doesn't replace doctors — it gives them a second opinion in 5 seconds,
> with built-in bias checks and no one left behind. Every component uses
> production-ready tech — the innovation is in how we connect them.
> Thank you."

---

## 🚨 Backup Plan (if API fails)
- If Gemini quota is exhausted: switch model in the dropdown
- If all models fail: have a **screen recording** ready as backup
- If internet is down: show the About page (works offline) + explain the architecture

## 💡 Judge Questions — Prepared Answers

| Likely Question | Answer |
|----------------|--------|
| "Is this using real patient data?" | "We use simulated data. The system is compatible with MIMIC-III format for real hospital deployment." |
| "Can it handle multiple patients?" | "Yes, each patient gets a unique ID and their history persists in SQLite across visits." |
| "What about LLM hallucinations?" | "We mitigate with confidence scores, differential diagnosis (alternatives), and the explainability agent as a second check." |
| "Why not use LangChain?" | "Simplicity. Plain Python functions are easier to debug, audit, and explain. No black-box frameworks." |
| "How is this different from ChatGPT?" | "ChatGPT is one model doing everything. ARIA is 4 specialized agents with temporal memory, bias detection, and structured clinical output." |
