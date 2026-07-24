import math
from typing import Dict, Any, Optional

class ClinicalCalculatorEngine:
    """
    Clinical Calculator Engine for MedRef v6.0.
    Executes medical scoring algorithms:
    - CKD-EPI 2021 eGFR
    - CURB-65 Pneumonia Severity Score
    - CHA₂DS₂-VASc Atrial Fibrillation Stroke Risk
    - Wells Criteria for DVT / PE
    """

    @classmethod
    def calculate_ckd_epi_2021(cls, scr: float, age: float, is_female: bool) -> Dict[str, Any]:
        """CKD-EPI 2021 Race-Free eGFR equation"""
        kappa = 0.7 if is_female else 0.9
        alpha = -0.241 if is_female else -0.302
        min_scr = min(scr / kappa, 1.0)
        max_scr = max(scr / kappa, 1.0)
        gender_mult = 1.012 if is_female else 1.0
        
        egfr = 142 * (min_scr ** alpha) * (max_scr ** -1.200) * (0.9938 ** age) * gender_mult
        egfr_val = round(egfr, 1)
        
        stage = "G1 (Normal)" if egfr_val >= 90 else (
            "G2 (Mildly decreased)" if egfr_val >= 60 else (
                "G3a (Mild-to-moderate)" if egfr_val >= 45 else (
                    "G3b (Moderate-to-severe)" if egfr_val >= 30 else (
                        "G4 (Severely decreased)" if egfr_val >= 15 else "G5 (Kidney Failure)"
                    )
                )
            )
        )
        return {
            "calculator": "CKD-EPI 2021 eGFR",
            "score": egfr_val,
            "unit": "mL/min/1.73m²",
            "interpretation": f"eGFR = {egfr_val} mL/min/1.73m² ({stage})."
        }

    @classmethod
    def calculate_curb65(cls, confusion: bool, bun_gt_19: bool, rr_gte_30: bool, bp_low: bool, age_gte_65: bool) -> Dict[str, Any]:
        """CURB-65 Pneumonia Severity Score"""
        score = sum([confusion, bun_gt_19, rr_gte_30, bp_low, age_gte_65])
        if score <= 1:
            risk = "Low mortality (0.6-1.5%). Outpatient treatment suitable."
        elif score == 2:
            risk = "Moderate mortality (5.2%). Consider short inpatient stay or close outpatient monitoring."
        else:
            risk = "High mortality (10-30%). Hospital admission required; consider ICU if score >= 4."
            
        return {
            "calculator": "CURB-65 Pneumonia Severity",
            "score": score,
            "interpretation": risk
        }

    @classmethod
    def calculate_cha2ds2_vasc(
        cls, age: float, is_female: bool, chf: bool, htn: bool, stroke_tia: bool,
        vasc_disease: bool, diabetes: bool
    ) -> Dict[str, Any]:
        """CHA₂DS₂-VASc Score for Atrial Fibrillation Stroke Risk"""
        score = 0
        if chf: score += 1
        if htn: score += 1
        if age >= 75: score += 2
        elif age >= 65: score += 1
        if diabetes: score += 1
        if stroke_tia: score += 2
        if vasc_disease: score += 1
        if is_female: score += 1
        
        annual_risk = [0, 1.3, 2.2, 3.2, 4.0, 6.7, 9.8, 9.6, 12.5, 15.2][min(score, 9)]
        
        recommendation = "No anticoagulation recommended." if (score == 0 if not is_female else score <= 1) else (
            "Oral anticoagulation (DOAC) should be considered." if (score == 1 if not is_female else score == 2) else
            "Oral anticoagulation (DOAC: Apixaban, Rivaroxaban, Dabigatran) RECOMMENDED."
        )
        
        return {
            "calculator": "CHA₂DS₂-VASc Score",
            "score": score,
            "annual_stroke_risk": f"{annual_risk}% per year",
            "recommendation": recommendation
        }
