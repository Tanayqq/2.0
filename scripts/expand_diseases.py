path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\ingestion\pipeline\ingest_multidomain_corpus.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_diseases = '''    {
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
    },'''

# Also re-apply interactions expansion cleanly
interactions_code = '''    {
        "title": "Simvastatin / Atorvastatin and Clarithromycin CYP3A4 Rhabdomyolysis Risk",
        "drugs": ["Simvastatin", "Atorvastatin", "Clarithromycin", "Erythromycin"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": """DRUG INTERACTION ALERT: Simvastatin / Atorvastatin + Clarithromycin / Erythromycin.
Severity: CONTRAINDICATED / HIGH RISK.
Mechanism: Strong CYP3A4 inhibition by Clarithromycin dramatically increases statin plasma AUC by 400-1000%, precipitating severe myopathy and life-threatening rhabdomyolysis with acute renal failure.
Management: Suspend Simvastatin/Atorvastatin during Clarithromycin therapy, or switch to non-CYP3A4 metabolized statin (Rosuvastatin, Pravastatin).""",
        "section": "drug_interactions"
    },
    {
        "title": "Methotrexate and NSAIDs Renal Clearance Competition Alert",
        "drugs": ["Methotrexate", "Ibuprofen", "Naproxen", "Ketorolac", "Aceclofenac"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": """DRUG INTERACTION ALERT: Methotrexate + NSAIDs.
Severity: MAJOR / HIGH RISK.
Mechanism: NSAIDs decrease renal blood flow via prostaglandin inhibition and competitively inhibit organic anion transporter (OAT1/OAT3) secretion of Methotrexate, elevating serum Methotrexate levels and causing severe bone marrow suppression, mucositis, and acute kidney injury.
Management: Avoid high-dose Methotrexate + NSAIDs. Monitor CBC and sCr closely if low-dose RA regimen used.""",
        "section": "drug_interactions"
    },
    {
        "title": "DOACs (Rivaroxaban / Apixaban) and P-gp / CYP3A4 Inhibitors Bleeding Alert",
        "drugs": ["Rivaroxaban", "Apixaban", "Clarithromycin", "Itraconazole", "Ritonavir"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": """DRUG INTERACTION ALERT: DOACs (Apixaban, Rivaroxaban) + Combined P-gp & Strong CYP3A4 Inhibitors.
Severity: CONTRAINDICATED / MAJOR RISK.
Mechanism: Combined inhibition of P-glycoprotein efflux pump and CYP3A4 metabolism doubles DOAC systemic exposure, significantly increasing major GI and intracranial bleeding risks.
Management: Avoid concomitant use with ketoconazole, itraconazole, clarithromycin, or ritonavir. Reduce Apixaban dose to 2.5 mg BID if moderate dual inhibitors used.""",
        "section": "drug_interactions"
    },
    {
        "title": "Grapefruit Juice Food-Drug Interaction with CYP3A4 Substrates",
        "drugs": ["Amlodipine", "Simvastatin", "Tacrolimus", "Felodipine"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": """FOOD-DRUG INTERACTION ALERT: Grapefruit Juice + CYP3A4 Substrates (Simvastatin, Amlodipine, Tacrolimus).
Severity: MODERATE TO MAJOR.
Mechanism: Furanocoumarins in grapefruit juice irreversibly inhibit intestinal CYP3A4, markedly increasing oral bioavailability and systemic exposure of oral CYP3A4 substrate drugs.
Management: Avoid grapefruit and grapefruit juice during treatment with Simvastatin, Felodipine, or Tacrolimus.""",
        "section": "drug_interactions"
    },
    {
        "title": "Biotin Supplementation Drug-Lab Assay Interference",
        "drugs": ["Biotin", "Troponin", "TSH", "Vitamin B7"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": """DRUG-LAB INTERACTION ALERT: High-Dose Biotin (Vitamin B7) + Immunoassay Lab Interference.
Severity: MAJOR CLINICAL DIAGNOSTIC RISK.
Mechanism: Biotin (>5-10 mg/day) interferes with streptavidin-biotin immunoassay technologies, causing FALSELY LOW Cardiac Troponin levels (risking missed MI diagnosis) and FALSELY HIGH Free T4 / FALSELY LOW TSH levels (mimicking Graves disease).
Management: Instruct patients to stop high-dose biotin supplements at least 48 hours prior to diagnostic laboratory testing.""",
        "section": "drug_interactions"
    },'''

marker_dis = '"section": "clinical_guideline"\n    }\n]'
marker_int = '"section": "drug_interactions"\n    }\n]'

if marker_dis in content:
    content = content.replace(marker_dis, '"section": "clinical_guideline"\n    },\n' + new_diseases + '\n]', 1)

if marker_int in content:
    content = content.replace(marker_int, '"section": "drug_interactions"\n    },\n' + interactions_code + '\n]', 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Clean patch applied with triple quotes")
