from typing import Dict, Any, List, Optional

class ADREngine:
    """
    Adverse Effect Engine (ADR Engine) for MedRef v6.0.
    Provides structured Adverse Drug Reaction data, Boxed Warnings,
    and toxicity management protocols.
    """

    ADR_DATABASE: Dict[str, Dict[str, Any]] = {
        "amiodarone": {
            "common_adrs": ["Photosensitivity", "Hypothyroidism", "Hyperthyroidism", "Nausea", "Microcorneal deposits"],
            "serious_adrs": ["Pulmonary fibrosis / pneumonitis", "Hepatotoxicity", "Severe bradycardia / AV block", "Optic neuropathy"],
            "boxed_warning": "FATAL PULMONARY TOXICITY, HEPATOTOXICITY, AND CARDIAC ARRHYTHMIA EXACERBATION. Initiate only in clinical setting with continuous ECG and cardiac resuscitation.",
            "monitoring_required": ["Baseline & 6-month Chest X-ray / PFTs", "Baseline & 6-month LFTs", "Baseline & 6-month TSH/T4", "Annual eye exam"],
            "management": "Discontinue immediately if pulmonary infiltrates, elevated liver transaminases (>3x ULN), or severe visual disturbances develop."
        },
        "methotrexate": {
            "common_adrs": ["Nausea", "Mucositis / Stomatitis", "Fatigue", "Alopecia", "Mild LFT elevation"],
            "serious_adrs": ["Bone marrow suppression / Pancytopenia", "Hepatotoxicity / Liver cirrhosis", "Pneumonitis", "Severe dermatologic reactions"],
            "boxed_warning": "SEVERE TOXICITY INCLUDING DEATH. Bone marrow suppression, hepatotoxicity, pulmonary toxicity, opportunist infections, and fetal death. Monitor CBC and LFTs closely.",
            "monitoring_required": ["Baseline CBC, LFTs, Serum Creatinine, Chest X-ray", "CBC & LFTs every 2-4 weeks during initiation, then every 8-12 weeks"],
            "management": "Co-administer Folic Acid 1mg daily. Hold dose if WBC <3,000/mm³, Platelets <100,000/mm³, or ALT/AST >3x ULN. Use Leucovorin rescue for overdose."
        },
        "vancomycin": {
            "common_adrs": ["Infusion reaction ('Red Man Syndrome')", "Nausea", "Phlebitis at injection site"],
            "serious_adrs": ["Acute Kidney Injury / Nephrotoxicity", "Ototoxicity (transient/permanent)", "TEN / SJS / DRESS", "Neutropenia"],
            "boxed_warning": "None (Black box warning absent, but high risk of nephrotoxicity with trough >20 mcg/mL or concomitant Pip-Tazo).",
            "monitoring_required": ["AUC/MIC targeting 400-600 mg·h/L", "Serum Creatinine & BUN every 24-48h in ICU", "Audiometry if prolonged use"],
            "management": "Infuse over at least 60 minutes to prevent histamine-mediated Red Man Syndrome. Switch to Meropenem from Pip-Tazo to reduce AKI risk."
        },
        "metformin": {
            "common_adrs": ["Diarrhea", "Nausea", "Abdominal discomfort", "Flatulence", "Metallic taste"],
            "serious_adrs": ["Lactic Acidosis (rare, high mortality)", "Vitamin B12 deficiency"],
            "boxed_warning": "METFORMIN-ASSOCIATED LACTIC ACIDOSIS. Risk increases with renal impairment, contrast dye, sepsis, hepatic failure, and excessive alcohol.",
            "monitoring_required": ["Baseline & annual eGFR", "Annual Vitamin B12 levels"],
            "management": "Discontinue if eGFR <30 mL/min/1.73m². Hold 48h prior to iodinated radiocontrast procedures in eGFR 30-60."
        },
        "finerenone": {
            "common_adrs": ["Hyperkalemia", "Hypotension", "Hyponatremia"],
            "serious_adrs": ["Severe hyperkalemia (K+ >6.0 mEq/L) leading to cardiac arrest"],
            "boxed_warning": "None, but contraindications exist for strong CYP3A4 inhibitors and K+ >5.0 mEq/L at baseline.",
            "monitoring_required": ["Serum potassium & eGFR prior to initiation, at 4 weeks, and periodically"],
            "management": "Do not initiate if K+ >5.0 mEq/L. Dose-reduce or hold if K+ rises >5.5 mEq/L. Restart when K+ <=5.0 mEq/L."
        }
    }

    @classmethod
    def get_adr_profile(cls, drug_name: str) -> Optional[Dict[str, Any]]:
        drug_key = drug_name.lower().strip()
        return cls.ADR_DATABASE.get(drug_key)
