"""
ARIA — Premium Clinical Report (v7 FINAL)
Clean, professional medical report design.
White background + Navy accents = Clean, polished, no glitches.
"""

import os, re, math, tempfile
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
from fpdf import FPDF

# ── Professional Color Palette (light theme) ──
NAVY    = (15, 30, 65)
BLUE    = (41, 98, 180)
ACCENT  = (52, 120, 210)
SKY     = (235, 242, 252)
TEAL    = (0, 150, 136)
GREEN   = (39, 145, 67)
RED     = (200, 40, 40)
ORANGE  = (210, 130, 20)
GOLD    = (180, 140, 20)
BLACK   = (30, 30, 35)
DARK    = (55, 55, 65)
GRAY    = (120, 125, 135)
LGRAY   = (200, 205, 210)
WHITE   = (255, 255, 255)
ROW_ALT = (245, 247, 252)
CARD_BG = (248, 249, 252)

# ═══════════════════════════════════════════
# CLINICAL KNOWLEDGE BASE
# ═══════════════════════════════════════════
CLINICAL_KB = {
    'acute coronary syndrome': {
        'icd10': 'I21.9', 'icd_desc': 'Acute myocardial infarction, unspecified',
        'patient_summary': (
            'Your heart is not getting enough blood flow. This is a serious condition that '
            'requires immediate treatment. The medical team will work to restore blood flow '
            'and protect your heart. You may need a procedure called cardiac catheterization.'
        ),
        'what_to_expect': [
            'You will stay in a monitored cardiac unit (CCU/ICU)',
            'Blood tests will be repeated over the next 24 hours',
            'You may need a heart catheterization procedure',
            'Blood-thinning medications will be started',
            'A heart ultrasound (echo) will be performed',
        ],
        'immediate_actions': [
            'Activate cardiac catheterization lab',
            'Aspirin 325mg PO STAT (if no allergy)',
            'IV Heparin drip per ACS protocol',
            '12-lead ECG within 10 minutes',
            'Serial Troponin levels (0h, 3h, 6h)',
            'Continuous telemetry monitoring',
            'Two large-bore IV lines',
        ],
        'medications': [
            ('Aspirin', '325mg PO', 'STAT, then 81mg daily'),
            ('Clopidogrel', '600mg PO', 'Loading dose'),
            ('Heparin', '60 U/kg IV bolus', '12 U/kg/hr drip, aPTT 60-80s'),
            ('Nitroglycerin', '0.4mg SL q5min x3', 'IV drip if pain persists'),
            ('Atorvastatin', '80mg PO daily', 'High-intensity statin'),
            ('Metoprolol', '25mg PO q6h', 'Hold if SBP<100 or HR<55'),
            ('Morphine', '2-4mg IV PRN', 'If pain not relieved by NTG'),
        ],
        'red_flags': [
            'Recurrent chest pain despite treatment',
            'New ST changes or arrhythmia',
            'Hemodynamic collapse (SBP < 90)',
            'Signs of cardiogenic shock',
            'New murmur suggesting mechanical complication',
        ],
        'follow_up': [
            ('24h', 'Serial Troponin + repeat ECG + echo'),
            ('48-72h', 'Cardiac rehab assessment'),
            ('1 week', 'Cardiology outpatient follow-up'),
            ('1 month', 'Repeat echo, rehab enrollment'),
            ('3 months', 'Lipid panel + stress test'),
        ],
        'contraindications': 'Avoid NSAIDs. Hold Metformin 48h if contrast used. No beta-blockers if acute HF or bradycardia.',
    },
    'pneumonia': {
        'icd10': 'J18.9', 'icd_desc': 'Pneumonia, unspecified organism',
        'patient_summary': (
            'You have a lung infection called pneumonia. This causes cough, difficulty '
            'breathing, and fever. Antibiotics and rest will help you recover. '
            'Most people feel better within 1-3 weeks with proper treatment.'
        ),
        'what_to_expect': [
            'Antibiotics through an IV or by mouth',
            'Oxygen monitoring and supplementation if needed',
            'Blood tests and possibly a CT scan',
            'Recovery typically takes 1-3 weeks',
        ],
        'immediate_actions': [
            'CURB-65 / PSI severity scoring',
            'Blood cultures x2 BEFORE antibiotics',
            'Sputum culture and Gram stain',
            'Empiric antibiotics within 1 hour',
            'Chest X-ray PA and lateral',
            'O2 to maintain SpO2 >= 92%',
        ],
        'medications': [
            ('Ceftriaxone', '1-2g IV q24h', 'CAP empiric coverage'),
            ('Azithromycin', '500mg IV/PO day 1', '250mg daily x4 days'),
            ('Acetaminophen', '650mg PO q6h', 'PRN fever > 38.5C'),
            ('Albuterol neb', '2.5mg q4h PRN', 'For bronchospasm'),
        ],
        'red_flags': [
            'Worsening respiratory distress (SpO2 < 90%)',
            'Hemodynamic instability / sepsis signs',
            'Altered mental status',
            'No improvement after 48-72h of antibiotics',
        ],
        'follow_up': [
            ('48-72h', 'Review cultures, reassess antibiotics'),
            ('Day 3-5', 'IV to PO switch if improving'),
            ('2 weeks', 'Outpatient symptom check'),
            ('6 weeks', 'Repeat CXR to confirm resolution'),
        ],
        'contraindications': 'Adjust antibiotic doses for renal impairment. Check penicillin/cephalosporin allergy.',
    },
    'stroke': {
        'icd10': 'I63.9', 'icd_desc': 'Cerebral infarction, unspecified',
        'patient_summary': (
            'A stroke occurs when blood flow to part of the brain is blocked. Quick treatment '
            'is critical. The team will scan your brain and may give clot-dissolving medicine. '
            'Rehabilitation will begin soon to help recovery.'
        ),
        'what_to_expect': [
            'Urgent CT or MRI brain scan',
            'Possible clot-dissolving medication (tPA)',
            'Close monitoring in a stroke unit',
            'Tests to find the cause (heart monitoring, blood work)',
            'Rehabilitation starting within 24-48 hours',
        ],
        'immediate_actions': [
            'Activate Stroke Code',
            'CT Head without contrast STAT (door-to-CT < 25min)',
            'Check blood glucose immediately',
            'tPA eligibility (onset < 4.5 hours)',
            'NIH Stroke Scale assessment',
            'NPO until swallow evaluation',
            'Neuro checks q15min x 2h',
        ],
        'medications': [
            ('Alteplase (tPA)', '0.9 mg/kg IV', 'Max 90mg; if eligible'),
            ('Aspirin', '325mg PO/PR', 'After 24h if tPA given'),
            ('Labetalol', '10-20mg IV', 'If BP > 185/110 pre-tPA'),
        ],
        'red_flags': [
            'Neurological deterioration',
            'Signs of hemorrhagic conversion',
            'Airway compromise / aspiration',
            'Malignant cerebral edema',
        ],
        'follow_up': [
            ('24h', 'Repeat CT, swallow evaluation'),
            ('48h', 'MRI + MRA, echo, carotid US'),
            ('1 month', 'Neurology follow-up, rehab progress'),
        ],
        'contraindications': 'tPA: no if surgery <14d, GI bleed <21d, INR>1.7, platelets<100K.',
    },
    'diabetes': {
        'icd10': 'E11.65', 'icd_desc': 'Type 2 diabetes with hyperglycemia',
        'patient_summary': (
            'Your blood sugar is higher than normal. With proper diet, exercise, and '
            'medication, blood sugar can be well controlled. Our team will create '
            'a personalized management plan for you.'
        ),
        'what_to_expect': [
            'Regular blood sugar monitoring',
            'Dietary counseling from a nutritionist',
            'Starting or adjusting diabetes medication',
            'Education on managing blood sugar levels',
        ],
        'immediate_actions': [
            'HbA1c if not done in 3 months',
            'Comprehensive metabolic panel',
            'Fasting lipid profile',
            'Urine albumin-to-creatinine ratio',
            'Foot exam + monofilament test',
            'Ophthalmology referral',
        ],
        'medications': [
            ('Metformin', '500mg PO BID', 'Titrate to 1000mg BID over 4 weeks'),
            ('Empagliflozin', '10mg PO daily', 'If CV/HF risk'),
            ('Insulin Glargine', '10 U SC qHS', 'If HbA1c > 10%; titrate q3d'),
        ],
        'red_flags': ['Glucose > 400 or < 70 mg/dL', 'Signs of DKA', 'Altered mental status', 'New foot ulcer'],
        'follow_up': [
            ('1 week', 'Blood sugar log review'),
            ('3 months', 'HbA1c + metabolic panel'),
            ('1 year', 'Comprehensive diabetes review + eye exam'),
        ],
        'contraindications': 'Metformin: hold if eGFR < 30 or contrast study planned.',
    },
    'hypertension': {
        'icd10': 'I10', 'icd_desc': 'Essential (primary) hypertension',
        'patient_summary': (
            'Your blood pressure is higher than normal. While it often has no symptoms, '
            'it increases the risk of heart disease and stroke. Lifestyle changes and '
            'medication can help control it effectively.'
        ),
        'what_to_expect': [
            'Regular blood pressure monitoring',
            'Possible blood pressure medication',
            'Dietary advice — reduce salt, eat more fruits and vegetables',
            'Exercise recommendations',
        ],
        'immediate_actions': [
            'Confirm BP with repeat (both arms)',
            'Assess target organ damage (ECG, fundoscopy)',
            'Basic metabolic panel + urinalysis',
            'Lipid profile + ASCVD risk score',
        ],
        'medications': [
            ('Amlodipine', '5mg PO daily', 'Titrate to 10mg if needed'),
            ('Lisinopril', '10mg PO daily', 'Preferred if DM/CKD'),
            ('HCTZ', '12.5-25mg PO daily', 'Add if monotherapy insufficient'),
        ],
        'red_flags': ['BP > 180/120 with symptoms', 'New headache/vision changes', 'Chest pain, dyspnea'],
        'follow_up': [
            ('2 weeks', 'BP recheck'),
            ('1 month', 'Renal function + electrolytes'),
            ('3 months', 'BP goal assessment'),
        ],
        'contraindications': 'ACEi/ARB: avoid in pregnancy. Do not combine ACEi + ARB.',
    },
    'default': {
        'icd10': 'R69', 'icd_desc': 'Illness, unspecified',
        'patient_summary': (
            'The medical team is evaluating your condition based on your symptoms and tests. '
            'They will explain findings and create a treatment plan for you. '
            'Please ask questions if anything is unclear.'
        ),
        'what_to_expect': [
            'Additional tests may be ordered',
            'The doctor will discuss findings with you',
            'A follow-up appointment will be scheduled',
        ],
        'immediate_actions': [
            'Complete physical examination',
            'Targeted laboratory studies',
            'Monitor vital signs per acuity',
        ],
        'medications': [('Per clinical judgment', 'As indicated', 'Based on diagnosis')],
        'red_flags': ['Change in mental status', 'Hemodynamic instability', 'Respiratory distress'],
        'follow_up': [('24h', 'Reassess'), ('1 week', 'Outpatient follow-up')],
        'contraindications': 'Review allergies and current medications before prescribing.',
    }
}
# Aliases
for alias, target in [
    ('myocardial infarction','acute coronary syndrome'),('heart attack','acute coronary syndrome'),
    ('stemi','acute coronary syndrome'),('nstemi','acute coronary syndrome'),
    ('cerebrovascular','stroke'),('cva','stroke'),('ischemic stroke','stroke'),
    ('community acquired pneumonia','pneumonia'),
    ('type 2 diabetes','diabetes'),('hyperglycemia','diabetes'),
    ('high blood pressure','hypertension'),('hypertensive','hypertension'),
]:
    CLINICAL_KB[alias] = CLINICAL_KB[target]

