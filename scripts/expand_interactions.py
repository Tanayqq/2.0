path = r'C:\Users\Tanay Kumar\Desktop\2.0\backend\ingestion\pipeline\ingest_multidomain_corpus.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_interactions = '''    {
        "title": "Simvastatin / Atorvastatin and Clarithromycin CYP3A4 Rhabdomyolysis Risk",
        "drugs": ["Simvastatin", "Atorvastatin", "Clarithromycin", "Erythromycin"],
        "authority": "FDA",
        "category": "drug_interactions",
        "content": (
            "DRUG INTERACTION ALERT: Simvastatin / Atorvastatin + Clarithromycin / Erythromycin.\\n"
            "Severity: CONTRAINDICATED / HIGH RISK.\\n"
            "Mechanism: Strong CYP3A4 inhibition by Clarithromycin dramatically increases statin plasma AUC by 400-1000%, precipitating severe myopathy and life-threatening rhabdomyolysis with acute renal failure.\\n"
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
            "DRUG INTERACTION ALERT: Methotrexate + NSAIDs.\\n"
            "Severity: MAJOR / HIGH RISK.\\n"
            "Mechanism: NSAIDs decrease renal blood flow via prostaglandin inhibition and competitively inhibit organic anion transporter (OAT1/OAT3) secretion of Methotrexate, elevating serum Methotrexate levels and causing severe bone marrow suppression, mucositis, and acute kidney injury.\\n"
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
            "DRUG INTERACTION ALERT: DOACs (Apixaban, Rivaroxaban) + Combined P-gp & Strong CYP3A4 Inhibitors.\\n"
            "Severity: CONTRAINDICATED / MAJOR RISK.\\n"
            "Mechanism: Combined inhibition of P-glycoprotein efflux pump and CYP3A4 metabolism doubles DOAC systemic exposure, significantly increasing major GI and intracranial bleeding risks.\\n"
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
            "FOOD-DRUG INTERACTION ALERT: Grapefruit Juice + CYP3A4 Substrates (Simvastatin, Amlodipine, Tacrolimus).\\n"
            "Severity: MODERATE TO MAJOR.\\n"
            "Mechanism: Furanocoumarins in grapefruit juice irreversibly inhibit intestinal CYP3A4, markedly increasing oral bioavailability and systemic exposure of oral CYP3A4 substrate drugs.\\n"
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
            "DRUG-LAB INTERACTION ALERT: High-Dose Biotin (Vitamin B7) + Immunoassay Lab Interference.\\n"
            "Severity: MAJOR CLINICAL DIAGNOSTIC RISK.\\n"
            "Mechanism: Biotin (>5-10 mg/day) interferes with streptavidin-biotin immunoassay technologies, causing FALSELY LOW Cardiac Troponin levels (risking missed MI diagnosis) and FALSELY HIGH Free T4 / FALSELY LOW TSH levels (mimicking Graves disease).\\n"
            "Management: Instruct patients to stop high-dose biotin supplements at least 48 hours prior to diagnostic laboratory testing."
        ),
        "section": "drug_interactions"
    },'''

marker = '"section": "drug_interactions"\n    }\n]'
if marker in content:
    content = content.replace(marker, '"section": "drug_interactions"\n    },\n' + new_interactions + '\n]', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Expanded INTERACTION_DATA in ingest_multidomain_corpus.py")
else:
    print("ERROR: marker not found")
