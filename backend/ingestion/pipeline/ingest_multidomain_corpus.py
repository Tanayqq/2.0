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
qclient = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
VECTOR_SIZE = 384

def ensure_collection(collection_name: str):
    try:
        qclient.get_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' exists.")
    except Exception:
        print(f"Creating collection '{collection_name}'...")
        qclient.create_collection(
            collection_name=collection_name,
            vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE)
        )

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
    }
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