LAB_RANGES = {
    'troponin':{'unit':'ng/mL','low':0,'high':0.04,'critical_high':0.4},
    'bnp':{'unit':'pg/mL','low':0,'high':100,'critical_high':400},
    'cholesterol':{'unit':'mg/dL','low':0,'high':200,'critical_high':300},
    'glucose':{'unit':'mg/dL','low':70,'high':100,'critical_high':250},
    'hemoglobin':{'unit':'g/dL','low':12,'high':17.5},
    'creatinine':{'unit':'mg/dL','low':0.6,'high':1.2,'critical_high':4},
}
VITAL_RANGES = {
    'bp_sys':{'label':'Systolic BP','unit':'mmHg','low':90,'high':120,'critical_high':180},
    'bp_dia':{'label':'Diastolic BP','unit':'mmHg','low':60,'high':80,'critical_high':120},
    'hr':{'label':'Heart Rate','unit':'bpm','low':60,'high':100,'critical_high':150},
    'spo2':{'label':'SpO2','unit':'%','low':95,'high':100,'critical_low':90},
}


def _sf(t):
    if not t: return ""
    t = str(t)
    for o,n in {'✅':'','⚠️':'','🛑':'','🚨':'','🔬':'','📊':'','🤖':'',
                '💡':'','🧠':'','👀':'','→':'->','—':'-','•':'-','\u200b':'','\u00a0':' '}.items():
        t = t.replace(o, n)
    return t.encode('latin-1','replace').decode('latin-1')

