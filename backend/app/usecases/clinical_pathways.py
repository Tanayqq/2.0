from typing import Dict, Any, List, Optional

class ClinicalPathwaysEngine:
    """
    Clinical Pathways Engine for MedRef v6.0.
    Executes interactive, step-by-step clinical decision flows:
    - Chest Pain ACS Pathway
    - Septic Shock ICU Pathway
    - AKI Evaluation Pathway
    - DKA Management Pathway
    """

    PATHWAYS: Dict[str, Dict[str, Any]] = {
        "chest_pain": {
            "title": "Acute Chest Pain / Suspected ACS Clinical Decision Pathway (ACC/AHA 2024)",
            "steps": [
                "1. Immediate Assessment: Vital signs, O2 saturation, 12-lead ECG within 10 minutes.",
                "2. ECG Interpretation: STEMI (ST elevation) -> Immediate Reperfusion / Primary PCI within 90 mins.",
                "3. Non-ST Elevation / Normal ECG: Draw High-Sensitivity Cardiac Troponin (hs-cTn) at 0h and 1h/2h.",
                "4. Risk Stratification: Calculate HEART Score (History, ECG, Age, Risk Factors, Troponin).",
                "5. Decision: HEART Score 0-3 (Low Risk) -> Discharge with outpatient stress test. HEART Score >=4 (Moderate/High Risk) -> Admit for serial troponins & Invasive Angiography."
            ],
            "first_line_therapy": "Aspirin 325mg chewable + P2Y12 inhibitor (Ticagrelor 180mg or Prasugrel 60mg) + Anticoagulation (Heparin / Enoxaparin) + Nitroglycerin SL for pain."
        },
        "sepsis": {
            "title": "Septic Shock Hour-1 Bundle & Resuscitation Protocol (Surviving Sepsis 2024)",
            "steps": [
                "1. Measure Serum Lactate immediately; re-measure if initial lactate > 2.0 mmol/L.",
                "2. Obtain Blood Cultures prior to initiating antimicrobial therapy (2 sets).",
                "3. Administer Broad-Spectrum Antibiotics (e.g. Vancomycin + Cefepime / Meropenem) within 1 hour.",
                "4. Rapid Fluid Resuscitation: 30 mL/kg IV crystalloid (Balanced Crystalloid: Lactated Ringer's preferred over Normal Saline) for hypotension or lactate >= 4.0 mmol/L.",
                "5. Vasopressors: Initiate Norepinephrine as first-line vasopressor to maintain Target MAP >= 65 mmHg.",
                "6. Refractory Shock: Add Vasopressin 0.03 units/min if Norepinephrine > 0.25 mcg/kg/min."
            ],
            "monitoring_triggers": "Reassess MAP, urine output (>0.5 mL/kg/h), and lactate clearance every 1-2 hours."
        },
        "aki": {
            "title": "Acute Kidney Injury (AKI) KDIGO Staging & Management Pathway",
            "steps": [
                "1. Confirm AKI Staging: Stage 1 (sCr 1.5-1.9x baseline or rise >=0.3 mg/dL); Stage 2 (sCr 2.0-2.9x); Stage 3 (sCr >=3.0x or sCr >=4.0 mg/dL or initiation of RRT).",
                "2. Etiology Differentiation: Prerenal (FeNa <1%, BUN/Cr >20:1) vs Intrinsic ATN (FeNa >2%, muddy brown casts) vs Postrenal (Bladder scan / Ultrasound).",
                "3. Nephrotoxic Drug Audit: Immediately HOLD NSAIDs, ACEi/ARBs, Aminoglycosides, Amphotericin B.",
                "4. Dosing Adjustment: Adjust Vancomycin (AUC/MIC 400-600), Pip-Tazo, Fluconazole, DOACs based on estimated GFR.",
                "5. Urgent RRT Indications (AEIOU): Acidosis (pH <7.1), Electrolytes (K+ >6.5), Ingestion (toxic alcohols), Overload (refractory pulmonary edema), Uremia (pericarditis, encephalopathy)."
            ]
        }
    }

    @classmethod
    def get_pathway(cls, query: str) -> Optional[Dict[str, Any]]:
        q_lower = query.lower()
        if any(w in q_lower for w in ["chest pain", "acs", "stemi", "nstemi"]):
            return cls.PATHWAYS.get("chest_pain")
        if any(w in q_lower for w in ["septic", "sepsis", "septic shock"]):
            return cls.PATHWAYS.get("sepsis")
        if any(w in q_lower for w in ["aki", "acute kidney injury", "renal failure"]):
            return cls.PATHWAYS.get("aki")
        return None
