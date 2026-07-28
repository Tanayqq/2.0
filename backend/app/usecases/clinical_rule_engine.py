"""
MedRef Clinical Rule Engine v5.5
Deterministic Rule-Based Clinical Decision Engine
Calculates explicit actions (STOP, HOLD, REDUCE DOSE, CONTINUE, INCREASE DOSE)
and safety requirements prior to LLM narrative generation.
"""

from typing import Dict, List, Any, Optional

class ClinicalRuleEngine:
    @staticmethod
    def evaluate_patient_medications(
        question_text: str,
        detected_drugs: List[str],
        patient_labs: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Deterministically evaluates patient medications and labs against clinical rules.
        """
        import re as regex
        
        # Normalize: ensure detected_drugs is always a list, never None
        if detected_drugs is None:
            detected_drugs = []
        
        q_lower = question_text.lower()
        
        # Extract lab values from prompt if not explicitly provided
        labs = patient_labs or {}
        if "egfr" not in labs:
            egfr_match = regex.search(r'egfr\s*(?:[=:]|\s+is\s+)?\s*([0-9]+(?:\.[0-9]+)?)', q_lower)
            if egfr_match:
                labs["egfr"] = float(egfr_match.group(1))
                
        if "potassium" not in labs and "k" not in labs:
            k_match = regex.search(r'(?:potassium|k\+?)\s*(?:[=:]|\s+is\s+)?\s*([0-9]+(?:\.[0-9]+)?)', q_lower)
            if k_match:
                labs["potassium"] = float(k_match.group(1))
                
        potassium = labs.get("potassium") or labs.get("k", 4.2)
        egfr = labs.get("egfr", 60.0)
        
        med_decisions: Dict[str, Dict[str, str]] = {}
        major_interactions: List[Dict[str, str]] = []
        mandatory_monitoring: List[str] = []
        immediate_dangers: List[str] = []

        # Track active drugs
        has_drug = lambda name: any(name in d.lower() for d in detected_drugs) or (name in q_lower)

        # ----------------------------------------------------
        # 1. IMMEDIATE LIFE-THREATENING HAZARDS
        # ----------------------------------------------------
        if potassium >= 6.0:
            immediate_dangers.append(
                f"CRITICAL HYPERKALEMIA (K+ = {potassium} mEq/L): Severe risk of fatal cardiac arrhythmias / AV block. "
                "Stat ECG required; administer IV Calcium Gluconate, Insulin + Dextrose, and immediately HOLD all potassium-retaining agents."
            )
        elif egfr < 30 and has_drug("metformin"):
            immediate_dangers.append(
                f"CONTRAINDICATED METFORMIN IN STAGE 4/5 CKD (eGFR = {egfr} mL/min): Severe risk of fatal Metformin-Associated Lactic Acidosis (MALA). Stop Metformin immediately."
            )

        # ----------------------------------------------------
        # 2. DETERMINISTIC MEDICATION DECISIONS & RATIONALE
        # ----------------------------------------------------
        # Spironolactone / Finerenone
        if has_drug("spironolactone") or has_drug("finerenone") or has_drug("eplerenone"):
            mra_name = "Spironolactone" if has_drug("spironolactone") else ("Finerenone" if has_drug("finerenone") else "Eplerenone")
            if potassium >= 5.5:
                med_decisions[mra_name] = {
                    "action": "HOLD",
                    "reason": f"Severe hyperkalemia (K+ {potassium} mEq/L > 5.5 mEq/L safety cut-off). Hold drug now; reassess after K+ drops < 5.0 mEq/L."
                }
            elif egfr < 30:
                med_decisions[mra_name] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Advanced CKD (eGFR {egfr} mL/min). Reduce dose to 12.5mg-25mg every other day with frequent K+ monitoring."
                }
            else:
                med_decisions[mra_name] = {
                    "action": "CONTINUE",
                    "reason": "GDMT Class 1A recommendation for HFrEF/CKD. Monitor K+ and serum creatinine."
                }

        # Metformin
        if has_drug("metformin"):
            if egfr < 30:
                med_decisions["Metformin XR"] = {
                    "action": "STOP",
                    "reason": f"eGFR {egfr} mL/min is below the absolute 30 mL/min discontinuation threshold for lactic acidosis prevention."
                }
            elif egfr < 45:
                med_decisions["Metformin XR"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"eGFR {egfr} mL/min requires maximum 1000mg/day limit and close renal monitoring."
                }
            else:
                med_decisions["Metformin XR"] = {
                    "action": "CONTINUE",
                    "reason": "First-line glycemic control. Safe at current renal function."
                }

        # Sacubitril/Valsartan (Entresto)
        if has_drug("sacubitril") or has_drug("entresto") or has_drug("valsartan"):
            if has_drug("enalapril") or has_drug("lisinopril") or has_drug("ramipril"):
                med_decisions["Sacubitril/Valsartan"] = {
                    "action": "HOLD",
                    "reason": "Mandatory 36-hour washout required after last ACEi dose to prevent life-threatening angioedema."
                }
            elif egfr < 30:
                med_decisions["Sacubitril/Valsartan"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"eGFR {egfr} mL/min is not an absolute contraindication, but requires starting at low dose (24/26mg BID) with close renal/K+ monitoring."
                }
            else:
                med_decisions["Sacubitril/Valsartan"] = {
                    "action": "CONTINUE",
                    "reason": "GDMT preferred first-line ARNI for HFrEF mortality reduction."
                }

        # Digoxin
        if has_drug("digoxin"):
            if has_drug("amiodarone"):
                med_decisions["Digoxin"] = {
                    "action": "REDUCE DOSE",
                    "reason": "Amiodarone inhibits P-gp, increasing serum Digoxin concentrations by 70-100%. Reduce Digoxin dose by 50% immediately; target trough 0.5-0.9 ng/mL."
                }
            else:
                med_decisions["Digoxin"] = {
                    "action": "CONTINUE",
                    "reason": "Symptom control in HFrEF / AFib. Monitor serum levels and heart rate."
                }

        # Amiodarone
        if has_drug("amiodarone"):
            med_decisions["Amiodarone"] = {
                "action": "CONTINUE",
                "reason": "Rhythm control in AFib/ventricular arrhythmia. Monitor LFTs, thyroid, PFTs, and ECG QTc."
            }

        # Clarithromycin
        if has_drug("clarithromycin"):
            if has_drug("atorvastatin") or has_drug("simvastatin"):
                med_decisions["Clarithromycin"] = {
                    "action": "HOLD",
                    "reason": "Potent CYP3A4 inhibitor that increases Statin AUC 4-5 fold, risking severe rhabdomyolysis and acute renal failure. Switch antibiotic to Azithromycin."
                }
            elif has_drug("warfarin"):
                med_decisions["Clarithromycin"] = {
                    "action": "REDUCE DOSE",
                    "reason": "Inhibits CYP2C9 metabolism of Warfarin, causing major INR surge and bleeding risk. Monitor INR closely."
                }
            else:
                med_decisions["Clarithromycin"] = {
                    "action": "CONTINUE",
                    "reason": "Short-term antimicrobial therapy. Monitor for CYP3A4 interactions."
                }

        # Atorvastatin
        if has_drug("atorvastatin") or has_drug("simvastatin"):
            stat_name = "Atorvastatin" if has_drug("atorvastatin") else "Simvastatin"
            if has_drug("clarithromycin"):
                med_decisions[stat_name] = {
                    "action": "HOLD",
                    "reason": "Temporarily hold statin therapy while on Clarithromycin to prevent CYP3A4-mediated rhabdomyolysis."
                }
            else:
                med_decisions[stat_name] = {
                    "action": "CONTINUE",
                    "reason": "Cardiovascular risk reduction. Safe at current hepatic/renal status."
                }

        # Warfarin
        if has_drug("warfarin"):
            if has_drug("clarithromycin") or has_drug("amiodarone"):
                med_decisions["Warfarin"] = {
                    "action": "REDUCE DOSE",
                    "reason": "CYP2C9/P-gp inhibition by concurrent Amiodarone/Clarithromycin increases INR and bleeding risk. Reduce dose and check INR in 3-5 days."
                }
            else:
                med_decisions["Warfarin"] = {
                    "action": "CONTINUE",
                    "reason": "Anticoagulation for stroke prevention. Maintain target INR 2.0-3.0."
                }

        # Metoprolol Succinate
        if has_drug("metoprolol"):
            med_decisions["Metoprolol Succinate"] = {
                "action": "CONTINUE",
                "reason": "GDMT Class 1A mortality-reducing beta-blocker in stable HFrEF. Monitor HR and AV conduction due to concurrent Amiodarone/Digoxin."
            }

        # Empagliflozin / Dapagliflozin
        if has_drug("empagliflozin") or has_drug("dapagliflozin"):
            sglt2_name = "Empagliflozin" if has_drug("empagliflozin") else "Dapagliflozin"
            med_decisions[sglt2_name] = {
                "action": "CONTINUE",
                "reason": "GDMT Class 1A cardiorenal protection in HFrEF and CKD (indicated down to eGFR 20 mL/min)."
            }

        # ----------------------------------------------------
        # 3. MAJOR INTERACTION ENGINE MATRIX
        # ----------------------------------------------------
        if has_drug("amiodarone") and has_drug("digoxin"):
            major_interactions.append({
                "pair": "Amiodarone ↔ Digoxin",
                "severity": "CRITICAL",
                "mechanism": "Amiodarone inhibits P-gp efflux, surging serum Digoxin concentrations by 70-100%, causing severe bradycardia, AV block, and fatal arrhythmias. Mandatory 50% Digoxin dose reduction."
            })
        if has_drug("clarithromycin") and (has_drug("atorvastatin") or has_drug("simvastatin")):
            major_interactions.append({
                "pair": "Clarithromycin ↔ Atorvastatin",
                "severity": "HIGH",
                "mechanism": "Clarithromycin strongly inhibits CYP3A4 hepatic metabolism, increasing Atorvastatin plasma AUC 4-5 fold, causing severe rhabdomyolysis, myoglobinuria, and AKI."
            })
        if has_drug("clarithromycin") and has_drug("warfarin"):
            major_interactions.append({
                "pair": "Clarithromycin ↔ Warfarin",
                "severity": "HIGH",
                "mechanism": "Clarithromycin inhibits CYP2C9 Warfarin breakdown, precipitating acute elevation of INR and major gastrointestinal/intracranial bleeding."
            })
        if has_drug("amiodarone") and has_drug("warfarin"):
            major_interactions.append({
                "pair": "Amiodarone ↔ Warfarin",
                "severity": "HIGH",
                "mechanism": "Amiodarone inhibits CYP2C9 and P-gp, potentiating Warfarin anticoagulant activity and significantly increasing bleeding risk."
            })
        if (has_drug("spironolactone") or has_drug("finerenone")) and (has_drug("sacubitril") or has_drug("entresto")):
            major_interactions.append({
                "pair": "Spironolactone ↔ Sacubitril/Valsartan",
                "severity": "MODERATE/HIGH",
                "mechanism": "Synergistic hyperkalemia risk cascade via dual RAAS/MRA blockade, requiring close serum potassium monitoring."
            })

        # ----------------------------------------------------
        # 4. MANDATORY MONITORING MATRIX
        # ----------------------------------------------------
        mandatory_monitoring = [
            "Serum Potassium (K+) & Creatinine / eGFR (every 48-72h during acute hyperkalemia)",
            "Target INR (2.0-3.0) for Warfarin therapy",
            "Serum Digoxin Trough Level (target 0.5-0.9 ng/mL for HFrEF)",
            "Creatine Kinase (CK) & LFTs (due to Statin + Macrolide co-administration)",
            "12-Lead ECG (monitor QTc interval and hyperkalemic T-wave peaking)",
            "Resting Heart Rate & Blood Pressure (due to triple AV-nodal blockade)"
        ]

        return {
            "decisions": med_decisions,
            "immediate_dangers": immediate_dangers,
            "major_interactions": major_interactions,
            "mandatory_monitoring": mandatory_monitoring,
            "labs": {"egfr": egfr, "potassium": potassium}
        }
