from typing import Dict, Any, List, Optional

class LabKnowledgeDomain:
    """
    Lab Knowledge Domain Engine for MedRef v6.0.
    Provides reference ranges, elevation/depression causes, drug effects,
    associated diseases, and clinical management for 12 core lab tests.
    """

    LAB_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
        "creatinine": {
            "name": "Serum Creatinine (sCr)",
            "reference_range": "Adult Male: 0.7 - 1.3 mg/dL | Adult Female: 0.6 - 1.1 mg/dL",
            "causes_of_elevation": ["Acute Kidney Injury (AKI)", "Chronic Kidney Disease (CKD)", "Dehydration / Prerenal Azotemia", "Urinary tract obstruction", "Rhabdomyolysis"],
            "causes_of_depression": ["Decreased muscle mass / Amputation", "Severe malnutrition / Muscle wasting", "Pregnancy (hyperfiltration)"],
            "drug_effects_increase": ["NSAIDs (Ibuprofen, Naproxen)", "ACEi / ARBs (transient <30% rise expected)", "Vancomycin", "Aminoglycosides", "Radiocontrast", "Trimethoprim (pseudo-elevation via OCT2 competition)"],
            "drug_effects_decrease": ["None clinically significant"],
            "associated_diseases": ["Diabetic Kidney Disease", "Hypertensive Nephrosclerosis", "Glomerulonephritis", "Septic Shock AKI"],
            "monitoring_recommendations": "Assess eGFR using CKD-EPI 2021 formula. Discontinue metformin if eGFR <30 mL/min/1.73m²."
        },
        "hba1c": {
            "name": "Glycated Hemoglobin (HbA1c)",
            "reference_range": "Normal: <5.7% | Prediabetes: 5.7 - 6.4% | Diabetes: >=6.5%",
            "causes_of_elevation": ["Uncontrolled Diabetes Mellitus", "Iron deficiency anemia (falsely high)", "Chronic renal failure", "Severe hypertriglyceridemia"],
            "causes_of_depression": ["Hemolytic anemia (falsely low)", "Acute blood loss", "Recent blood transfusion", "Erythropoietin therapy", "Pregnancy"],
            "drug_effects_increase": ["Systemic corticosteroids (Prednisone, Dexamethasone)", "Atypical antipsychotics (Olanzapine, Clozapine)", "Thiazide diuretics", "Protease inhibitors"],
            "drug_effects_decrease": ["Insulin", "SGLT2 inhibitors", "GLP-1 receptor agonists", "Metformin", "Sulfonylureas"],
            "associated_diseases": ["Type 1 & Type 2 Diabetes Mellitus", "Metabolic Syndrome", "Cushing's Syndrome"],
            "monitoring_recommendations": "Measure every 3 months in uncontrolled patients; every 6 months in stable patients achieving target (<7.0%)."
        },
        "potassium": {
            "name": "Serum Potassium (K+)",
            "reference_range": "3.5 - 5.0 mEq/L (mmol/L)",
            "causes_of_elevation": ["Renal failure / Anuria", "Addison's disease (adrenal insufficiency)", "Cellular lysis (tumor lysis, rhabdomyolysis)", "Metabolic acidosis"],
            "causes_of_depression": ["GI loss (vomiting, severe diarrhea)", "Renal potassium wasting", "Refeeding syndrome", "Hyperaldosteronism"],
            "drug_effects_increase": ["ACEi (Enalapril, Lisinopril)", "ARBs (Losartan, Valsartan)", "MRAs (Spironolactone, Finerenone, Eplerenone)", "Trimethoprim", "NSAIDs", "Heparin"],
            "drug_effects_decrease": ["Loop diuretics (Furosemide, Torsemide)", "Thiazides (HCTZ, Chlorthalidone)", "Insulin", "Beta-2 agonists (Albuterol)", "Corticosteroids"],
            "associated_diseases": ["CKD / AKI", "Diabetic Ketoacidosis", "Heart Failure"],
            "monitoring_recommendations": "Stat ECG if K+ >6.0 or <2.8. Hyperkalemia K+ >5.5 requires holding RAAS inhibitors/MRAs."
        },
        "troponin": {
            "name": "High-Sensitivity Cardiac Troponin I / T",
            "reference_range": "hs-cTnI: <14 ng/L (0.014 ng/mL) | Standard cTnI: <0.04 ng/mL",
            "causes_of_elevation": ["Acute Myocardial Infarction (STEMI / NSTEMI)", "Myocarditis / Pericarditis", "Pulmonary Embolism", "Takotsubo Cardiomyopathy", "Severe Sepsis", "CKD Stage 4-5 (baseline elevation)"],
            "causes_of_depression": ["None"],
            "drug_effects_increase": ["Chemotherapy cardiotoxicity (Doxorubicin, Trastuzumab)", "Sympathomimetics (Cocaine, Amphetamines)"],
            "drug_effects_decrease": ["Biotin supplementation (can cause FALSELY LOW results on biotinylated immunoassays)"],
            "associated_diseases": ["Acute Coronary Syndrome (ACS)", "Heart Failure exacerbation", "Myocardial injury"],
            "monitoring_recommendations": "Serial troponin at 0h, 1h/2h, or 3h. Evaluate using HEART / TIMI score."
        }
    }

    @classmethod
    def get_lab_info(cls, lab_name: str) -> Optional[Dict[str, Any]]:
        lab_key = lab_name.lower().strip()
        return cls.LAB_KNOWLEDGE.get(lab_key)
