import structlog
from typing import Dict, Any, List, Optional
from app.domain.models import PatientProfile

logger = structlog.get_logger()

class RecommendationModule:
    @staticmethod
    def recommend_therapy(disease_or_symptom: str, patient_profile: Optional[PatientProfile] = None) -> Dict[str, Any]:
        """
        Deterministic, evidence-grounded recommendation module.
        Pipeline selects therapy options based on guidelines and contraindications, NOT the LLM.
        """
        logger.info("executing_recommendation_module", target=disease_or_symptom)
        
        target_lower = disease_or_symptom.lower()
        recommendations = {
            "first_line_drugs": [],
            "second_line_drugs": [],
            "contraindicated_drugs": [],
            "recommended_labs": [],
            "monitoring_plan": [],
            "referral_recommendation": None,
            "patient_education": []
        }

        # Deterministic Clinical Rule Matrix
        if "chest pain" in target_lower or "acs" in target_lower:
            recommendations["first_line_drugs"] = ["Aspirin (162-325 mg chewed)", "Nitroglycerin (Sublingual)"]
            recommendations["second_line_drugs"] = ["Clopidogrel", "Ticagrelor", "Heparin"]
            recommendations["recommended_labs"] = ["12-Lead ECG (within 10 mins)", "Cardiac Troponin I/T", "CBC", "BMP"]
            recommendations["referral_recommendation"] = "IMMEDIATE EMERGENCY CARDIOLOGY REFERRAL / CATH LAB ACTIVATION."
            recommendations["patient_education"].append("Chew uncoated aspirin immediately unless allergic. Do not drive yourself to the emergency department.")

        elif "asthma" in target_lower:
            recommendations["first_line_drugs"] = ["Low-dose ICS-Formoterol (As-needed for MART)"]
            recommendations["second_line_drugs"] = ["Medium-dose ICS + LABA", "LTRA (Montelukast)"]
            recommendations["recommended_labs"] = ["Spirometry (FEV1/FVC)", "Peak Expiratory Flow (PEF)"]
            recommendations["monitoring_plan"].append("Assess PEF twice daily during exacerbations. Review inhaler technique at every visit.")

        elif "diabetes" in target_lower or "t2d" in target_lower:
            recommendations["first_line_drugs"] = ["Metformin", "SGLT2 Inhibitors (Empagliflozin / Dapagliflozin)", "GLP-1 RA (Semaglutide)"]
            recommendations["recommended_labs"] = ["HbA1c (Every 3 months)", "eGFR & Urine Albumin-to-Creatinine Ratio (UACR)", "Lipid Panel"]
            recommendations["monitoring_plan"].append("Target HbA1c < 7.0% for most non-pregnant adults.")

        # Patient Context Safety Adjustments
        if patient_profile:
            if patient_profile.eGFR and patient_profile.eGFR < 30:
                recommendations["contraindicated_drugs"].append("High-dose Metformin (Contraindicated when eGFR < 30 mL/min)")
                recommendations["contraindicated_drugs"].append("NSAIDs (High risk of acute renal failure)")
            if patient_profile.pregnancy:
                recommendations["contraindicated_drugs"].append("ACE Inhibitors / ARBs / Entresto (Boxed Warning: Fetal Toxicity)")

        return recommendations