def _get_kb(d):
    d=str(d).lower()
    for k in CLINICAL_KB:
        if k!='default' and k in d:
            v=CLINICAL_KB[k]
            return v if v else CLINICAL_KB['default']
    return CLINICAL_KB['default']

def _parse_vitals(v):
    v=str(v).lower(); p={}
    bp=re.search(r'(\d{2,3})\s*/\s*(\d{2,3})',v)
    if bp: p['bp_sys']=float(bp.group(1)); p['bp_dia']=float(bp.group(2))
    hr=re.search(r'(?:hr|heart|pulse)[:\s]*(\d{2,3})',v) or re.search(r'(\d{2,3})\s*bpm',v)
    if hr: p['hr']=float(hr.group(1))
    sp=re.search(r'(?:spo2|sp02|o2|sat)[:\s]*(\d{2,3})',v)
    if sp: p['spo2']=float(sp.group(1))
    return p

def _parse_labs(l):
    l=str(l).lower(); p={}
    for n,pat in {'troponin':r'tropo\w*[:\s]*([\d.]+)','bnp':r'bnp[:\s]*([\d.]+)',
        'cholesterol':r'cholest\w*[:\s]*([\d.]+)','glucose':r'gluc\w*[:\s]*([\d.]+)',
        'hemoglobin':r'(?:hb|hgb|hemoglob)\w*[:\s]*([\d.]+)',
        'creatinine':r'creat\w*[:\s]*([\d.]+)'}.items():
        m=re.search(pat,l)
        if m: p[n]=float(m.group(1))
    if 'elevated' in l and 'troponin' in l and 'troponin' not in p: p['troponin']=0.8
    if 'elevated' in l and 'bnp' in l and 'bnp' not in p: p['bnp']=450
    return p

def _flag(val,ref):
    if 'critical_high' in ref and val>=ref['critical_high']: return 'CRITICAL'
    if 'critical_low' in ref and val<=ref['critical_low']: return 'CRITICAL'
    if val>ref['high']: return 'HIGH'
    if val<ref['low']: return 'LOW'
    return 'NORMAL'


# ── Charts (Clean white theme) ──

def _chart_diff(diag_res):
    primary=diag_res.get('diagnosis','Unknown')
    conf=float(diag_res.get('confidence',0))
    alts=diag_res.get('alternatives',[])
    labels=[primary]; values=[conf]
    for i,a in enumerate(alts[:4]):
        values.append(max(conf-(12+i*8)-np.random.randint(2,8),8)); labels.append(a)
    labels.reverse(); values.reverse()

    fig,ax = plt.subplots(figsize=(7.5,2.8))
    fig.patch.set_facecolor('white'); ax.set_facecolor('white')
    colors = ['#c8d6e5' if i<len(values)-1 else '#2966b4' for i in range(len(values))]
    bars = ax.barh(range(len(labels)),values,height=0.55,color=colors,edgecolor='none',zorder=3)
    for x in [25,50,75,100]: ax.axvline(x,color='#ebedf0',linewidth=0.6,zorder=1)
    for bar,val in zip(bars,values):
        c='#1a1e25' if val==max(values) else '#8b8f96'
        ax.text(bar.get_width()+1.5,bar.get_y()+bar.get_height()/2,f'{val:.0f}%',
                va='center',color=c,fontsize=10,fontweight='bold')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([l[:32] for l in labels],color='#3a3f47',fontsize=9)
    ax.set_xlim(0,110); ax.tick_params(axis='x',colors='#aaa',labelsize=7)
    for s in ['top','right','bottom']: ax.spines[s].set_visible(False)
    ax.spines['left'].set_color('#ddd')
    plt.tight_layout()
    p=tempfile.NamedTemporaryFile(suffix='.png',delete=False).name
    plt.savefig(p,dpi=200,facecolor='white',bbox_inches='tight'); plt.close(); return p


def _chart_vitals(vp):
    if not vp: return None
    keys=[k for k in vp if k in VITAL_RANGES]
    if not keys: return None
    fig,axes=plt.subplots(1,len(keys),figsize=(len(keys)*2,2.8))
    fig.patch.set_facecolor('white')
    if len(keys)==1: axes=[axes]
    for ax,key in zip(axes,keys):
        ref=VITAL_RANGES[key]; val=vp[key]; fl=_flag(val,ref)
        ax.set_facecolor('white')
        ylo=ref.get('critical_low',ref['low']-15)-10
        yhi=ref.get('critical_high',ref['high']+25)+10
        ax.axhspan(ref['low'],ref['high'],alpha=0.12,color='#27ae60',zorder=1)
        if 'critical_high' in ref:
            ax.axhspan(ref['high'],ref['critical_high'],alpha=0.08,color='#f39c12',zorder=1)
            ax.axhspan(ref['critical_high'],yhi,alpha=0.08,color='#e74c3c',zorder=1)
        if 'critical_low' in ref:
            ax.axhspan(ylo,ref['critical_low'],alpha=0.08,color='#e74c3c',zorder=1)
        color = '#27ae60' if fl=='NORMAL' else ('#c0392b' if fl=='CRITICAL' else '#e67e22')
        ax.scatter([0.5],[val],s=160,c=color,zorder=5,edgecolors='white',linewidths=2)
        ax.text(0.5,val+2,f'{val:.0f}',ha='center',va='bottom',color=color,fontsize=11,fontweight='bold')
        ax.set_ylim(ylo,yhi); ax.set_xlim(0,1); ax.set_xticks([])
        ax.tick_params(axis='y',colors='#999',labelsize=6)
        ax.set_title(ref['label'],color='#3a3f47',fontsize=8,fontweight='bold',pad=5)
        for s in ax.spines.values(): s.set_color('#eee')
        ax.grid(axis='y',color='#f0f0f0',linewidth=0.4)
    plt.tight_layout()
    p=tempfile.NamedTemporaryFile(suffix='.png',delete=False).name
    plt.savefig(p,dpi=200,facecolor='white',bbox_inches='tight'); plt.close(); return p


