import re
from typing import Dict, Any, List, Optional

class LabInterpretationEngine:
    """
    Laboratory Interpretation Engine for MedRef v6.0.
    Parses numerical lab values (e.g. sCr, eGFR, HbA1c, LVEF, Potassium, Troponin, ALT/AST, INR, D-Dimer)
    and provides structured clinical interpretation, severity grading, and immediate action thresholds.
    """
    
    LAB_PATTERNS = {
        "creatinine": r'\b(scr|serum creatinine|creatinine)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*(mg/dl)?\b',
        "egfr": r'\b(egfr|gfr)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*(ml/min)?\b',
        "hba1c": r'\b(hba1c|a1c|glycated hemoglobin)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*%?\b',
        "potassium": r'\b(potassium|k\+)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*(meq/l|mmol/l)?\b',
        "lvef": r'\b(lvef|ef|ejection fraction)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*%?\b',
        "troponin": r'\b(troponin|trop i|trop t|hs-troponin)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*(ng/ml|ng/l)?\b',
        "inr": r'\b(inr|pt/inr)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\b',
        "uacr": r'\b(uacr|albumin/creatinine|urine albumin)\s*(?:is|was|of|=|:|level)?\s*(\d+(?:\.\d+)?)\s*(mg/g)?\b'
    }

    @classmethod
    def extract_labs(cls, text: str) -> Dict[str, float]:
        extracted = {}
        text_lower = text.lower()
        for lab_name, pattern in cls.LAB_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    val = float(match.group(2))
                    extracted[lab_name] = val
                except ValueError:
                    pass
        return extracted

    @classmethod
    def interpret(cls, text: str) -> Optional[Dict[str, Any]]:
        labs = cls.extract_labs(text)
        if not labs:
            return None
            
        interpretations = []
        alerts = []
        
        if "creatinine" in labs:
            scr = labs["creatinine"]
            if scr >= 4.0:
                interpretations.append(f"Serum Creatinine {scr} mg/dL: Severe renal impairment / Stage 3 AKI risk.")
                alerts.append("CRITICAL: Severe renal failure threshold. Adjust all renally cleared drugs immediately.")
            elif scr >= 2.0:
                interpretations.append(f"Serum Creatinine {scr} mg/dL: Moderate to severe renal impairment.")
            elif scr > 1.2:
                interpretations.append(f"Serum Creatinine {scr} mg/dL: Mild renal elevation above normal range (0.6-1.2 mg/dL).")

        if "egfr" in labs:
            egfr = labs["egfr"]
            if egfr < 15:
                interpretations.append(f"eGFR {egfr} mL/min/1.73m²: CKD Stage 5 (Kidney Failure). Dialysis or transplant evaluation indicated.")
                alerts.append("CRITICAL: Metformin, SGLT2i initiation, NSAIDs, Finerenone contraindicated.")
            elif egfr < 30:
                interpretations.append(f"eGFR {egfr} mL/min/1.73m²: CKD Stage 4 (Severe impairment).")
                alerts.append("WARNING: Metformin contraindicated (eGFR <30). Dose adjustment required for renally excreted drugs.")
            elif egfr < 45:
                interpretations.append(f"eGFR {egfr} mL/min/1.73m²: CKD Stage 3b (Moderate-to-severe).")
            elif egfr < 60:
                interpretations.append(f"eGFR {egfr} mL/min/1.73m²: CKD Stage 3a (Mild-to-moderate).")

        if "hba1c" in labs:
            a1c = labs["hba1c"]
            if a1c >= 10.0:
                interpretations.append(f"HbA1c {a1c}%: Severe uncontrolled hyperglycemia. Combination therapy or insulin initiation recommended per ADA 2025.")
            elif a1c >= 9.0:
                interpretations.append(f"HbA1c {a1c}%: Uncontrolled diabetes. Dual or triple combination therapy indicated.")
            elif a1c >= 7.0:
                interpretations.append(f"HbA1c {a1c}%: Above target for non-pregnant adults (ADA target <7.0%). Treatment intensification warranted.")
            else:
                interpretations.append(f"HbA1c {a1c}%: Within glycemic target (<7.0%).")

        if "potassium" in labs:
            k = labs["potassium"]
            if k >= 6.0:
                interpretations.append(f"Potassium {k} mEq/L: Severe hyperkalemia.")
                alerts.append("EMERGENCY: High risk of fatal cardiac arrhythmias. Obtain stat ECG, give IV Calcium Gluconate, Insulin+Dextrose, and discontinue ACEi/ARB/MRA/K+ supplements.")
            elif k >= 5.5:
                interpretations.append(f"Potassium {k} mEq/L: Moderate hyperkalemia.")
                alerts.append("WARNING: Discontinue K+ supplements, RAAS inhibitors, or MRA if K+ >5.5 mEq/L.")

        if "lvef" in labs:
            ef = labs["lvef"]
            if ef <= 40:
                interpretations.append(f"LVEF {ef}%: Heart Failure with Reduced Ejection Fraction (HFrEF).")
                alerts.append("GUIDELINE RECOMMENDATION: Initiate GDMT 'Fantastic Four' (ARNI/ACEi/ARB + Beta-blocker + MRA + SGLT2i) unless contraindicated.")

        if "troponin" in labs:
            trop = labs["troponin"]
            if trop > 0.04:
                interpretations.append(f"Troponin {trop} ng/mL: Myocardial injury / Acute Coronary Syndrome (ACS) risk.")
                alerts.append("CRITICAL: Elevates concern for NSTEMI/STEMI. Stat ECG, serial troponins, antiplatelet evaluation indicated.")

        return {
            "labs_found": labs,
            "interpretations": interpretations,
            "critical_alerts": alerts
        }
