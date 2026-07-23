import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger()

class ClinicalWorkflowEngine:
    """
    Executes clinical workflow pathways:
    Symptom -> Diagnostic Step -> Clinical Calculator -> Guideline Referral -> Treatment Strategy.
    """
    PATHWAYS = {
        "chest_pain": {
            "title": "Acute Chest Pain / Suspected ACS Pathway",
            "steps": [
                "1. Immediate 12-Lead ECG (Within 10 minutes of presentation)",
                "2. Serial High-Sensitivity Cardiac Troponin (0h and 1h/3h)",
                "3. Calculate HEART Score (History, ECG, Age, Risk Factors, Troponin)",
                "4. Apply ACC/AHA 2026 Chest Pain Guideline Pathway",
                "5. Low Risk (HEART 0-3): Outpatient stress testing / CCTA",
                "6. High Risk (HEART ≥4 or ST Elevation): Urgent Cardiology Consultation / Cath Lab Activation",
                "7. Initiate First-Line ACS Medical Therapy (Aspirin + P2Y12 Inhibitor + Anticoagulation)"
            ]
        },
        "shortness_of_breath": {
            "title": "Acute Dyspnea / Pulmonary Embolism & Heart Failure Pathway",
            "steps": [
                "1. Assess Vitals & Oxygen Saturation (Target SpO2 > 92%)",
                "2. Calculate Wells Score for PE & D-Dimer Test",
                "3. NT-proBNP / BNP Testing for Acute Heart Failure",
                "4. Bedside Ultrasound (POCUS) & Chest X-Ray",
                "5. Apply GINA / GOLD Guideline Escalation Strategy"
            ]
        }
    }

    @classmethod
    def execute_workflow(cls, symptom_or_condition: str) -> Optional[Dict[str, Any]]:
        cond_lower = symptom_or_condition.lower().replace(" ", "_")
        for key, pathway in cls.PATHWAYS.items():
            if key in cond_lower or cond_lower in key:
                logger.info("executing_clinical_workflow", pathway=key)
                return pathway
        return None