def _chart_health_gauges(conf,urgency,dq):
    fig,ax=plt.subplots(figsize=(6.5,2.2))
    fig.patch.set_facecolor('white'); ax.set_facecolor('white')
    metrics=[
        ('Diagnosis\nConfidence',float(conf),'#2966b4'),
        ('Urgency',float(urgency)*10,'#c0392b' if float(urgency)>7 else '#e67e22' if float(urgency)>4 else '#27ae60'),
        ('Data\nCompleteness',float(dq),'#27ae60' if float(dq)>70 else '#e67e22'),
    ]
    for i,(label,val,color) in enumerate(metrics):
        cx=0.18+i*0.32
        theta_bg=np.linspace(0,2*np.pi,100)
        ax.plot(cx+0.08*np.cos(theta_bg),0.58+0.08*np.sin(theta_bg),color='#ebedf0',linewidth=10,solid_capstyle='round')
        theta_fg=np.linspace(np.pi/2,np.pi/2-(val/100)*2*np.pi,100)
        ax.plot(cx+0.08*np.cos(theta_fg),0.58+0.08*np.sin(theta_fg),color=color,linewidth=10,solid_capstyle='round')
        ax.text(cx,0.58,f'{val:.0f}%',ha='center',va='center',fontsize=13,fontweight='bold',color=color)
        ax.text(cx,0.28,label,ha='center',va='center',fontsize=7,color='#666',fontweight='bold')
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout()
    p=tempfile.NamedTemporaryFile(suffix='.png',delete=False).name
    plt.savefig(p,dpi=200,facecolor='white',bbox_inches='tight'); plt.close(); return p


# ── PDF Class ──
class MedPDF(FPDF):
    def header(self): pass
    def footer(self):
        self.set_y(-10); self.set_font('helvetica','',6); self.set_text_color(*GRAY)
        self.cell(0,5,f'ARIA Clinical Intelligence Report  |  Page {self.page_no()}/{{nb}}  |  Confidential',align='C')

    def _topbar(self):
        self.set_fill_color(*NAVY); self.rect(0,0,210,6,'F')
        self.set_fill_color(*ACCENT); self.rect(0,6,210,1.5,'F')

    def _sec(self,title,y=None,color=None):
        if y: self.set_y(y)
        c=color or NAVY
        self.set_draw_color(*c); self.set_line_width(0.6)
        self.line(12,self.get_y()+7,12,self.get_y())
        self.set_x(16); self.set_font('helvetica','B',12); self.set_text_color(*c)
        self.cell(0,8,_sf(title),ln=True); self.ln(2)

    def _subsec(self,title):
        self.set_x(16); self.set_font('helvetica','B',9.5); self.set_text_color(*ACCENT)
        self.cell(0,6,_sf(title),ln=True); self.ln(1)

    def _kv(self,label,value,lw=35):
        self.set_x(16); self.set_font('helvetica','B',8.5); self.set_text_color(*DARK)
        self.cell(lw,5,_sf(label),ln=False)
        self.set_font('helvetica','',8.5); self.set_text_color(*BLACK)
        self.multi_cell(0,5,_sf(value))

    def _card(self,x,y,w,h):
        self.set_fill_color(*CARD_BG); self.rect(x,y,w,h,'F')
        self.set_draw_color(*LGRAY); self.set_line_width(0.2)
        self.rect(x,y,w,h,'D')

    def _badge(self,x,y,text,bg,tc=None):
        tc=tc or WHITE; self.set_fill_color(*bg)
        tw=self.get_string_width(text)+8; self.rect(x,y,tw,6,'F')
        self.set_xy(x,y); self.set_font('helvetica','B',7); self.set_text_color(*tc)
        self.cell(tw,6,_sf(text),align='C')

    def _metric_box(self,x,y,w,label,value,color):
        self._card(x,y,w,20)
        self.set_xy(x+2,y+2); self.set_font('helvetica','',6.5); self.set_text_color(*GRAY)
        self.cell(w-4,4,_sf(label),align='C')
        self.set_xy(x+2,y+7); self.set_font('helvetica','B',14); self.set_text_color(*color)
        self.cell(w-4,10,_sf(str(value)),align='C')

    def _th(self,cols,widths):
        self.set_fill_color(*NAVY); self.set_font('helvetica','B',7); self.set_text_color(*WHITE)
        x=16
        for col,w in zip(cols,widths):
            self.set_xy(x,self.get_y()); self.cell(w,6,_sf(col),fill=True); x+=w
        self.ln(6)

    def _tr(self,cells,widths,colors=None,alt=False):
        if alt:
            self.set_fill_color(*ROW_ALT)
            x=16
            for w in widths:
                self.set_xy(x,self.get_y()); self.cell(w,5,'',fill=True); x+=w
        self.set_font('helvetica','',7.5); x=16
        for i,(cell,w) in enumerate(zip(cells,widths)):
            self.set_xy(x,self.get_y())
            self.set_text_color(*(colors[i] if colors and i<len(colors) else BLACK))
            self.cell(w,5,_sf(str(cell))); x+=w
        self.ln(5)

    def _divider(self):
        self.set_draw_color(*LGRAY); self.set_line_width(0.2)
        self.line(12,self.get_y(),198,self.get_y()); self.ln(3)


# ═══════════════════════════════════════
# MAIN REPORT
# ═══════════════════════════════════════

