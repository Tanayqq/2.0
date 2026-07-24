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
        "title": "ICMR Guidelines for Management of Acute Fever and Tropical Fevers",
        "disease": "Fever / Dengue / Typhoid / Influenza",
        "authority": "ICMR",
        "category": "disease_corpus",
        "content": (
            "Clinical Protocol for Acute Undifferentiated Fever (ICMR / MoHFW):\n"
            "Evaluation Protocol:\n"
            "1. History Taking: Record exact fever duration (days), temperature pattern, patient age, pregnancy status, active medications, cough, rash, and travel history.\n"
            "2. Diagnostic Considerations:\n"
            "   - Viral Fever / Influenza: Sudden onset fever, myalgia, sore throat, cough. Symptomatic management with Paracetamol 500mg-650mg QDS.\n"
            "   - Dengue Fever: High fever, retro-orbital pain, severe arthralgia ('breakbone fever'), thrombocytopenia. AVOID NSAIDs (Ibuprofen, Aspirin) due to severe hemorrhage risk. Maintain oral hydration.\n"
            "   - Typhoid Fever (Enteric Fever): Step-ladder fever pattern, abdominal pain, bradycardia (Faget's sign). Blood culture & Widal test. Empiric therapy: Azithromycin or Ceftriaxone.\n"
            "Red Flag Symptoms: Persistent vomiting, petechial rash, bleeding gums, altered sensorium, breathlessness require urgent emergency hospitalization."
        ),
        "section": "clinical_guideline"
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
    }
]

# 2. REAL DRUG-DRUG INTERACTIONS (DDI) DATA
INTERACTION_DATA = [
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
            "section": item["section"],
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
