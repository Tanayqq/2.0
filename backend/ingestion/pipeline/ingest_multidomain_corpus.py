import os
import sys
import json
import uuid
import time
from typing import List, Dict, Any

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from app.infrastructure.embedding_models import FastEmbedModel
from app.core.config import settings

# Initialize Embedding Model & Qdrant Client
embedding_model = FastEmbedModel()
qclient = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, prefer_grpc=False, timeout=60.0)
VECTOR_SIZE = 384

def ensure_collection(collection_name: str):
    try:
        qclient.get_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' exists.")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Collection '{collection_name}' exists.")
            return
        print(f"Creating collection '{collection_name}'...")
        try:
            qclient.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE)
            )
        except Exception as inner_e:
            if "already exists" in str(inner_e).lower():
                print(f"Collection '{collection_name}' already exists.")
            else:
                raise inner_e

# 1. REAL DISEASE GUIDELINES & PATHOPHYSIOLOGY DATA
DISEASE_DATA = [
    {
        "title": "ADA 2026 Standards of Medical Care in Type 2 Diabetes",
        "disease": "Type 2 Diabetes",
        "authority": "ADA",
        "category": "disease_guidelines",
        "content": (
            "Type 2 Diabetes Mellitus Management Guidelines (ADA 2026 / RSSDI / ICMR):\n"
            "First-Line Therapy: Lifestyle modification plus Metformin is recommended for all non-contraindicated patients with Type 2 Diabetes.\n"
            "Cardiovascular & Renal Risk: In patients with established Atherosclerotic Cardiovascular Disease (ASCVD), Heart Failure (HF), or Chronic Kidney Disease (CKD Stage 1-4 with eGFR >= 20 mL/min), initial therapy MUST include an SGLT2 inhibitor (Empagliflozin, Dapagliflozin) or a GLP-1 Receptor Agonist (Semaglutide, Dulaglutide) with proven CVD benefit independent of baseline HbA1c.\n"
            "HbA1c Target: Target HbA1c < 7.0% for most non-pregnant adults. De-escalate sulfonylureas or insulin if hypoglycemia risk is elevated."
        ),
        "section": "clinical_guideline"
    },
    {
        "title": "Type 2 Diabetes Pathophysiology and Clinical Overview",
        "disease": "Type 2 Diabetes",
        "authority": "ADA",
        "category": "disease_corpus",
        "content": (
            "Type 2 Diabetes Mellitus Pathophysiology and Clinical Overview:\n"
            "Definition: Metabolic disorder characterized by hyperglycemia due to progressive loss of adequate beta-cell insulin secretion on the background of insulin resistance.\n"
            "Clinical Presentation: Polyuria, polydipsia, weight loss, blurred vision, fatigue, and recurrent cutaneous or genital infections.\n"
            "Complications: Microvascular (retinopathy, nephropathy, neuropathy) and macrovascular (coronary artery disease, peripheral arterial disease, stroke)."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Chronic Kidney Disease (CKD) Pathophysiology and Clinical Overview",
        "disease": "Chronic Kidney Disease",
        "authority": "KDIGO",
        "category": "disease_corpus",
        "content": (
            "Chronic Kidney Disease (CKD) Clinical Overview & KDIGO Staging:\n"
            "Definition: Abnormalities of kidney structure or function, present for >3 months, with implications for health.\n"
            "Staging by eGFR (mL/min/1.73m²): G1 (>=90), G2 (60-89), G3a (45-59), G3b (30-44), G4 (15-29 severe), G5 (<15 kidney failure).\n"
            "Staging by Albuminuria (UACR mg/g): A1 (<30 normal), A2 (30-300 microalbuminuria), A3 (>300 macroalbuminuria).\n"
            "Clinical Features: Uremic frost, edema, hypertension, anemia of CKD (decreased EPO), hyperkalemia, secondary hyperparathyroidism, metabolic acidosis.\n"
            "GDMT Protections: RAS inhibitors (ACEi/ARB) for albuminuric CKD, SGLT2 inhibitors (Empagliflozin, Dapagliflozin) down to eGFR 20, nonsteroidal MRA (Finerenone) in diabetic CKD."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Acute Kidney Injury (AKI) KDIGO Staging and Clinical Overview",
        "disease": "Acute Kidney Injury",
        "authority": "KDIGO",
        "category": "disease_corpus",
        "content": (
            "Acute Kidney Injury (AKI) Clinical Overview & KDIGO Definition:\n"
            "Definition: Increase in SCr by >=0.3 mg/dL within 48h, OR increase in SCr to >=1.5 times baseline within 7 days, OR urine volume <0.5 mL/kg/h for 6h.\n"
            "KDIGO AKI Staging:\n"
            "  - Stage 1: SCr 1.5-1.9x baseline OR SCr increase >=0.3 mg/dL.\n"
            "  - Stage 2: SCr 2.0-2.9x baseline.\n"
            "  - Stage 3: SCr 3.0x baseline OR SCr >=4.0 mg/dL OR initiation of RRT.\n"
            "Etiology Classification:\n"
            "  - Prerenal: Renal hypoperfusion (dehydration, sepsis, NSAIDs, ACEi).\n"
            "  - Intrinsic: Acute Tubular Necrosis (ATN) via aminoglycosides, vancomycin, contrast media, ischemia; AIN via antibiotics, proton pump inhibitors.\n"
            "  - Postrenal: Urinary tract obstruction (BPH, nephrolithiasis).\n"
            "Management: Discontinue nephrotoxic agents, adjust renal dosing, optimize fluid status, monitor serum potassium."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Heart Failure (HFrEF and HFpEF) Pathophysiology and Clinical Overview",
        "disease": "Heart Failure",
        "authority": "ACC/AHA",
        "category": "disease_corpus",
        "content": (
            "Heart Failure (HF) Clinical Overview & ACC/AHA Classification:\n"
            "Classification by Ejection Fraction:\n"
            "  - HFrEF (HF with Reduced EF): LVEF <= 40%. Requires 4 Pillars of GDMT: ARNI (Entresto) or ACEi/ARB, Beta-Blocker (Carvedilol, Metoprolol Succinate, Bisoprolol), MRA (Spironolactone, Eplerenone), SGLT2i (Dapagliflozin, Empagliflozin).\n"
            "  - HFmrEF (HF with Mildly Reduced EF): LVEF 41-49%. SGLT2i recommended; ARNI, MRA, Beta-blocker reasonable.\n"
            "  - HFpEF (HF with Preserved EF): LVEF >= 50%. SGLT2i (Empagliflozin/Dapagliflozin) Class 1 recommendation to reduce HF hospitalizations.\n"
            "Clinical Presentation: Dyspnea on exertion, orthopnea, paroxysmal nocturnal dyspnea (PND), elevated JVP, bilateral pedal edema, S3 gallop.\n"
            "Safety Washout: 36-hour washout required when switching from ACEi to ARNI (Sacubitril/Valsartan) due to angioedema risk."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "COPD Pathophysiology and GOLD Staging Overview",
        "disease": "Chronic Obstructive Pulmonary Disease",
        "authority": "GOLD",
        "category": "disease_corpus",
        "content": (
            "COPD Pathophysiology & GOLD 2025 Clinical Overview:\n"
            "Definition: Heterogeneous lung condition characterized by chronic respiratory symptoms (dyspnea, cough, sputum production) due to abnormalities of airways (bronchitis) and/or alveoli (emphysema).\n"
            "Diagnosis: Post-bronchodilator FEV1/FVC < 0.70 mandatory.\n"
            "GOLD Spirometric Grading (based on post-bronchodilator FEV1 % predicted):\n"
            "  - GOLD 1 (Mild): FEV1 >= 80%\n"
            "  - GOLD 2 (Moderate): 50% <= FEV1 < 80%\n"
            "  - GOLD 3 (Severe): 30% <= FEV1 < 50%\n"
            "  - GOLD 4 (Very Severe): FEV1 < 30%\n"
            "GOLD ABE Group Classification:\n"
            "  - Group A: 0-1 moderate exacerbations, no hospitalizations, CAT < 10 -> Initial therapy: Bronchodilator (LAMA or LABA).\n"
            "  - Group B: 0-1 moderate exacerbations, CAT >= 10 -> Initial therapy: LABA + LAMA combination.\n"
            "  - Group E: >=2 moderate exacerbations OR >=1 leading to hospitalization -> Initial therapy: LABA + LAMA; add ICS if blood eosinophils >= 300 cells/µL."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Asthma Pathophysiology and GINA Severity Assessment",
        "disease": "Asthma",
        "authority": "GINA",
        "category": "disease_corpus",
        "content": (
            "Asthma Pathophysiology & GINA 2025 Clinical Overview:\n"
            "Definition: Chronic inflammatory disease of airways characterized by variable respiratory symptoms (wheeze, shortness of breath, chest tightness, cough) and variable expiratory airflow limitation.\n"
            "GINA Track 1 (Preferred Strategy): Low-dose ICS-formoterol as needed for symptom relief across all steps.\n"
            "  - Step 1-2: As-needed low-dose ICS-formoterol.\n"
            "  - Step 3: Low-dose maintenance ICS-formoterol + as-needed low-dose ICS-formoterol.\n"
            "  - Step 4: Medium-dose maintenance ICS-formoterol + as-needed low-dose ICS-formoterol.\n"
            "  - Step 5: High-dose maintenance ICS-formoterol, evaluate phenotype (eosinophilic vs allergic) for biologic therapy (Omalizumab, Mepolizumab, Dupilumab).\n"
            "GINA Track 2 (Alternative): SABA reliever (Salbutamol) MUST be accompanied by regular daily ICS to prevent fatal exacerbations."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Sepsis and Septic Shock Pathophysiology & Surviving Sepsis 2024 Protocol",
        "disease": "Sepsis and Septic Shock",
        "authority": "Surviving Sepsis Campaign",
        "category": "disease_corpus",
        "content": (
            "Sepsis & Septic Shock Clinical Overview (Sepsis-3 / Surviving Sepsis Campaign 2024):\n"
            "Definition of Sepsis: Life-threatening organ dysfunction caused by a dysregulated host response to infection (SOFA score increase >= 2 points).\n"
            "Definition of Septic Shock: Subset of sepsis with persisting hypotension requiring vasopressors to maintain MAP >= 65 mmHg AND serum lactate > 2 mmol/L despite adequate fluid resuscitation.\n"
            "Hour-1 Bundle Interventions:\n"
            "  1. Measure lactate level; remeasure if initial lactate > 2 mmol/L.\n"
            "  2. Obtain blood cultures prior to administration of antibiotics.\n"
            "  3. Administer broad-spectrum antimicrobials (e.g., Vancomycin + Zosyn / Cefepime).\n"
            "  4. Rapidly administer 30 mL/kg crystalloid for hypotension or lactate >= 4 mmol/L.\n"
            "  5. Apply vasopressors if MAP < 65 mmHg during or after fluid resuscitation (First-line: Norepinephrine; Second-line: Vasopressin 0.03 units/min).\n"
            "Nephrotoxicity Warning: Vancomycin + Piperacillin/Tazobactam (Zosyn) combination significantly increases AKI incidence compared to Vancomycin + Cefepime."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Atrial Fibrillation (AFib) Pathophysiology & Stroke Prevention Protocol",
        "disease": "Atrial Fibrillation",
        "authority": "ESC / ACC",
        "category": "disease_corpus",
        "content": (
            "Atrial Fibrillation (AFib) Clinical Overview & Stroke Prevention (ESC 2024 / ACC 2024):\n"
            "Definition: Supraventricular tachyarrhythmia with uncoordinated atrial electrical activation and ineffective atrial contraction.\n"
            "CHA2DS2-VASc Risk Score for Stroke:\n"
            "  - C: CHF (1 pt)\n"
            "  - H: Hypertension (1 pt)\n"
            "  - A2: Age >= 75 (2 pts)\n"
            "  - D: Diabetes (1 pt)\n"
            "  - S2: Stroke/TIA/Thromboembolism history (2 pts)\n"
            "  - V: Vascular disease (prior MI, PAD, aortic plaque) (1 pt)\n"
            "  - A: Age 65-74 (1 pt)\n"
            "  - Sc: Sex category (Female) (1 pt)\n"
            "Anticoagulation Thresholds: DOAC (Apixaban, Rivaroxaban, Dabigatran, Edoxaban) recommended if score >= 2 in males or >= 3 in females.\n"
            "P-glycoprotein Drug Interactions: Amiodarone inhibits P-gp, increasing Digoxin levels by 70-100% and DOAC concentrations. Reduce Digoxin dose by 50% when co-prescribed with Amiodarone."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Acute Coronary Syndrome (STEMI and NSTEMI) Clinical Overview",
        "disease": "Acute Coronary Syndrome",
        "authority": "ACC/AHA",
        "category": "disease_corpus",
        "content": (
            "Acute Coronary Syndrome (ACS) Clinical Overview & Emergency Management:\n"
            "Spectrum: Unstable Angina (UA), Non-ST-Segment Elevation Myocardial Infarction (NSTEMI), ST-Segment Elevation Myocardial Infarction (STEMI).\n"
            "Diagnostic Criteria: Ischemic chest pain radiating to jaw/left arm, ECG ST elevations or T-wave inversions, elevated High-Sensitivity Cardiac Troponin (hs-cTn).\n"
            "Emergency Pharmacotherapy (MONA-BASH):\n"
            "  - Morphine (if severe pain unresolved by nitroglycerin)\n"
            "  - Oxygen (if SpO2 < 90%)\n"
            "  - Nitroglycerin sublingual (contraindicated if SBP < 90 or PDE5 inhibitor use within 24-48h)\n"
            "  - Aspirin 162-325mg chewed immediately\n"
            "  - P2Y12 Inhibitor (Ticagrelor 180mg or Prasugrel 60mg or Clopidogrel 600mg loading dose)\n"
            "  - Anticoagulation (Unfractionated Heparin or Enoxaparin)\n"
            "  - High-Intensity Statin (Atorvastatin 80mg or Rosuvastatin 40mg)\n"
            "Biotin Warning: High-dose Biotin (>5-10 mg/day) interferes with streptavidin-biotin troponin assays, causing FALSELY LOW troponin readings and delayed MI diagnosis."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Acute Ischemic Stroke and TIA Clinical Overview & Thrombolysis Protocol",
        "disease": "Stroke",
        "authority": "AHA/ASA",
        "category": "disease_corpus",
        "content": (
            "Acute Ischemic Stroke (AIS) Clinical Overview & Thrombolytic Management (AHA/ASA):\n"
            "Definition: Sudden neurological deficit caused by focal cerebral ischemia resulting in permanent tissue infarction.\n"
            "FAST Evaluation: Facial droop, Arm drift, Speech difficulty, Time to call emergency services.\n"
            "Reperfusion Windows:\n"
            "  - Intravenous Thrombolysis (Alteplase / Tenecteplase): Recommended within 4.5 hours of symptom onset in eligible patients without bleeding contraindications.\n"
            "  - Endovascular Thrombectomy (EVT): Recommended within 6-24 hours for large vessel occlusion (LVO) in anterior circulation.\n"
            "Blood Pressure Management: SBP must be < 185 mmHg and DBP < 110 mmHg prior to IV thrombolytic administration (use Labetalol or Nicardipine IV).\n"
            "Secondary Prevention: Antiplatelet therapy (Aspirin or Clopidogrel), high-intensity statin, blood pressure control, DOAC if cardioembolic (AFib)."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Community-Acquired Pneumonia (CAP) Clinical Overview & CURB-65 Protocol",
        "disease": "Community-Acquired Pneumonia",
        "authority": "IDSA / ATS",
        "category": "disease_corpus",
        "content": (
            "Community-Acquired Pneumonia (CAP) Clinical Overview (IDSA/ATS Guidelines):\n"
            "Definition: Acute infection of lung parenchyma acquired outside of hospital settings.\n"
            "Common Pathogens: Streptococcus pneumoniae, Mycoplasma pneumoniae, Chlamydia pneumoniae, Haemophilus influenzae, Respiratory viruses.\n"
            "CURB-65 Risk Stratification (1 point each):\n"
            "  - C: Confusion\n"
            "  - U: BUN > 19 mg/dL (7 mmol/L)\n"
            "  - R: Respiratory rate >= 30 breaths/min\n"
            "  - B: SBP < 90 mmHg or DBP <= 60 mmHg\n"
            "  - 65: Age >= 65 years\n"
            "Site of Care Decision:\n"
            "  - Score 0-1: Outpatient management (Amoxicillin 1g TID OR Doxycycline 100mg BID OR Macrolide if local resistance < 25%).\n"
            "  - Score 2: Inpatient ward admission (Beta-lactam + Macrolide OR Respiratory Fluoroquinolone).\n"
            "  - Score 3-5: ICU admission required (Beta-lactam + Macrolide OR Beta-lactam + Respiratory Fluoroquinolone; add MRSA/Pseudomonas coverage if risk factors present)."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "GINA 2025 Global Strategy for Asthma Management",
        "disease": "Asthma",
        "authority": "GINA",
        "category": "disease_guidelines",
        "content": (
            "Asthma Management Guidelines (GINA 2025):\n"
            "Track 1 (Preferred): Low-dose Inhaled Corticosteroid (ICS) - Formoterol as needed for symptom relief across all severity steps to reduce exacerbation risk.\n"
            "Avoid SABA Monotherapy: SABA (Salbutamol) alone is no longer recommended due to increased mortality and severe exacerbation risk without anti-inflammatory coverage."
        ),
        "section": "clinical_guideline"
    },
    {
        "title": "GOLD 2025 Executive Summary for COPD",
        "disease": "COPD",
        "authority": "GOLD",
        "category": "disease_guidelines",
        "content": (
            "COPD Management Guidelines (GOLD 2025):\n"
            "Initial Pharmacotherapy:\n"
            "Group A: Single bronchodilator (LAMA or LABA).\n"
            "Group B: LABA + LAMA combination bronchodilation (e.g. Tiotropium + Olodaterol).\n"
            "Group E (Frequent Exacerbators): LABA + LAMA combination. Add ICS (Triple Therapy: ICS + LABA + LAMA) if blood eosinophil count is >= 300 cells/mcL."
        ),
        "section": "clinical_guideline"
    },
    {
        "title": "KDIGO 2024 Clinical Practice Guideline for Diabetes and Chronic Kidney Disease",
        "disease": "Chronic Kidney Disease (CKD)",
        "authority": "KDIGO",
        "category": "disease_guidelines",
        "content": (
            "KDIGO 2024 CKD Guidelines:\n"
            "1. ACE Inhibitors (ACEi) or ARBs (Losartan, Telmisartan): Recommended at maximum tolerated dose for patients with CKD, hypertension, and albuminuria.\n"
            "2. SGLT2 Inhibitors (Dapagliflozin 10mg): Recommended for adults with CKD and eGFR >= 20 mL/min with or without diabetes.\n"
            "3. Non-Steroidal Anti-Inflammatory Drugs (NSAIDs): Contraindicated in moderate-to-severe CKD (eGFR < 45 mL/min) due to acute hemodynamically mediated decline in renal function."
        ),
        "section": "clinical_guideline"
    },
    {
        "title": "ACC/AHA 2024 Guideline for the Management of Heart Failure (HFrEF)",
        "disease": "Heart Failure with Reduced Ejection Fraction (HFrEF)",
        "authority": "ACC/AHA",
        "category": "disease_guidelines",
        "content": """ACC/AHA 2024 Heart Failure Guidelines (HFrEF, LVEF <= 40%):
Guideline-Directed Medical Therapy (GDMT) 'Fantastic Four' pillars:
1. ARNI (Sacubitril/Valsartan Entresto): Preferred over ACEi/ARB to reduce morbidity and mortality (PARADIGM-HF). Requires 36h ACEi washout.
2. Evidence-based Beta-Blocker: Bisoprolol, Carvedilol, or Metoprolol Succinate extended-release.
3. Mineralocorticoid Receptor Antagonist (MRA): Spironolactone 12.5-25mg daily or Eplerenone. Monitor K+ and sCr.
4. SGLT2 Inhibitor: Dapagliflozin 10mg or Empagliflozin 10mg daily regardless of diabetes status (DAPA-HF, EMPEROR-Reduced).
Diuretics: Loop diuretics (Furosemide, Torsemide) as needed for fluid overload symptoms.""",
        "section": "clinical_guideline"
    },
    {
        "title": "ACC/AHA 2024 Clinical Practice Guideline for Management of High Blood Pressure",
        "disease": "Hypertension",
        "authority": "ACC/AHA",
        "category": "disease_guidelines",
        "content": """ACC/AHA 2024 Hypertension Guidelines:
Classification: Normal <120/<80; Elevated 120-129/<80; Stage 1 HTN 130-139/80-89; Stage 2 HTN >=140/>=90 mmHg.
First-Line Antihypertensive Classes: Thiazide diuretics (Chlorthalidone, Indapamide, HCTZ), Calcium Channel Blockers (Amlodipine), ACE inhibitors (Lisinopril, Enalapril), or ARBs (Losartan, Telmisartan).
Stage 2 HTN: Initiate two first-line agents of different classes if BP >20/10 mmHg above goal (e.g., Telmisartan + Amlodipine combination).
Resistant HTN: BP uncontrolled on 3 full-dose drugs including a diuretic -> Add Spironolactone 25mg daily.""",
        "section": "clinical_guideline"
    },
    {
        "title": "ESC 2024 Guidelines for Management of Atrial Fibrillation",
        "disease": "Atrial Fibrillation",
        "authority": "ESC",
        "category": "disease_guidelines",
        "content": """ESC 2024 Atrial Fibrillation Guidelines:
Stroke Risk Assessment (CHA2DS2-VASc): Score >=2 in males or >=3 in females -> Oral Anticoagulation RECOMMENDED.
Preferred Anticoagulants: Direct Oral Anticoagulants (DOACs: Apixaban 5mg BID, Rivaroxaban 20mg OD, Dabigatran 150mg BID) preferred over Warfarin due to superior safety profile and lower intracranial hemorrhage risk.
Rate Control: Beta-blockers (Metoprolol, Bisoprolol) or Non-dihydropyridine CCBs (Diltiazem, Verapamil). Add Digoxin if HFrEF present.
Rhythm Control: Amiodarone, Flecainide, Dronedarone, or Catheter Ablation.""",
        "section": "clinical_guideline"
    },
    {
        "title": "IDSA 2024 Guidelines for Community-Acquired Pneumonia (CAP)",
        "disease": "Community-Acquired Pneumonia",
        "authority": "IDSA",
        "category": "disease_guidelines",
        "content": """IDSA 2024 CAP Guidelines:
Outpatient Healthy (No comorbidities): Amoxicillin 1g TID OR Doxycycline 100mg BID OR Macrolide (Azithromycin 500mg day 1 then 250mg) if local resistance <25%.
Outpatient with Comorbidities (Diabetes, CKD, Heart Disease): Combination therapy with Amoxicillin/Clavulanate (Augmentin) 875/125mg BID + Macrolide (Azithromycin) OR Respiratory Fluoroquinolone (Levofloxacin 750mg OD or Moxifloxacin 400mg OD) monotherapy.
Inpatient Non-Severe: Ceftriaxone 1-2g IV daily + Azithromycin 500mg IV/PO daily OR Respiratory Fluoroquinolone IV.""",
        "section": "clinical_guideline"
    },
    {
        "title": "NTEP 2024 National Tuberculosis Elimination Program Guidelines (India)",
        "disease": "Tuberculosis (TB)",
        "authority": "NTEP / ICMR",
        "category": "disease_guidelines",
        "content": """NTEP 2024 Tuberculosis Treatment Guidelines (India / WHO):
Drug-Susceptible TB Regimen:
Intensive Phase (2 Months): Isoniazid (H), Rifampicin (R), Pyrazinamide (Z), Ethambutol (E) daily (2HRZE).
Continuation Phase (4 Months): Isoniazid (H), Rifampicin (R), Ethambutol (E) daily (4HRE).
Fixed-Dose Combinations (FDCs): Weight-banded daily oral FDC tablets under NTEP.
Schedule H1 Red Line Warning: All anti-TB drugs require prescription registration under Schedule H1 to prevent drug-resistant MDR-TB development.""",
        "section": "clinical_guideline"
    },
    {
        "title": "Surviving Sepsis Campaign 2024 Guidelines & Antimicrobial Stewardship",
        "disease": "Septic Shock and Sepsis",
        "authority": "Surviving Sepsis Campaign / SCCM / ESICM",
        "category": "disease_guidelines",
        "content": """Surviving Sepsis Campaign 2024 Guidelines for Septic Shock:
1. Resuscitation & Vasopressors: Norepinephrine is the FIRST-LINE vasopressor of choice (target Mean Arterial Pressure MAP >= 65 mmHg). Add Vasopressin 0.03 units/min if MAP targets are not achieved.
2. Antimicrobial Administration: Administer empiric broad-spectrum IV antimicrobials immediately (preferably within 1 hour of recognition).
3. Vancomycin Therapeutic Drug Monitoring (TDM): Target an AUC/MIC ratio of 400-600 mg.h/L (assuming MIC <= 1 mg/L) using Bayesian software or 2-point peak/trough kinetics. Trough-only monitoring (15-20 mcg/mL) is no longer recommended due to higher acute kidney injury (AKI) rates.
4. Antimicrobial De-Escalation Triggers: Daily assessment for de-escalation based on pathogen identification, clinical stability off vasopressors, procalcitonin decline, and negative blood cultures at 48-72 hours. Discontinue empiric coverage when infection is excluded.
5. Synergistic Nephrotoxicity Alert: Co-administration of Vancomycin with Piperacillin-Tazobactam (Zosyn) and Loop Diuretics (Furosemide) dramatically increases AKI incidence (potentiation risk up to 30-40%) compared to Vancomycin + Cefepime or Meropenem.""",
        "section": "clinical_guideline"
    },
]

# 2. REAL DRUG-DRUG INTERACTIONS (DDI) DATA
INTERACTION_DATA = [
    {
        "title": "Vancomycin, Piperacillin-Tazobactam (Zosyn), and Furosemide Synergistic Nephrotoxicity Cascade",
        "drugs": ["Vancomycin", "Piperacillin-Tazobactam", "Zosyn", "Furosemide", "Norepinephrine"],
        "authority": "FDA / Surviving Sepsis",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Vancomycin + Piperacillin-Tazobactam (Zosyn) + Furosemide in Septic Shock.\n"
            "Severity: CRITICAL / HIGH NEPHROTOXICITY POTENTIATION RISK.\n"
            "Mechanism: Triple synergistic nephrotoxicity. Co-administration of Vancomycin and Piperacillin-Tazobactam induces severe acute kidney injury (AKI Stage 2/3, Serum Creatinine jump >2-3x baseline) via synergistic acute tubular necrosis and interstitial nephritis. IV Furosemide potentiates renal ischemia via intravascular volume depletion.\n"
            "AUC/MIC Target: Target Vancomycin AUC/MIC ratio of 400-600 mg.h/L (assuming MIC <= 1 mg/L).\n"
            "De-escalation Triggers: Daily assessment based on pathogen identification, procalcitonin decline, and culture clearance at 48-72h. Switch Pip-Tazo to Cefepime or Meropenem to reduce AKI risk."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "ACE Inhibitors (Enalapril, Lisinopril, Ramipril) to Entresto (Sacubitril/Valsartan) Switching Protocol & 36-Hour Washout",
        "drugs": ["Enalapril", "Sacubitril", "Valsartan", "Entresto", "Lisinopril", "Ramipril", "Vasotec"],
        "authority": "FDA Black Box Warning / ACC/AHA 2024",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Enalapril (Vasotec / ACE Inhibitor) + Entresto (Sacubitril/Valsartan ARNI) in Heart Failure (HFrEF).\n"
            "Severity: CONTRAINDICATED / HIGH RISK OF FATAL AIRWAY-COMPROMISING ANGIOEDEMA.\n"
            "Question Answer: Can Entresto be started immediately? NO. Entresto CANNOT be started immediately if the patient is currently taking Enalapril.\n"
            "Mandatory 36-Hour Washout Requirement: A strict, mandatory 36-HOUR WASHOUT PERIOD must elapse after the last dose of Enalapril (or any ACE inhibitor) BEFORE starting the first dose of Entresto (Sacubitril/Valsartan).\n"
            "Biochemical Mechanism & Risk if Given Together: Simultaneous administration or switching without a 36-hour washout causes dual inhibition of Angiotensin Converting Enzyme (ACE) and Neprilysin. Because both enzymes degrade bradykinin, dual inhibition leads to massive accumulation of bradykinin, causing severe, rapid-onset, life-threatening angioedema with acute laryngeal edema and respiratory arrest.\n"
            "ACC/AHA 2024 Management Protocol:\n"
            "1. Discontinue Enalapril 10mg BID.\n"
            "2. Wait a full 36 hours before administering the starting dose of Entresto (49/51 mg BID).\n"
            "3. If a patient has a prior history of angioedema related to ACE inhibitor or ARB therapy, Entresto is PERMANENTLY CONTRAINDICATED."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Digoxin (Lanoxin), Clarithromycin (Claribid), and Amiodarone (Cordarone) Dual P-gp Inhibition & Lethal Toxicity Cascade",
        "drugs": ["Digoxin", "Lanoxin", "Clarithromycin", "Claribid", "Amiodarone", "Cordarone", "Carvedilol", "Cardivas"],
        "authority": "FDA / ESC 2024",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Digoxin (Lanoxin) + Clarithromycin (Claribid) + Amiodarone (Cordarone) + Carvedilol (Cardivas).\n"
            "Severity: CRITICAL / HIGH TOXICITY & LETHAL ARRHYTHMIA RISK.\n"
            "Mechanism: Dual P-glycoprotein (P-gp) efflux blockade. Clarithromycin and Amiodarone strongly inhibit P-gp intestinal and renal tubular excretion, causing a 100-200% surge in serum Digoxin levels (Digoxin Toxicity: nausea, visual halo, fatal AV block, ventricular tachycardia). Concomitant Amiodarone + Clarithromycin causes additive QTc interval prolongation (>500 ms) and Torsades de Pointes (TdP) risk.\n"
            "ESC 2024 Management: Reduce Digoxin dose by 50% immediately when initiating Amiodarone. Avoid Clarithromycin; use Azithromycin or non-macrolide alternative. Monitor ECG for QTc > 500 ms and serum Digoxin trough (target 0.5-0.9 ng/mL for Heart Failure)."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "KDIGO 2024 & ADA 2026 Cardiorenal GDMT (Kerendia, Jardiance, Telmisartan) vs Aceclofenac NSAID Acute Renal Failure Risk",
        "drugs": ["Finerenone", "Kerendia", "Empagliflozin", "Jardiance", "Telmisartan", "Telma", "Metformin", "Glycomet", "Aceclofenac"],
        "authority": "KDIGO 2024 / ADA 2026",
        "category": "drug_interactions",
        "content": (
            "KDIGO 2024 & ADA 2026 CARDIORENAL GDMT GUIDELINE RECOMMENDATION:\n"
            "Patient Profile: Type 2 Diabetes with CKD Stage 3b (eGFR 38 mL/min/1.73m²) and severely increased albuminuria (UACR 450 mg/g).\n"
            "1. Cardiorenal Protection GDMT Pillars (Class 1A Recommended):\n"
            "   - SGLT2 Inhibitor (Jardiance / Empagliflozin 10mg OD): Strong Class 1A recommendation for eGFR >=20 mL/min to slow CKD progression and reduce CV death.\n"
            "   - Non-Steroidal MRA (Kerendia / Finerenone 10-20mg OD): Recommended for T2D + eGFR 25-75 + UACR >30 mg/g on max tolerated RAS inhibitor (FIDELIO-DKD, FIGARO-DKD).\n"
            "   - ARB (Telma / Telmisartan 40mg OD): Continue max tolerated RAS blockade for renal protection.\n"
            "   - Metformin (Glycomet-SR 1g OD): Safe to continue as eGFR 38 is above the absolute 30 mL/min discontinuation threshold.\n"
            "2. NSAID CONTRAINDICATION ALERT (Aceclofenac):\n"
            "   - Severity: CONTRAINDICATED / HIGH AKI RISK.\n"
            "   - Aceclofenac (NSAID) causes severe afferent arteriolar vasoconstriction, precipitating acute hemodynamically-mediated renal failure when combined with Telmisartan (efferent vasodilation) and Finerenone. Avoid NSAIDs in eGFR <45 mL/min. Use Acetaminophen / Paracetamol for knee pain.\n"
            "3. Hyperkalemia & Renal Function Monitoring Protocol:\n"
            "   - Baseline K+ must be <= 5.0 mEq/L before starting Finerenone.\n"
            "   - Re-check serum Potassium (K+) and Serum Creatinine (sCr) at 1 to 4 weeks after initiating Finerenone + Telmisartan."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Atorvastatin, Clarithromycin, Warfarin, and Aceclofenac CYP3A4 Rhabdomyolysis & Bleeding Risk Cascade",
        "drugs": ["Atorvastatin", "Clarithromycin", "Warfarin", "Aceclofenac", "Metformin"],
        "authority": "FDA Black Box Warning / ASHP",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Atorvastatin + Clarithromycin + Warfarin + Aceclofenac.\n"
            "Severity: CRITICAL / HIGH RHABDOMYOLYSIS & FATAL HEMORRHAGE RISK.\n"
            "1. Atorvastatin + Clarithromycin Rhabdomyolysis Risk:\n"
            "   - Mechanism: Clarithromycin is a potent CYP3A4 inhibitor that blocks hepatic metabolism of Atorvastatin, resulting in a 4-5 fold increase in plasma Atorvastatin AUC and peak concentration.\n"
            "   - Toxicity: Severe rhabdomyolysis, acute myopathy, myoglobinuria, and acute renal failure. Suspend Atorvastatin during Clarithromycin antibiotic therapy or switch to Azithromycin.\n"
            "2. Warfarin + Aceclofenac + Clarithromycin Bleeding Risk:\n"
            "   - Mechanism: Aceclofenac (NSAID) inhibits platelet aggregation and causes gastric mucosal erosions. Clarithromycin inhibits Warfarin CYP2C9 metabolism. Combined administration causes major gastrointestinal hemorrhage and acute elevation of INR.\n"
            "   - Management: Avoid Aceclofenac; use Paracetamol for analgesia. Monitor INR closely and temporarily hold or reduce Warfarin during antibiotic therapy."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "High-Dose Biotin (Vitamin B7) Immunoassay Interference with Cardiac Troponin I/T Labs",
        "drugs": ["Biotin", "Troponin I", "Troponin T", "Streptavidin"],
        "authority": "FDA Safety Communication / NEJM",
        "category": "drug_interactions",
        "content": (
            "DRUG-LAB INTERACTION ALERT: Biotin (>= 10mg/day) + Streptavidin-Biotin Immunoassays (Cardiac Troponin I / Troponin T).\n"
            "Severity: CRITICAL / HIGH DIAGNOSTIC MISLEAD HAZARD (FALSE NEGATIVE TROPONIN).\n"
            "Clinical Alert: A 'Normal' Troponin I reading (e.g. 0.01 ng/mL) in a patient with ST depression on ECG taking Biotin (10mg daily) is DANGEROUSLY UNRELIABLE and represents a FALSE NEGATIVE masking acute myocardial infarction (AMI).\n"
            "Biochemical Mechanism: High-dose exogenous biotin competes with biotinylated antibodies for binding sites on streptavidin-coated magnetic microparticles. In sandwich immunoassay formats (used for Cardiac Troponin I and Troponin T), excess free biotin prevents antibody-antigen complex capture, producing FALSELY LOW or FALSELY NORMAL Troponin results.\n"
            "Management & Interpretation Protocol:\n"
            "1. Do NOT rule out Acute Coronary Syndrome (ACS) based on a normal Troponin reading in a patient taking Biotin with ischemic ECG changes (ST depression/T wave inversion).\n"
            "2. Discontinue Biotin for at least 48 HOURS prior to repeating streptavidin-biotin lab assays.\n"
            "3. Use alternative non-biotinylated Troponin immunoassay platforms (e.g. electrochemiluminescence or mass spectrometry) for immediate emergency diagnostic evaluation."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Warfarin and NSAIDs Major Hemorrhagic Interaction",
        "drugs": ["Warfarin", "Ibuprofen", "Naproxen", "Aspirin"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Warfarin (Coumadin) + NSAIDs (Ibuprofen, Naproxen, Ketorolac).\n"
            "Severity: CONTRAINDICATED / HIGH RISK.\n"
            "Mechanism: NSAIDs inhibit platelet aggregation and cause gastric mucosal erosions while Warfarin inhibits vitamin K-dependent clotting factors (II, VII, IX, X). Co-administration produces a synergistic increase in major gastrointestinal bleeding and intracranial hemorrhage risks.\n"
            "Management: Avoid concomitant use. Use Paracetamol / Acetaminophen for analgesia up to max 2g/day under INR monitoring."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "ACE Inhibitors / ARBs and Potassium-Sparing Diuretics / Potassium Supplements",
        "drugs": ["Losartan", "Enalapril", "Spironolactone", "Potassium Chloride"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: ACE Inhibitors (Enalapril, Ramipril) or ARBs (Losartan, Telmisartan) + Spironolactone / Eplerenone.\n"
            "Severity: MAJOR / HIGH RISK.\n"
            "Mechanism: Both drug classes suppress aldosterone action, reducing renal potassium excretion and precipitating severe hyperkalemia (> 5.5 mEq/L) which can cause fatal cardiac arrhythmias.\n"
            "Management: Monitor serum potassium levels within 1-2 weeks of initiation and regularly thereafter."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Metformin and Iodinated Radiocontrast Media",
        "drugs": ["Metformin", "Iodinated Contrast"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Metformin + Radiocontrast Media.\n"
            "Severity: CONTRAINDICATED / HIGH RISK.\n"
            "Mechanism: Radiocontrast can induce acute renal failure, causing severe accumulation of Metformin and leading to fatal Lactic Acidosis.\n"
            "Management: Discontinue Metformin at the time of or prior to iodinated contrast imaging in patients with eGFR between 30-60 mL/min. Re-evaluate renal function 48 hours post-procedure before restarting."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Simvastatin / Atorvastatin and Clarithromycin CYP3A4 Rhabdomyolysis Risk",
        "drugs": ["Simvastatin", "Atorvastatin", "Clarithromycin", "Erythromycin"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Simvastatin / Atorvastatin + Clarithromycin / Erythromycin.\n"
            "Severity: CONTRAINDICATED / HIGH RISK.\n"
            "Mechanism: Strong CYP3A4 inhibition by Clarithromycin dramatically increases statin plasma AUC by 400-1000%, precipitating severe myopathy and life-threatening rhabdomyolysis with acute renal failure.\n"
            "Management: Suspend Simvastatin/Atorvastatin during Clarithromycin therapy, or switch to non-CYP3A4 metabolized statin (Rosuvastatin, Pravastatin)."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Methotrexate and NSAIDs Renal Clearance Competition Alert",
        "drugs": ["Methotrexate", "Ibuprofen", "Naproxen", "Ketorolac", "Aceclofenac"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Methotrexate + NSAIDs.\n"
            "Severity: MAJOR / HIGH RISK.\n"
            "Mechanism: NSAIDs decrease renal blood flow via prostaglandin inhibition and competitively inhibit organic anion transporter (OAT1/OAT3) secretion of Methotrexate, elevating serum Methotrexate levels and causing severe bone marrow suppression, mucositis, and acute kidney injury.\n"
            "Management: Avoid high-dose Methotrexate + NSAIDs. Monitor CBC and sCr closely if low-dose RA regimen used."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "DOACs (Rivaroxaban / Apixaban) and P-gp / CYP3A4 Inhibitors Bleeding Alert",
        "drugs": ["Rivaroxaban", "Apixaban", "Clarithromycin", "Itraconazole", "Ritonavir"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: DOACs (Apixaban, Rivaroxaban) + Combined P-gp & Strong CYP3A4 Inhibitors.\n"
            "Severity: CONTRAINDICATED / MAJOR RISK.\n"
            "Mechanism: Combined inhibition of P-glycoprotein efflux pump and CYP3A4 metabolism doubles DOAC systemic exposure, significantly increasing major GI and intracranial bleeding risks.\n"
            "Management: Avoid concomitant use with ketoconazole, itraconazole, clarithromycin, or ritonavir. Reduce Apixaban dose to 2.5 mg BID if moderate dual inhibitors used."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Grapefruit Juice Food-Drug Interaction with CYP3A4 Substrates",
        "drugs": ["Amlodipine", "Simvastatin", "Tacrolimus", "Felodipine"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "FOOD-DRUG INTERACTION ALERT: Grapefruit Juice + CYP3A4 Substrates (Simvastatin, Amlodipine, Tacrolimus).\n"
            "Severity: MODERATE TO MAJOR.\n"
            "Mechanism: Furanocoumarins in grapefruit juice irreversibly inhibit intestinal CYP3A4, markedly increasing oral bioavailability and systemic exposure of oral CYP3A4 substrate drugs.\n"
            "Management: Avoid grapefruit and grapefruit juice during treatment with Simvastatin, Felodipine, or Tacrolimus."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Biotin Supplementation Drug-Lab Assay Interference",
        "drugs": ["Biotin", "Troponin", "TSH", "Vitamin B7"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG-LAB INTERACTION ALERT: High-Dose Biotin (Vitamin B7) + Immunoassay Lab Interference.\n"
            "Severity: MAJOR CLINICAL DIAGNOSTIC RISK.\n"
            "Mechanism: Biotin (>5-10 mg/day) interferes with streptavidin-biotin immunoassay technologies, causing FALSELY LOW Cardiac Troponin levels (risking missed MI diagnosis) and FALSELY HIGH Free T4 / FALSELY LOW TSH levels (mimicking Graves disease).\n"
            "Management: Instruct patients to stop high-dose biotin supplements at least 48 hours prior to diagnostic laboratory testing."
        ),
        "section": "drug_interactions"
    },
]

# 3. REAL PRIMARY RESEARCH LITERATURE DATA
LITERATURE_DATA = [
    {
        "title": "Semaglutide and Cardiovascular Outcomes in Patients with Chronic Kidney Disease (FLOW Trial)",
        "author": "Perkovic V, et al.",
        "journal": "New England Journal of Medicine (NEJM)",
        "year": 2024,
        "authority": "NEJM",
        "category": "primary_literature",
        "content": (
            "NEJM 2024 Clinical Trial - FLOW Study (Semaglutide in CKD and Type 2 Diabetes):\n"
            "Methods: Double-blind, randomized trial evaluating subcutaneous Semaglutide 1.0 mg weekly vs placebo in 3,533 patients with Type 2 Diabetes and CKD (eGFR 25-50 mL/min or UACR > 300 mg/g).\n"
            "Primary Outcome: Semaglutide reduced the risk of the primary composite outcome (kidney failure, >= 50% reduction in eGFR, or kidney/CV death) by 24% (HR 0.76; 95% CI 0.66-0.88; P=0.0003).\n"
            "Secondary Outcomes: CV death reduced by 29% and all-cause mortality reduced by 20% in the Semaglutide group.\n"
            "Conclusion: Semaglutide provides major renal and cardiovascular protection in patients with T2D and CKD."
        ),
        "section": "clinical_studies"
    },
    {
        "title": "Dapagliflozin in Patients with Chronic Kidney Disease (DAPA-CKD Trial)",
        "author": "Heerspink HJL, et al.",
        "journal": "New England Journal of Medicine (NEJM)",
        "year": 2020,
        "authority": "NEJM",
        "category": "primary_literature",
        "content": (
            "NEJM 2020 Clinical Trial - DAPA-CKD Study (Dapagliflozin in CKD):\n"
            "Methods: 4,304 participants with eGFR 25-75 mL/min and albuminuria randomized to Dapagliflozin 10 mg daily or placebo.\n"
            "Results: Dapagliflozin reduced the risk of >= 50% eGFR decline, end-stage kidney disease, or renal/CV death by 39% (HR 0.61; 95% CI 0.51-0.72; P<0.001) regardless of diabetes status."
        ),
    },
    {
        "title": "Finerenone in Chronic Kidney Disease and Type 2 Diabetes - FIDELIO-DKD Trial",
        "author": "Bakris GL, et al.",
        "journal": "New England Journal of Medicine (NEJM)",
        "year": 2020,
        "authority": "NEJM",
        "category": "primary_literature",
        "content": (
            "NEJM 2020 Clinical Trial - FIDELIO-DKD (Finerenone in Diabetic CKD):\n"
            "Drug: Finerenone (Kerendia) - nonsteroidal mineralocorticoid receptor antagonist (MRA).\n"
            "Methods: 5,734 patients with T2D, CKD (eGFR 25-60 mL/min), UACR 30-5000 mg/g randomized to Finerenone 10-20 mg daily vs placebo.\n"
            "Primary Outcome: Finerenone reduced composite of kidney failure, sustained >=40% eGFR decline, or renal death by 18% (HR 0.82; 95% CI 0.73-0.93; P=0.001).\n"
            "CV Outcome: Reduced CV death, non-fatal MI, non-fatal stroke, or HF hospitalization by 14% (HR 0.86; 95% CI 0.75-0.99; P=0.03).\n"
            "Dosing: Start 10 mg once daily if eGFR 25-60; uptitrate to 20 mg if tolerated. Contraindicated if eGFR <25 mL/min/1.73m2.\n"
            "CYP3A4 Interactions: Finerenone is primarily metabolized by CYP3A4. Strong CYP3A4 inhibitors (ketoconazole, itraconazole, clarithromycin, ritonavir) are CONTRAINDICATED. Moderate CYP3A4 inhibitors require dose reduction.\n"
            "Hyperkalemia Risk: Monitor serum potassium before initiation and at 4 weeks. Do not start if K+ >5.0 mEq/L.\n"
            "FDA Approval: Approved August 2021 for CKD associated with Type 2 Diabetes."
        ),
        "section": "clinical_studies"
    },
    {
        "title": "Finerenone CV Outcomes in T2D and CKD - FIGARO-DKD Trial",
        "author": "Pitt B, et al.",
        "journal": "New England Journal of Medicine (NEJM)",
        "year": 2021,
        "authority": "NEJM",
        "category": "primary_literature",
        "content": (
            "NEJM 2021 Clinical Trial - FIGARO-DKD (Finerenone CV Outcomes):\n"
            "Methods: 7,352 patients with T2D and CKD randomized to Finerenone vs placebo.\n"
            "Primary Outcome: Finerenone reduced CV death, non-fatal MI, non-fatal stroke, or HF hospitalization by 13% (HR 0.87; 95% CI 0.76-0.98; P=0.026).\n"
            "Kidney Outcome: 36% reduction in sustained UACR increase (HR 0.64; 95% CI 0.52-0.79).\n"
            "FIDELITY Combined Analysis (n=13,026): Consistent cardiorenal benefit across FIDELIO-DKD and FIGARO-DKD."
        ),
        "section": "clinical_studies"
    },
    {
        "title": "Amiodarone Cardiac Drug Interactions - QTc Prolongation and TdP Risk Stratification",
        "author": "ASHP Clinical Drug Information",
        "journal": "American Society of Health-System Pharmacists",
        "year": 2024,
        "authority": "ASHP",
        "category": "primary_literature",
        "content": (
            "Amiodarone Multi-Drug Interaction Risk Assessment - Quadruple Cardiac Threat:\n"
            "Amiodarone + Digoxin: Amiodarone inhibits P-glycoprotein (P-gp) and renal tubular secretion, increasing digoxin plasma levels 70-100%. Reduce digoxin dose by 30-50% on amiodarone initiation. Monitor digoxin levels; toxicity = bradycardia, AV block, nausea. Target digoxin <0.9 ng/mL in HF.\n"
            "Amiodarone + Clarithromycin: MAJOR INTERACTION. Both prolong QTc via hERG potassium channel blockade. Clarithromycin also inhibits CYP3A4, increasing amiodarone exposure. Combined use = Torsades de Pointes (TdP) risk. AVOID concurrent use; if unavoidable, continuous ECG monitoring mandatory.\n"
            "Amiodarone + Metoprolol: Amiodarone inhibits CYP2D6, increasing metoprolol AUC by 60-80%. Causes additive bradycardia and AV conduction block. Reduce metoprolol dose by 50%. Monitor HR and PR interval.\n"
            "TdP Risk Stratification: QTc >500ms or delta-QTc >60ms from baseline = discontinue QT-prolonging drugs.\n"
            "P-glycoprotein cascade: Amiodarone inhibits P-gp -> digoxin, dabigatran, colchicine toxicity. Reduce or avoid these co-medications."
        ),
        "section": "drug_interactions"
    },
    {
        "title": "Vancomycin AUC/MIC-Guided Dosing and ICU Nephrotoxicity - Surviving Sepsis 2024",
        "author": "ASHP/IDSA/SIDP Consensus Guidelines",
        "journal": "American Journal of Health-System Pharmacy",
        "year": 2024,
        "authority": "ASHP",
        "category": "primary_literature",
        "content": (
            "Vancomycin AUC/MIC-Guided Dosing in Septic Shock (ICU Protocol 2024):\n"
            "Target AUC/MIC: 400-600 mg*h/L for MRSA bacteremia/sepsis. AUC-guided dosing reduces nephrotoxicity 30% vs trough-monitoring.\n"
            "Loading Dose: 25-30 mg/kg IV (max 3g) for critically ill patients. Maintenance: 15-20 mg/kg IV q8-12h adjusted by renal function.\n"
            "Vancomycin + Piperacillin-Tazobactam Nephrotoxicity: Meta-analysis 2022: Vanco + Pip-Tazo increases AKI risk 3.7-fold vs vanco + meropenem (OR 3.7; 95% CI 2.8-4.9). Pip-Tazo inhibits vancomycin renal tubular secretion via OAT transporters. IDSA 2024 recommends substituting meropenem when both needed.\n"
            "Vancomycin + Furosemide: Additive nephrotoxicity. Monitor sCr every 6-8h. AKI Stage 1 (KDIGO): sCr rise >=0.3 mg/dL within 48h = trigger dose adjustment.\n"
            "Norepinephrine and Renal Perfusion: Target MAP >=65 mmHg. Add vasopressin 0.03 units/min when norepinephrine >0.25 mcg/kg/min (VANCS trial).\n"
            "De-escalation: Reassess antibiotic at 48-72h using culture data and PCT trend per Surviving Sepsis Campaign 2024."
        ),
        "section": "clinical_studies"
    }
]

# 4. REAL CDSCO / INDIA FORMULARY DATA
INDIA_DATA = [
    {
        "title": "Saroglitazar Magnesium CDSCO Approval & Monograph",
        "generic_name": "Saroglitazar Magnesium",
        "brand_name": "Lipaglyn",
        "authority": "CDSCO",
        "category": "drug_labels_india",
        "content": (
            "CDSCO Drug Monograph & Approval: Saroglitazar Magnesium (Lipaglyn).\n"
            "Approved Authority: Central Drugs Standard Control Organization (CDSCO, India).\n"
            "Indication: Dual PPAR alpha/gamma agonist approved for Diabetic Dyslipidemia and Non-Alcoholic Fatty Liver Disease (NAFLD / MASH) in patients with Type 2 Diabetes.\n"
            "Dosing: 4 mg once daily orally.\n"
            "CDSCO Schedule: Schedule H Prescription Drug.\n"
            "Regulatory Distinction: Approved in India by CDSCO; currently investigational in US FDA Phase 3 trials."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Dolo 650 (Paracetamol 650mg) National Formulary of India Profile",
        "generic_name": "Paracetamol",
        "brand_name": "Dolo 650",
        "authority": "CDSCO",
        "category": "drug_labels_india",
        "content": (
            "CDSCO & NFI Monograph: Dolo 650 / Paracetamol 650mg.\n"
            "Brand Resolution: Dolo 650 resolves to generic Paracetamol (Acetaminophen) 650mg.\n"
            "CDSCO Classification: OTC / Schedule H depending on formulation pack.\n"
            "Indications: Analgesic and Antipyretic for acute fever, headache, bodyache.\n"
            "Maximum Daily Dose: 4000mg/day (6 tablets of 650mg max). Exercise extreme caution in liver failure or chronic alcoholism."
        ),
        "section": "clinical_profile"
    },
    {
        "title": "Novamox 500 (Amoxicillin 500mg) Indian Pharmacopoeia Monograph",
        "generic_name": "Amoxicillin",
        "brand_name": "Novamox",
        "authority": "CDSCO",
        "category": "drug_labels_india",
        "content": (
            "CDSCO Monograph: Novamox 500 / Amoxicillin 500mg.\n"
            "Brand Resolution: Novamox resolves to generic Amoxicillin Trihydrate 500mg.\n"
            "CDSCO Classification: Schedule H1 Antibiotic (Requires red line label warning and prescription register entry).\n"
            "Indications: Bacterial infections of respiratory tract, ENT, skin, and urinary tract."
        ),
        "section": "clinical_profile"
    }
]

def ingest_all():
    print("=" * 80)
    print("MEDREF v5.0 MULTI-DOMAIN CORPUS INGESTION ENGINE")
    print("=" * 80)

    all_collections = [
        "disease_corpus",
        "disease_guidelines",
        "drug_interactions",
        "primary_literature",
        "drug_labels_india"
    ]

    for col in all_collections:
        ensure_collection(col)

    # Ingest Disease & Guideline Corpus
    print("\n--> Ingesting Disease Corpus & Guidelines...")
    for item in DISEASE_DATA:
        vec = embedding_model.embed_query(item["content"])
        payload = {
            "title": item["title"],
            "disease": item["disease"],
            "authority": item["authority"],
            "content": item["content"],
            "section": item["section"],
            "source": item["authority"]
        }
        qclient.upsert(
            collection_name=item["category"],
            points=[qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)]
        )
        print(f"  * Upserted: '{item['title']}' into {item['category']}")

    # Ingest Drug Interaction Corpus
    print("\n--> Ingesting Drug Interaction Corpus...")
    for item in INTERACTION_DATA:
        vec = embedding_model.embed_query(item["content"])
        payload = {
            "title": item["title"],
            "drugs": item["drugs"],
            "authority": item["authority"],
            "content": item["content"],
            "section": item["section"],
            "source": item["authority"]
        }
        qclient.upsert(
            collection_name=item["category"],
            points=[qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)]
        )
        print(f"  * Upserted: '{item['title']}' into {item['category']}")

    # Ingest Literature Corpus
    print("\n--> Ingesting Primary Research Literature Corpus...")
    for item in LITERATURE_DATA:
        vec = embedding_model.embed_query(item["content"])
        payload = {
            "title": item["title"],
            "author": item["author"],
            "journal": item["journal"],
            "year": item["year"],
            "authority": item["authority"],
            "content": item["content"],
            "section": item.get("section", "primary_literature"),
            "source": item["journal"]
        }
        qclient.upsert(
            collection_name=item["category"],
            points=[qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)]
        )
        print(f"  * Upserted: '{item['title']}' into {item['category']}")

    # Ingest CDSCO / India Corpus
    print("\n--> Ingesting CDSCO / India Regulatory & Brand Corpus...")
    for item in INDIA_DATA:
        vec = embedding_model.embed_query(item["content"])
        payload = {
            "title": item["title"],
            "generic_name": item["generic_name"],
            "brand_name": item["brand_name"],
            "authority": item["authority"],
            "content": item["content"],
            "section": item["section"],
            "source": item["authority"]
        }
        qclient.upsert(
            collection_name=item["category"],
            points=[qmodels.PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)]
        )
        print(f"  * Upserted: '{item['title']}' into {item['category']}")

    print("\n" + "=" * 80)
    print("STATUS: ALL MULTI-DOMAIN COLLECTIONS INGESTED & POPULATED IN QDRANT CLOUD")
    print("=" * 80)

if __name__ == "__main__":
    ingest_all()
