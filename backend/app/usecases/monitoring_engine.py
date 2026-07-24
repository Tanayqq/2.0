from typing import Dict, Any, List, Optional

class ClinicalMonitoringEngine:
    """
    Clinical Monitoring Engine for MedRef v6.0.
    Provides baseline lab protocols, ongoing monitoring intervals,
    and explicit stop/discontinuation triggers.
    """

    MONITORING_RULES: Dict[str, Dict[str, Any]] = {
        "methotrexate": {
            "baseline": ["CBC with differential", "LFTs (ALT, AST, Bilirubin)", "Serum Creatinine & eGFR", "Chest X-ray", "Hepatitis B & C screening"],
            "routine_interval": "Every 2 to 4 weeks for first 3 months; every 8 to 12 weeks thereafter.",
            "stop_triggers": [
                "ALT / AST > 3x Upper Limit of Normal (ULN)",
                "WBC < 3,000 / mm³ or Absolute Neutrophil Count (ANC) < 1,500 / mm³",
                "Platelets < 100,000 / mm³",
                "Unexplained dry cough, fever, or dyspnea (Pneumonitis risk)",
                "Pregnancy (Absolute stop trigger)"
            ]
        },
        "amiodarone": {
            "baseline": ["Chest X-ray & Pulmonary Function Tests (DLCO)", "Liver Function Tests (ALT, AST, Alk Phos)", "Thyroid Function Tests (TSH, Free T4)", "ECG (QTc interval)", "Eye exam"],
            "routine_interval": "LFTs & TSH every 6 months; Chest X-ray annually; ECG every 3 to 6 months.",
            "stop_triggers": [
                "Pulmonary symptoms or new infiltrates on Chest X-ray",
                "ALT / AST > 3x baseline or ULN",
                "QTc > 500 ms or delta-QTc > 60 ms from baseline",
                "Optic neuritis / visual field defect"
            ]
        },
        "clozapine": {
            "baseline": ["Absolute Neutrophil Count (ANC) via REMS program", "Fasting Blood Glucose / HbA1c", "Lipid Panel", "ECG", "Troponin"],
            "routine_interval": "ANC weekly for months 1-6; biweekly for months 6-12; monthly thereafter.",
            "stop_triggers": [
                "ANC < 1,000 / mm³ (Severe Neutropenia / Agranulocytosis)",
                "Myocarditis symptoms (chest pain, tachycardia, elevated Troponin)"
            ]
        },
        "valproic_acid": {
            "baseline": ["CBC with platelets", "LFTs", "Pregnancy test (teratogenic)"],
            "routine_interval": "Trough serum valproate level (target 50-100 mcg/mL), LFTs & CBC every 3-6 months.",
            "stop_triggers": [
                "ALT / AST > 3x ULN or jaundice (Fatal Hepatotoxicity risk in <2yo)",
                "Ammonia elevation with encephalopathy",
                "Pancreatitis (severe abdominal pain, lipase elevation)"
            ]
        },
        "statins": {
            "baseline": ["Fasting Lipid Panel", "ALT / AST", "CK (Creatine Kinase) if muscle symptoms history"],
            "routine_interval": "Lipid panel at 4-12 weeks post-initiation, then annually. Routine LFT monitoring not required unless symptomatic.",
            "stop_triggers": [
                "Unexplained severe muscle pain with CK > 10x ULN (Rhabdomyolysis)",
                "ALT / AST > 3x ULN persistent"
            ]
        }
    }

    @classmethod
    def get_monitoring_protocol(cls, drug_name: str) -> Optional[Dict[str, Any]]:
        drug_key = drug_name.lower().strip()
        return cls.MONITORING_RULES.get(drug_key)