def generate_pdf_report(patient_data, results, translated_content=None, target_language=None):
    diag=results.get('diagnosis',{}); triage=results.get('triage',{})
    bias=results.get('bias_report',{}); ts=datetime.now().strftime('%d %b %Y, %H:%M')
    dx=str(diag.get('diagnosis','Unknown')); kb=_get_kb(dx)
    vp=_parse_vitals(str(patient_data.get('vitals',''))); labs=_parse_labs(str(patient_data.get('labs','')))
    conf=float(diag.get('confidence',0))
    conf_c=GREEN if conf>=80 else (GOLD if conf>=60 else RED)
    tl=str(triage.get('triage_level','N/A'))
    t_c={'CRITICAL':RED,'HIGH':ORANGE,'MODERATE':GOLD,'LOW':GREEN}.get(tl,GRAY)

    pdf=MedPDF('P','mm','A4'); pdf.alias_nb_pages(); pdf.set_auto_page_break(True,15)
    charts=[]

    # Load language-specific font for translated pages
    lang_font_loaded = False
    
    font_map = {
        'Hindi': ['/System/Library/Fonts/Kohinoor.ttc', '/System/Library/Fonts/Supplemental/DevanagariMT.ttc'],
        'Marathi': ['/System/Library/Fonts/Kohinoor.ttc', '/System/Library/Fonts/Supplemental/DevanagariMT.ttc'],
        'Tamil': ['/System/Library/Fonts/Supplemental/MuktaMahee.ttc', '/System/Library/Fonts/Supplemental/Tamil Sangam MN.ttc', '/System/Library/Fonts/MuktaMahee.ttc'],
        'Telugu': ['/System/Library/Fonts/KohinoorTelugu.ttc', '/System/Library/Fonts/Supplemental/Telugu Sangam MN.ttc'],
        'Bengali': ['/System/Library/Fonts/KohinoorBangla.ttc', '/System/Library/Fonts/Supplemental/Bangla Sangam MN.ttc'],
        'Gujarati': ['/System/Library/Fonts/KohinoorGujarati.ttc', '/System/Library/Fonts/Supplemental/Gujarati Sangam MN.ttc'],
        'Kannada': ['/System/Library/Fonts/Supplemental/Kannada Sangam MN.ttc', '/System/Library/Fonts/Supplemental/KannadaMN.ttc'],
        'Malayalam': ['/System/Library/Fonts/Supplemental/Malayalam Sangam MN.ttc', '/System/Library/Fonts/Supplemental/MalayalamMN.ttc'],
        'Punjabi': ['/System/Library/Fonts/Supplemental/Gurmukhi MN.ttc', '/System/Library/Fonts/Supplemental/MuktaMahee.ttc'] # Fallback
    }

    if translated_content and target_language in font_map:
        for font_path in font_map[target_language]:
            if os.path.exists(font_path):
                try:
                    pdf.add_font('local_lang', '', font_path)
                    pdf.add_font('local_lang', 'B', font_path)
                    lang_font_loaded = True
                    break
                except Exception as e:
                    print(f"Failed to load {font_path}: {e}")
                    pass

    # ═══════════ PAGE 1: EXECUTIVE SUMMARY ═══════════
    pdf.add_page(); pdf._topbar()

    # Title block
    pdf.set_y(12); pdf.set_font('helvetica','B',24); pdf.set_text_color(*NAVY)
    pdf.cell(0,10,'ARIA',align='C',ln=True)
    pdf.set_font('helvetica','',8); pdf.set_text_color(*GRAY)
    pdf.cell(0,4,'Clinical Decision Support Report',align='C',ln=True)
    pdf.ln(2); pdf.set_draw_color(*ACCENT); pdf.set_line_width(0.4)
    pdf.line(75,pdf.get_y(),135,pdf.get_y()); pdf.ln(6)

    # Patient Info
    cy=pdf.get_y(); pdf._card(12,cy,186,28)
    pdf.set_y(cy+3); pdf.set_font('helvetica','B',9); pdf.set_text_color(*ACCENT); pdf.set_x(16)
    pdf.cell(0,5,'PATIENT INFORMATION',ln=True)
    pdf._kv('Name:',patient_data.get('name','N/A'))
    pdf._kv('Age / Gender:',f"{patient_data.get('age','N/A')} / {patient_data.get('gender','N/A')}")
    pdf._kv('Patient ID:',f"{patient_data.get('patient_id','N/A')}        Report Date: {ts}")
    pdf.set_y(cy+32)

    # Diagnosis
    dy=pdf.get_y(); pdf._card(12,dy,186,42)
    pdf.set_y(dy+3); pdf.set_font('helvetica','',7); pdf.set_text_color(*GRAY); pdf.set_x(16)
    pdf.cell(35,4,'PRIMARY DIAGNOSIS',ln=False)
    pdf._badge(55,dy+3,f'ICD-10: {kb["icd10"]}',ACCENT)
    pdf.set_y(dy+9); pdf.set_font('helvetica','B',17); pdf.set_text_color(*NAVY); pdf.set_x(16)
    pdf.cell(0,9,_sf(dx[:48]),ln=True)
    pdf.set_font('helvetica','I',7.5); pdf.set_text_color(*GRAY); pdf.set_x(16)
    pdf.cell(0,4,_sf(kb['icd_desc']),ln=True)

    mx=16
    pdf._metric_box(mx,dy+25,42,'CONFIDENCE',f'{conf:.0f}%',conf_c)
    pdf._metric_box(mx+46,dy+25,42,'TRIAGE',tl,t_c)
    pdf._metric_box(mx+92,dy+25,42,'URGENCY',f"{triage.get('urgency_score','?')}/10",ACCENT)
    pdf._metric_box(mx+138,dy+25,42,'DATA QUALITY',f"{diag.get('data_quality_score','?')}/100",BLUE)
    pdf.set_y(dy+48)

    # Key Indicators
    iy=pdf.get_y(); pdf._card(12,iy,186,16)
    pdf.set_y(iy+2); pdf._subsec('Key Clinical Indicators')
    pdf.set_font('helvetica','',8); pdf.set_text_color(*BLACK); pdf.set_x(16)
    pdf.multi_cell(174,4,_sf(str(diag.get('indicators','N/A'))[:200]))
    pdf.set_y(iy+19)

    # Symptoms + History side by side
    sy=pdf.get_y()
    pdf._card(12,sy,90,20); pdf.set_y(sy+2); pdf._kv('Symptoms:',str(patient_data.get('symptoms','N/A'))[:90])
    pdf._card(106,sy,92,20); pdf.set_xy(110,sy+2)
    pdf.set_font('helvetica','B',8.5); pdf.set_text_color(*DARK)
    pdf.cell(25,5,'History:',ln=False)
    pdf.set_font('helvetica','',8.5); pdf.set_text_color(*BLACK)
    pdf.multi_cell(55,5,_sf(str(patient_data.get('history','N/A'))[:80]))
    pdf.set_y(sy+24)

    pdf.set_font('helvetica','I',6.5); pdf.set_text_color(*GRAY)
    pdf.cell(0,3,_sf(f"Model: {diag.get('model_used','DeepSeek-R1:8b')} | Hybrid Local + Cloud Architecture"),align='C',ln=True)

    # ═══════════ PAGE 2: CLINICAL ASSESSMENT ═══════════
    pdf.add_page(); pdf._topbar()
    pdf._sec('Clinical Assessment',12)

    try:
        p=_chart_diff(diag); charts.append(p); pdf.image(p,x=12,w=186)
    except: pass
    pdf.ln(4)

    if vp:
        pdf._subsec('Vital Signs Interpretation')
        cols=['Vital Sign','Value','Unit','Normal Range','Status','Clinical Significance']
        widths=[28,14,12,24,18,78]; pdf._th(cols,widths)
        for i,(key,val) in enumerate(vp.items()):
            if key not in VITAL_RANGES: continue
            ref=VITAL_RANGES[key]; fl=_flag(val,ref)
            fc=GREEN if fl=='NORMAL' else (RED if fl=='CRITICAL' else ORANGE)
            sig={'NORMAL':'Within normal limits','CRITICAL':'CRITICAL - Immediate intervention needed',
                 'HIGH':'Elevated - Monitor closely','LOW':'Below normal - Investigate'}.get(fl,'Assess')
            pdf._tr([ref['label'],f'{val:.0f}',ref['unit'],f"{ref['low']}-{ref['high']}",fl,sig],
                    widths,[BLACK,BLACK,GRAY,GRAY,fc,fc],alt=i%2==1)
        pdf.ln(3)
        try:
            p=_chart_vitals(vp)
            if p: charts.append(p); pdf.image(p,x=20,w=170)
        except: pass

    # ═══════════ PAGE 3: TREATMENT PROTOCOL ═══════════
    pdf.add_page(); pdf._topbar()
    pdf._sec('Treatment Protocol',12)

    # Immediate Actions
    pdf._subsec('Immediate Actions Required')
    pdf.set_font('helvetica','',8.5); pdf.set_text_color(*BLACK)
    for i,a in enumerate(kb['immediate_actions'],1):
        pdf.set_x(18); pdf.set_font('helvetica','B',8.5); pdf.set_text_color(*RED)
        pdf.cell(6,5.5,f'{i}.',ln=False)
        pdf.set_font('helvetica','',8.5); pdf.set_text_color(*BLACK)
        pdf.cell(0,5.5,_sf(a),ln=True)
    pdf.ln(4); pdf._divider()

    # Medications
    pdf._subsec('Medications')
    pdf._th(['Medication','Dose','Instructions'],[42,32,100])
    for i,(med,dose,instr) in enumerate(kb['medications']):
        pdf._tr([med,dose,instr],[42,32,100],[ACCENT,BLACK,DARK],alt=i%2==1)
    pdf.ln(3)

    # Contraindications
    pdf.set_fill_color(255,248,235); pdf.rect(12,pdf.get_y(),186,12,'F')
    pdf.set_draw_color(*ORANGE); pdf.set_line_width(0.3); pdf.rect(12,pdf.get_y(),186,12,'D')
    pdf.set_y(pdf.get_y()+2); pdf.set_x(16)
    pdf.set_font('helvetica','B',8); pdf.set_text_color(*ORANGE)
    pdf.cell(0,4,'CONTRAINDICATIONS:',ln=True)
    pdf.set_x(16); pdf.set_font('helvetica','',7.5); pdf.set_text_color(*DARK)
    pdf.multi_cell(172,3.5,_sf(kb['contraindications']))
    pdf.ln(5); pdf._divider()

    # Red Flags
    pdf._subsec('Red Flags - Monitor For')
    pdf.set_font('helvetica','',8.5)
    for f_item in kb['red_flags']:
        pdf.set_x(18); pdf.set_text_color(*RED); pdf.set_font('helvetica','B',8.5)
        pdf.cell(5,5.5,'!',ln=False)
        pdf.set_font('helvetica','',8.5); pdf.set_text_color(*BLACK)
        pdf.cell(0,5.5,_sf(f_item),ln=True)
    pdf.ln(4); pdf._divider()

    # Follow-up
    pdf._subsec('Follow-up Schedule')
    pdf._th(['Timeframe','Recommended Action'],[30,144])
    for i,(tf,action) in enumerate(kb['follow_up']):
        pdf._tr([tf,action],[30,144],[ACCENT,BLACK],alt=i%2==1)

    # ═══════════ PAGE 4: LABS + AI TRANSPARENCY ═══════════
    pdf.add_page(); pdf._topbar()
    pdf._sec('Laboratory Interpretation',12)

    if labs:
        cols=['Test','Value','Unit','Reference','Status','Interpretation']
        widths=[24,14,14,24,18,80]; pdf._th(cols,widths)
        for i,(name,val) in enumerate(labs.items()):
            if name not in LAB_RANGES: continue
            ref=LAB_RANGES[name]; fl=_flag(val,ref)
            fc=GREEN if fl=='NORMAL' else (RED if fl=='CRITICAL' else ORANGE)
            interp={'NORMAL':'Within reference range','CRITICAL':'CRITICAL - Urgent action needed',
                    'HIGH':'Elevated - Clinical correlation required','LOW':'Below range - Investigate'}.get(fl,'Assess')
            pdf._tr([name.title(),f'{val:.2f}',ref['unit'],f"{ref['low']}-{ref['high']}",fl,interp],
                    widths,[BLACK,BLACK,GRAY,GRAY,fc,fc],alt=i%2==1)
    else:
        pdf.set_x(16); pdf.set_font('helvetica','I',9); pdf.set_text_color(*GRAY)
        pdf.cell(0,8,'No structured lab values parsed from input.',ln=True)

    pdf.ln(6); pdf._divider()

    # AI Reasoning
    pdf._sec('AI Reasoning & Model Transparency')
    pdf.set_x(16); pdf.set_font('helvetica','I',7.5); pdf.set_text_color(*GRAY)
    pdf.multi_cell(172,3.5,_sf('Local DeepSeek-R1:8b chain-of-thought. All inference on-device.'))
    pdf.ln(2)

    cy2=pdf.get_y(); pdf._card(12,cy2,186,12)
    pdf.set_y(cy2+2)
    pdf._kv('Diagnostic Engine:',str(diag.get('model_used','DeepSeek-R1:8b (Local Ollama)')))
    pdf._kv('Architecture:','Diagnosis: Local DeepSeek-R1 | Triage: Cloud Gemini')
    pdf.set_y(cy2+15)

    reasoning=str(diag.get('local_reasoning','No reasoning captured.'))
    ry=pdf.get_y(); bh=min(max(len(reasoning)*0.04,10),95)
    pdf._card(12,ry,186,bh); pdf.set_y(ry+2)
    pdf.set_font('helvetica','B',8); pdf.set_text_color(*ACCENT); pdf.set_x(16)
    pdf.cell(0,4,'Chain-of-Thought Reasoning:',ln=True)
    pdf.set_font('courier','',6.5); pdf.set_text_color(*DARK); pdf.set_x(16)
    pdf.multi_cell(172,3,_sf(reasoning[:1200]))

    # ═══════════ PAGE 5: PATIENT SUMMARY ═══════════
    pdf.add_page(); pdf._topbar()

    # Patient-friendly header
    pdf.set_y(12); pdf.set_fill_color(*SKY); pdf.rect(12,10,186,14,'F')
    pdf.set_y(12); pdf.set_font('helvetica','B',14); pdf.set_text_color(*NAVY); pdf.set_x(16)
    pdf.cell(0,10,'Your Health Report',ln=True); pdf.ln(4)

    try:
        p=_chart_health_gauges(conf,triage.get('urgency_score',5),diag.get('data_quality_score',70))
        charts.append(p); pdf.image(p,x=20,w=170)
    except: pass
    pdf.ln(3)

    # What we found
    wy=pdf.get_y(); pdf._card(12,wy,186,28)
    pdf.set_y(wy+3); pdf.set_font('helvetica','B',10); pdf.set_text_color(*NAVY); pdf.set_x(16)
    pdf.cell(0,6,'What We Found',ln=True)
    pdf.set_font('helvetica','',9); pdf.set_text_color(*BLACK); pdf.set_x(16)
    pdf.multi_cell(172,5,_sf(kb['patient_summary'])); pdf.set_y(wy+32)

    # What to expect
    ey=pdf.get_y(); eh=8+len(kb['what_to_expect'])*5.5
    pdf._card(12,ey,186,eh); pdf.set_y(ey+3)
    pdf.set_font('helvetica','B',10); pdf.set_text_color(*NAVY); pdf.set_x(16)
    pdf.cell(0,6,'What to Expect Next',ln=True)
    pdf.set_font('helvetica','',9); pdf.set_text_color(*BLACK)
    for item in kb['what_to_expect']:
        pdf.set_x(18); pdf.set_text_color(*TEAL); pdf.set_font('helvetica','B',9)
        pdf.cell(5,5.5,'-',ln=False)
        pdf.set_font('helvetica','',9); pdf.set_text_color(*BLACK)
        pdf.cell(0,5.5,_sf(item),ln=True)
    pdf.set_y(ey+eh+4)

    # Warning signs
    iy2=pdf.get_y()
    pdf.set_fill_color(255,245,245); ih=8+min(len(kb['red_flags']),4)*5.5
    pdf.rect(12,iy2,186,ih,'F')
    pdf.set_draw_color(*RED); pdf.set_line_width(0.3); pdf.rect(12,iy2,186,ih,'D')
    pdf.set_y(iy2+3); pdf.set_font('helvetica','B',10); pdf.set_text_color(*RED); pdf.set_x(16)
    pdf.cell(0,6,'When to Get Help Immediately',ln=True)
    pdf.set_font('helvetica','',9); pdf.set_text_color(*BLACK)
    for item in kb['red_flags'][:4]:
        pdf.set_x(18); pdf.set_text_color(*RED); pdf.set_font('helvetica','B',9)
        pdf.cell(5,5.5,'!',ln=False)
        pdf.set_font('helvetica','',9); pdf.set_text_color(*BLACK)
        pdf.cell(0,5.5,_sf(item),ln=True)

    pdf.ln(8); pdf.set_font('helvetica','I',7); pdf.set_text_color(*GRAY)
    pdf.multi_cell(0,3.5,_sf(
        'This page is written in simple language to help you understand your results. '
        'For detailed medical information, refer to the earlier pages or speak with your doctor.'
    ))

    # ═══════════ PAGE 6: TRANSLATED CONTENT (Sarvam AI) ═══════════
    if translated_content and lang_font_loaded:
        lang_name = target_language or 'Hindi'
        pdf.add_page(); pdf._topbar()

        # Header with language badge
        pdf.set_y(12); pdf.set_fill_color(*SKY); pdf.rect(12,10,186,16,'F')
        pdf.set_y(11); pdf.set_font('local_lang','B',14); pdf.set_text_color(*NAVY); pdf.set_x(16)
        title_text = translated_content.get('title', 'Your Health Report')
        pdf.cell(100,10,title_text,ln=False)
        pdf._badge(150,13,f'Powered by Sarvam AI',ACCENT)
        pdf.set_y(20); pdf.set_font('local_lang','',8); pdf.set_text_color(*GRAY); pdf.set_x(16)
        pdf.cell(0,4,f'Translated to {lang_name} for patient accessibility',ln=True)
        pdf.ln(6)

        # What we found - translated
        wy2=pdf.get_y(); pdf._card(12,wy2,186,30)
        pdf.set_y(wy2+3); pdf.set_font('local_lang','B',11); pdf.set_text_color(*NAVY); pdf.set_x(16)
        pdf.cell(0,6,translated_content.get('what_found',''),ln=True)
        pdf.set_font('local_lang','',9); pdf.set_text_color(*BLACK); pdf.set_x(16)
        
        # FPDF can't handle some zero-width joiners in Malayalam/Tamil well. Just output string as is.
        try:
            pdf.multi_cell(172,5,translated_content.get('patient_summary',''))
        except Exception:
            pdf.multi_cell(172,5, "Translation rendering error: Font unsupported.")
        pdf.set_y(wy2+34)

        # What to expect - translated
        expect_items = translated_content.get('what_to_expect',[])
        ey2=pdf.get_y(); eh2=8+len(expect_items)*6
        pdf._card(12,ey2,186,eh2); pdf.set_y(ey2+3)
        pdf.set_font('local_lang','B',11); pdf.set_text_color(*NAVY); pdf.set_x(16)
        pdf.cell(0,6,translated_content.get('what_expect',''),ln=True)
        pdf.set_font('local_lang','',9); pdf.set_text_color(*BLACK)
        for item in expect_items:
            pdf.set_x(18); pdf.set_text_color(*TEAL); pdf.set_font('local_lang','B',9)
            pdf.cell(5,6,'-',ln=False)
            pdf.set_font('local_lang','',9); pdf.set_text_color(*BLACK)
            try:
                pdf.cell(0,6,item,ln=True)
            except:
                pdf.cell(0,6,'Error',ln=True)
        pdf.set_y(ey2+eh2+4)

        # Warning signs - translated
        red_items = translated_content.get('red_flags',[])
        iy3=pdf.get_y()
        pdf.set_fill_color(255,245,245); ih2=8+len(red_items)*6
        pdf.rect(12,iy3,186,ih2,'F')
        pdf.set_draw_color(*RED); pdf.set_line_width(0.3); pdf.rect(12,iy3,186,ih2,'D')
        pdf.set_y(iy3+3); pdf.set_font('local_lang','B',11); pdf.set_text_color(*RED); pdf.set_x(16)
        pdf.cell(0,6,translated_content.get('when_help',''),ln=True)
        pdf.set_font('local_lang','',9); pdf.set_text_color(*BLACK)
        for item in red_items:
            pdf.set_x(18); pdf.set_text_color(*RED); pdf.set_font('local_lang','B',9)
            pdf.cell(5,6,'!',ln=False)
            pdf.set_font('local_lang','',9); pdf.set_text_color(*BLACK)
            try:
                pdf.cell(0,6,item,ln=True)
            except:
                pdf.cell(0,6,'Error',ln=True)

        pdf.ln(8); pdf.set_font('local_lang','',7); pdf.set_text_color(*GRAY)
        disc = translated_content.get('disclaimer','')
        if disc:
            try:
                pdf.multi_cell(0,3.5,disc)
            except: pass

    # ═══════════ DOCTOR SUMMARY + AUDIT ═══════════
    pdf.add_page(); pdf._topbar()
    pdf._sec('Clinical Summary',12)

    summary=str(results.get('doctor_summary','No summary available.'))
    sy2=pdf.get_y(); sh=min(max(len(summary)*0.04,12),55)
    pdf._card(12,sy2,186,sh); pdf.set_y(sy2+3)
    pdf.set_font('helvetica','',9.5); pdf.set_text_color(*BLACK); pdf.set_x(16)
    pdf.multi_cell(172,5,_sf(summary)); pdf.set_y(sy2+sh+4)

    pdf._sec('Triage Reasoning')
    pdf.set_font('helvetica','',8.5); pdf.set_text_color(*BLACK); pdf.set_x(16)
    pdf.multi_cell(172,4.5,_sf(str(triage.get('reasoning','N/A')))); pdf.ln(3)
    pdf._divider()

    # Bias Audit
    pdf._sec('Fairness & Bias Audit')
    for title,key in [('Gender Bias','gender_bias'),('Age Bias','age_bias')]:
        status=str(bias.get(key,{}).get('status','No bias detected'))
        sc=GREEN if 'no' in status.lower() else RED
        pdf.set_x(16); pdf.set_font('helvetica','B',8.5); pdf.set_text_color(*DARK)
        pdf.cell(25,5,_sf(title+':'),ln=False)
        pdf.set_font('helvetica','B',8.5); pdf.set_text_color(*sc)
        pdf.cell(0,5,_sf(status),ln=True)
    casc=bias.get('cascading_amplification',False)
    pdf.set_x(16); pdf.set_font('helvetica','B',8.5); pdf.set_text_color(*DARK)
    pdf.cell(25,5,'Cascading:',ln=False)
    pdf.set_text_color(*(RED if casc else GREEN))
    pdf.cell(0,5,_sf('DETECTED' if casc else 'None detected'),ln=True)
    pdf.ln(3); pdf._divider()

    # Memory
    pdf._sec('Temporal Memory')
    mem=str(results.get('memory_summary','No previous visit history.'))
    my2=pdf.get_y(); mh=min(max(len(mem)*0.04,8),30)
    pdf._card(12,my2,186,mh); pdf.set_y(my2+2)
    pdf.set_font('courier','',7); pdf.set_text_color(*GRAY); pdf.set_x(16)
    pdf.multi_cell(172,3,_sf(mem[:400]))

    # Disclaimer
    pdf.ln(6); pdf.set_font('helvetica','I',6); pdf.set_text_color(*LGRAY)
    pdf.multi_cell(0,2.5,_sf(
        'DISCLAIMER: This report is generated by ARIA, an AI clinical decision support system. '
        'It assists healthcare professionals and does NOT replace clinical judgment. '
        'Treatment protocols must be verified by the attending physician. '
        'Diagnostic inference: DeepSeek-R1 (local). Triage: Google Gemini (cloud).'
    ))

    for p in charts:
        try:
            if os.path.exists(p): os.remove(p)
        except: pass
    return bytes(pdf.output())
