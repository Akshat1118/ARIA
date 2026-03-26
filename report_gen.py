import os
from datetime import datetime
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import io

class ARIA_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 18)
        self.set_text_color(40, 40, 40)
        self.cell(190, 10, 'ARIA Clinical Decision Support Report', align='C')
        self.ln(12)
        self.set_draw_color(200, 200, 200)
        self.line(10, 22, 200, 22)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(190, 10, f'Page {self.page_no()}', align='C')

def generate_pdf_report(patient_data, results):
    def safetext(text):
        if not text: return ""
        text = str(text)
        text = text.replace('✅', '[OK]').replace('⚠️', '[FLAG]').replace('🛑', '[CRITICAL]').replace('🚨', '[ALERT]')
        # Strip remaining non-latin1 characters which crash basic FPDF fonts
        return text.encode('latin-1', 'ignore').decode('latin-1')

    # Set orientation, unit, and format explicitly
    pdf = ARIA_PDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    
    # Standard usable width
    W = 190 
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(W, 5, f"Generated: {timestamp}", ln=True, align='C')
    pdf.ln(5)

    # 1. Patient Information
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "1. Patient Information", ln=True)
    pdf.ln(2)

    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(40, 40, 40)
    
    pi_data = [
        ("Name", patient_data.get('name', 'N/A')),
        ("Patient ID", patient_data.get('patient_id', 'N/A')),
        ("Age/Gender", f"{patient_data.get('age', 'N/A')} / {patient_data.get('gender', 'N/A')}"),
        ("Symptoms", patient_data.get('symptoms', 'N/A')),
        ("Vitals", patient_data.get('vitals', 'N/A')),
        ("History", patient_data.get('history', 'N/A'))
    ]
    
    for label, val in pi_data:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 7, safetext(f"{label}:"), ln=False)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(W-30, 7, safetext(val))
        
    pdf.ln(5)

    # 2. Diagnostic Assessment
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "2. Diagnostic & Triage Assessment", ln=True)
    pdf.ln(2)

    diag_res = results.get('diagnosis', {})
    triage_res = results.get('triage', {})
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 7, "Primary Diagnosis:", ln=False)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(W-40, 7, safetext(f"{diag_res.get('diagnosis', 'N/A')} ({diag_res.get('confidence', 0)}% confidence)"))
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 7, "Triage Level:", ln=False)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(W-40, 7, safetext(f"{triage_res.get('triage_level', 'N/A')} (Urgency: {triage_res.get('urgency_score', 0)}/10)"))

    pdf.set_font("helvetica", "B", 10)
    pdf.cell(40, 7, "Reasoning:", ln=False)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(W-40, 7, safetext(triage_res.get('reasoning', 'N/A')))

    # Conflict check
    if results.get('conflict', False):
        pdf.set_text_color(200, 0, 0)
        pdf.set_font("helvetica", "B", 10)
        audit = " | ".join(triage_res.get('conflict_audit', ["Triage adjusted for safety."]))
        pdf.multi_cell(W, 7, safetext(f"CONFLICT RESOLVED: {audit}"))
        pdf.set_text_color(40, 40, 40)

    pdf.ln(5)

    # Chart
    img_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            img_path = tmpfile.name
            plt.figure(figsize=(5, 2.5))
            plt.bar(['Confidence', 'Urgency', 'Data Qual'], 
                    [float(diag_res.get('confidence', 0)), 
                     float(triage_res.get('urgency_score', 0)) * 10, 
                     float(diag_res.get('data_quality_score', 0))],
                    color=['#2ca02c', '#d62728', '#1f77b4'])
            plt.ylim(0, 100)
            plt.title('Patient Clinical metrics')
            plt.tight_layout()
            plt.savefig(img_path, format='png', dpi=150)
            plt.close()
        pdf.image(img_path, x=40, w=130)
    except:
        pass
    finally:
        if img_path and os.path.exists(img_path):
            try: os.remove(img_path)
            except: pass

    # 3. Fairness & Summary
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "3. Fairness & Doctor Summary", ln=True)
    pdf.ln(2)

    bias_repo = results.get('bias_report', {})
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(W, 6, safetext(f"Gender Bias: {bias_repo.get('gender_bias', {}).get('status', 'N/A')}"))
    pdf.multi_cell(W, 6, safetext(f"Age Bias: {bias_repo.get('age_bias', {}).get('status', 'N/A')}"))
    
    if bias_repo.get('cascading_amplification', False):
        pdf.set_text_color(255, 100, 0)
        pdf.set_font("helvetica", "B", 10)
        pdf.multi_cell(W, 7, safetext("CASCADING BIAS FLAG DETECTED"))
        pdf.set_text_color(40, 40, 40)

    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(W, 7, "Doctor Summary:", ln=True)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(W, 6, safetext(results.get('doctor_summary', 'N/A')))

    # 4. Memory
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "4. Temporal Memory Audit", ln=True)
    pdf.ln(2)
    pdf.set_font("courier", size=8)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(W, 4, safetext(results.get('memory_summary', 'No history.')))

    # 5. Treatment Plan
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "5. Treatment Plan", ln=True)
    pdf.ln(2)

    treat = results.get('treatment_plan', {})
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(W, 7, "Immediate Actions:", ln=True)
    pdf.set_font("helvetica", size=10)
    for action in treat.get('immediate_actions', ['N/A']):
        pdf.multi_cell(W, 6, safetext(f"  - {action}"))

    if treat.get('medications'):
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(W, 7, "Medications:", ln=True)
        pdf.set_font("helvetica", size=10)
        for med in treat['medications']:
            if isinstance(med, dict):
                med_str = f"  - {med.get('name', 'N/A')} | {med.get('dosage', '')} | {med.get('route', '')} | {med.get('frequency', '')}"
            else:
                med_str = f"  - {med}"
            pdf.multi_cell(W, 6, safetext(med_str))

    if treat.get('monitoring'):
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 7, "Monitoring:", ln=False)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(W-30, 6, safetext(treat['monitoring']))

    if treat.get('precautions'):
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(30, 7, "Precautions:", ln=False)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(W-30, 6, safetext(treat['precautions']))

    # 6. Specialist Referral
    pdf.ln(8)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "6. Specialist Referral", ln=True)
    pdf.ln(2)

    ref = results.get('referral', {})
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(40, 40, 40)
    ref_needed = "Yes" if ref.get('referral_needed') else "No"
    pdf.multi_cell(W, 6, safetext(f"Referral Needed: {ref_needed}"))
    if ref.get('departments'):
        pdf.multi_cell(W, 6, safetext(f"Departments: {', '.join(ref['departments'])}"))
    pdf.multi_cell(W, 6, safetext(f"Urgency: {ref.get('urgency', 'N/A')}"))
    pdf.multi_cell(W, 6, safetext(f"Reasoning: {ref.get('reasoning', 'N/A')}"))

    # 7. Patient-Friendly Summary
    pdf.ln(8)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "7. Patient-Friendly Summary", ln=True)
    pdf.ln(2)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(W, 6, safetext(results.get('patient_message', 'N/A')))

    # 8. Follow-Up Care Plan
    pdf.ln(8)
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(W, 10, "8. Follow-Up Care Plan", ln=True)
    pdf.ln(2)

    fu = results.get('follow_up', {})
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(40, 40, 40)

    if fu.get('discharge_instructions'):
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(W, 7, "Discharge Instructions:", ln=True)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(W, 6, safetext(fu['discharge_instructions']))

    if fu.get('follow_up_timeline'):
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(W, 7, "Follow-Up Timeline:", ln=True)
        pdf.set_font("helvetica", size=10)
        for step in fu['follow_up_timeline']:
            if isinstance(step, dict):
                pdf.multi_cell(W, 6, safetext(f"  [{step.get('timeframe', '')}] {step.get('action', '')}"))
            else:
                pdf.multi_cell(W, 6, safetext(f"  - {step}"))

    if fu.get('red_flags'):
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(W, 7, "Red Flags (Return to ED if):", ln=True)
        pdf.set_font("helvetica", size=10)
        pdf.set_text_color(40, 40, 40)
        for flag in fu['red_flags']:
            pdf.multi_cell(W, 6, safetext(f"  [!] {flag}"))

    if fu.get('lifestyle_advice'):
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(30, 7, "Lifestyle:", ln=False)
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(W-30, 6, safetext(fu['lifestyle_advice']))

    return bytes(pdf.output())
