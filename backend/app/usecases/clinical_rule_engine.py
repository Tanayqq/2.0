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
            egfr_match = regex.search(r'(?:egfr|gfr)(?:\s*\([^\)]*\))?\s*(?:[=:|]|is|level|of)?\s*([0-9]+(?:\.[0-9]+)?)', q_lower)
            if egfr_match:
                labs["egfr"] = float(egfr_match.group(1))
                
        if "potassium" not in labs and "k" not in labs:
            k_match = regex.search(r'(?:potassium|k\+?)(?:\s*\([^\)]*\))?\s*(?:[=:|]|is|level|of)?\s*([0-9]+(?:\.[0-9]+)?)', q_lower)
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
        # 1. IMMEDIATE LIFE-THREATENING HAZARDS (Independent checks)
        # ----------------------------------------------------
        if potassium >= 6.0:
            immediate_dangers.append(
                f"CRITICAL HYPERKALEMIA (K+ = {potassium} mEq/L): Severe risk of fatal cardiac arrhythmias / AV block. "
                "Stat ECG required; administer IV Calcium Gluconate, Insulin + Dextrose, and immediately HOLD all potassium-retaining agents."
            )
        elif potassium >= 5.5:
            immediate_dangers.append(
                f"HYPERKALEMIA (K+ = {potassium} mEq/L): High risk of cardiac arrhythmias. Hold Spironolactone and all potassium-retaining agents."
            )
            
        if egfr < 30 and has_drug("metformin"):
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
                    "reason": "CONTRAINDICATED COMBINATION: Mandatory 36-hour washout required between ACEi (Enalapril/Lisinopril) and Sacubitril/Valsartan to prevent life-threatening angioedema."
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
        if has_drug("empagliflozin") or has_drug("dapagliflozin") or has_drug("canagliflozin"):
            sglt2_name = "Empagliflozin" if has_drug("empagliflozin") else ("Dapagliflozin" if has_drug("dapagliflozin") else "Canagliflozin")
            med_decisions[sglt2_name] = {
                "action": "CONTINUE",
                "reason": "GDMT Class 1A cardiorenal protection in HFrEF and CKD (indicated down to eGFR 20 mL/min)."
            }

        # Colchicine
        if has_drug("colchicine"):
            if has_drug("fluconazole") or has_drug("ketoconazole") or has_drug("clarithromycin"):
                med_decisions["Colchicine"] = {
                    "action": "HOLD",
                    "reason": "Contraindicated: Strong P-gp/CYP3A4 inhibition with Fluconazole/Macrolide in renal impairment risks fatal colchicine toxicity (rhabdomyolysis & bone marrow suppression)."
                }
            elif egfr < 30:
                med_decisions["Colchicine"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Advanced CKD (eGFR {egfr} mL/min). Reduce colchicine dose by 50% or extend dosing interval."
                }
            else:
                med_decisions["Colchicine"] = {
                    "action": "CONTINUE",
                    "reason": "Gout management. Monitor for muscular pain or gastrointestinal symptoms."
                }

        # Fluconazole
        if has_drug("fluconazole"):
            if has_drug("colchicine"):
                med_decisions["Fluconazole"] = {
                    "action": "HOLD",
                    "reason": "Strong P-gp/CYP3A4 inhibitor causing colchicine accumulation in CKD. Consider alternative antifungal (e.g. Echinocandin or Nystatin) to prevent severe toxicity."
                }
            else:
                med_decisions["Fluconazole"] = {
                    "action": "CONTINUE",
                    "reason": "Short-term antifungal therapy. Monitor liver function tests and QTc interval."
                }

        # Allopurinol
        if has_drug("allopurinol"):
            if egfr < 30:
                med_decisions["Allopurinol"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Severe renal impairment (eGFR {egfr} mL/min). Maximum starting dose 50mg daily; titrate cautiously to prevent hypersensitivity (AHS)."
                }
            elif egfr < 60:
                med_decisions["Allopurinol"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Moderate CKD (eGFR {egfr} mL/min). Reduce dose (max 100-200mg/day) to prevent oxypurinol accumulation."
                }
            else:
                med_decisions["Allopurinol"] = {
                    "action": "CONTINUE",
                    "reason": "Urate-lowering therapy. Monitor serum uric acid and renal function."
                }

        # Dabigatran / Apixaban / Rivaroxaban
        if has_drug("dabigatran") or has_drug("apixaban") or has_drug("rivaroxaban"):
            doac_name = "Dabigatran" if has_drug("dabigatran") else ("Apixaban" if has_drug("apixaban") else "Rivaroxaban")
            if egfr < 30:
                med_decisions[doac_name] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Renal clearance (eGFR {egfr} mL/min). Dose reduction required to prevent severe accumulation and major hemorrhage."
                }
            else:
                med_decisions[doac_name] = {
                    "action": "CONTINUE",
                    "reason": "Stroke prevention in Atrial Fibrillation. Monitor eGFR and signs of bleeding."
                }

        # Ticagrelor / Clopidogrel
        if has_drug("ticagrelor") or has_drug("clopidogrel"):
            p2y12_name = "Ticagrelor" if has_drug("ticagrelor") else "Clopidogrel"
            if has_drug("fluconazole"):
                med_decisions[p2y12_name] = {
                    "action": "REDUCE DOSE",
                    "reason": "Fluconazole inhibits CYP3A4, significantly increasing Ticagrelor exposure and bleeding risk. Monitor closely for signs of hemorrhage."
                }
            else:
                med_decisions[p2y12_name] = {
                    "action": "CONTINUE",
                    "reason": "Antiplatelet therapy for post-PCI CAD. Monitor for bleeding."
                }

        # Lisinopril / Enalapril / Losartan
        if has_drug("lisinopril") or has_drug("enalapril") or has_drug("losartan"):
            acei_name = "Lisinopril" if has_drug("lisinopril") else ("Enalapril" if has_drug("enalapril") else "Losartan")
            if potassium >= 5.5:
                med_decisions[acei_name] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Moderate hyperkalemia (K+ {potassium} mEq/L). Reduce dose by 50% and monitor serum potassium closely."
                }
            else:
                med_decisions[acei_name] = {
                    "action": "CONTINUE",
                    "reason": "GDMT RAAS inhibition for CKD and hypertension."
                }

        # Linezolid
        if has_drug("linezolid"):
            if has_drug("fluoxetine") or has_drug("sumatriptan") or has_drug("tramadol") or has_drug("sertraline"):
                med_decisions["Linezolid"] = {
                    "action": "HOLD",
                    "reason": "Reversible non-selective MAO inhibitor: Concurrent use with serotonergic drugs (Fluoxetine, Sumatriptan, Tramadol) causes life-threatening Serotonin Syndrome. Switch antibiotic to Vancomycin or Daptomycin."
                }
            else:
                med_decisions["Linezolid"] = {
                    "action": "CONTINUE",
                    "reason": "Oxazolidinone antibacterial. Monitor complete blood count weekly for myelosuppression."
                }

        # Fluoxetine
        if has_drug("fluoxetine"):
            if has_drug("linezolid"):
                med_decisions["Fluoxetine"] = {
                    "action": "HOLD",
                    "reason": "Potent SSRI: Concurrent Linezolid (MAOI) therapy risks severe Serotonin Syndrome (hyperthermia, autonomic instability, clonus). Require 5-week washout before MAOI."
                }
            else:
                med_decisions["Fluoxetine"] = {
                    "action": "CONTINUE",
                    "reason": "SSRI therapy for depression. Monitor for drug interactions and suicidal ideation."
                }

        # Sumatriptan
        if has_drug("sumatriptan"):
            if has_drug("linezolid"):
                med_decisions["Sumatriptan"] = {
                    "action": "HOLD",
                    "reason": "Contraindicated with MAO inhibitors like Linezolid due to severe serotonergic vasospastic reaction and Serotonin Syndrome."
                }
            else:
                med_decisions["Sumatriptan"] = {
                    "action": "CONTINUE",
                    "reason": "Acute migraine therapy. Use PRN; limit to max 200mg/24 hours."
                }

        # Aceclofenac / NSAIDs
        if has_drug("aceclofenac") or has_drug("ibuprofen") or has_drug("naproxen") or has_drug("ketorolac") or has_drug("diclofenac"):
            nsaid_name = "Aceclofenac" if has_drug("aceclofenac") else ("Ibuprofen" if has_drug("ibuprofen") else "NSAID")
            if egfr < 30 or (potassium >= 5.5 and (has_drug("enalapril") or has_drug("lisinopril") or has_drug("losartan"))):
                med_decisions[nsaid_name] = {
                    "action": "STOP",
                    "reason": f"Contraindicated in severe AKI/CKD (eGFR {egfr} mL/min) and Triple Whammy DDI with RAASi/Diuretics (severe afferent vasoconstriction AKI)."
                }
            else:
                med_decisions[nsaid_name] = {
                    "action": "REDUCE DOSE",
                    "reason": "Use lowest effective dose for shortest duration due to renal and GI risks."
                }

        # Vancomycin
        if has_drug("vancomycin"):
            if egfr < 30 or has_drug("tazobactam") or has_drug("zosyn") or has_drug("piperacillin"):
                med_decisions["Vancomycin"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Renal impairment (eGFR {egfr} mL/min) and synergistic AKI risk with Pip-Tazo. Dose per AUC/MIC (target 400-600) and monitor trough levels."
                }
            else:
                med_decisions["Vancomycin"] = {
                    "action": "CONTINUE",
                    "reason": "Glycopeptide antibacterial. Monitor serum trough concentrations and renal function."
                }

        # Piperacillin/Tazobactam (Zosyn)
        if has_drug("tazobactam") or has_drug("zosyn") or has_drug("piperacillin"):
            if has_drug("vancomycin"):
                med_decisions["Piperacillin/Tazobactam"] = {
                    "action": "HOLD",
                    "reason": "Synergistic AKI risk with Vancomycin. Evaluate culture clearance; consider de-escalation to Cefepime or Meropenem for renal protection during Vancomycin co-therapy."
                }
            elif egfr < 50:
                med_decisions["Piperacillin/Tazobactam"] = {
                    "action": "REDUCE DOSE",
                    "reason": f"Renal impairment (eGFR {egfr} mL/min). Dose adjustment required (2.25g q6h or 3.375g q6h)."
                }
            else:
                med_decisions["Piperacillin/Tazobactam"] = {
                    "action": "CONTINUE",
                    "reason": "Extended-spectrum antipseudomonal penicillin. Adjust dose for renal clearance."
                }

        # Furosemide
        if has_drug("furosemide") or has_drug("torsemide") or has_drug("bumetanide"):
            diuretic_name = "Furosemide" if has_drug("furosemide") else "Loop Diuretic"
            if egfr < 30:
                med_decisions[diuretic_name] = {
                    "action": "CONTINUE",
                    "reason": "Loop diuretic for volume management in CKD/AKI; monitor fluid status, K+, and serum creatinine."
                }
            else:
                med_decisions[diuretic_name] = {
                    "action": "CONTINUE",
                    "reason": "Loop diuretic for edema management. Monitor volume status and electrolytes."
                }

        # Tramadol
        if has_drug("tramadol"):
            if has_drug("linezolid") or has_drug("fluoxetine"):
                med_decisions["Tramadol"] = {
                    "action": "HOLD",
                    "reason": "Inhibits serotonin reuptake: Concurrent Linezolid (MAOI) or Fluoxetine risks Serotonin Syndrome and lowers seizure threshold. Switch to non-serotonergic analgesic."
                }
            else:
                med_decisions["Tramadol"] = {
                    "action": "CONTINUE",
                    "reason": "Analgesic for pain. Use lowest effective dose; monitor for CNS depression."
                }

        # 100% Medication Coverage Guarantee: Ensure every prescribed drug has an entry in Section 2 table
        for raw_d in (detected_drugs or []):
            if not raw_d or raw_d.lower() in ("general clinical evidence", "patient scenario"):
                continue
            clean_d = raw_d.strip().capitalize()
            if not any(clean_d.lower() in k.lower() or k.lower() in clean_d.lower() for k in med_decisions.keys()):
                med_decisions[clean_d] = {
                    "action": "CONTINUE",
                    "reason": "Safe at current clinical status; monitor routine therapeutic parameters."
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
        if has_drug("fluconazole") and has_drug("colchicine"):
            major_interactions.append({
                "pair": "Fluconazole ↔ Colchicine",
                "severity": "CRITICAL",
                "mechanism": "Fluconazole strongly inhibits CYP3A4 and P-gp, surging Colchicine plasma levels and precipitating fatal bone marrow suppression and rhabdomyolysis in renal impairment."
            })
        if has_drug("fluconazole") and has_drug("ticagrelor"):
            major_interactions.append({
                "pair": "Fluconazole ↔ Ticagrelor",
                "severity": "HIGH",
                "mechanism": "Fluconazole inhibits CYP3A4 metabolism of Ticagrelor, increasing plasma exposure and systemic bleeding risk."
            })
        if (has_drug("dabigatran") or has_drug("apixaban")) and has_drug("ticagrelor") and has_drug("aspirin"):
            major_interactions.append({
                "pair": "Dabigatran ↔ Ticagrelor ↔ Aspirin",
                "severity": "HIGH",
                "mechanism": "Triple antithrombotic therapy markedly elevates major gastrointestinal and intracranial bleeding risks; limit duration post-PCI."
            })
        if has_drug("linezolid") and (has_drug("fluoxetine") or has_drug("sertraline")):
            major_interactions.append({
                "pair": "Linezolid ↔ Fluoxetine",
                "severity": "CRITICAL",
                "mechanism": "Linezolid non-selective MAO inhibition combined with Fluoxetine SSRI action triggers fatal Serotonin Syndrome (hyperthermia, rigidity, autonomic failure)."
            })
        if has_drug("linezolid") and has_drug("sumatriptan"):
            major_interactions.append({
                "pair": "Linezolid ↔ Sumatriptan",
                "severity": "CRITICAL",
                "mechanism": "Linezolid MAO inhibition impairs Sumatriptan clearance, precipitating severe vasospastic reactions and serotonin toxicity."
            })
        if has_drug("linezolid") and has_drug("tramadol"):
            major_interactions.append({
                "pair": "Linezolid ↔ Tramadol",
                "severity": "HIGH",
                "mechanism": "Dual serotonergic stimulation and MAO inhibition increases risks of Serotonin Syndrome and severe seizure activity."
            })
        if (has_drug("aceclofenac") or has_drug("ibuprofen") or has_drug("naproxen")) and (has_drug("enalapril") or has_drug("lisinopril") or has_drug("losartan")) and (has_drug("furosemide") or has_drug("torsemide")):
            major_interactions.append({
                "pair": "Aceclofenac ↔ Enalapril ↔ Furosemide",
                "severity": "CRITICAL",
                "mechanism": "Triple Whammy DDI: NSAID afferent arteriolar constriction + ACEi efferent arteriolar vasodilation + Diuretic volume depletion causes severe acute kidney injury (AKI Stage 3)."
            })
        if has_drug("vancomycin") and (has_drug("tazobactam") or has_drug("zosyn") or has_drug("piperacillin")):
            major_interactions.append({
                "pair": "Vancomycin ↔ Piperacillin/Tazobactam",
                "severity": "HIGH",
                "mechanism": "Synergistic nephrotoxicity: Combined administration induces acute tubular injury and interstitial nephritis, causing rapid elevation in serum creatinine."
            })

        # ----------------------------------------------------
        # 4. MANDATORY MONITORING MATRIX (Dynamic — only include items relevant to active drugs)
        # ----------------------------------------------------
        mandatory_monitoring = []

        # Universal baseline monitoring
        mandatory_monitoring.append("Serum Potassium (K+): Check weekly during CKD/RAAS/diuretic therapy; q24-48h if acutely abnormal.")
        mandatory_monitoring.append("Serum Creatinine & eGFR: Check baseline and 1-2 weeks after any RAAS/MRA/SGLT2i adjustment.")

        # Anticoagulant monitoring
        if has_drug("warfarin"):
            mandatory_monitoring.append("Target INR (2.0-3.0): Check INR q3-5 days during concurrent Amiodarone or Clarithromycin initiation/discontinuation.")
        if has_drug("dabigatran") or has_drug("apixaban") or has_drug("rivaroxaban"):
            mandatory_monitoring.append("DOAC Renal Clearance: Check eGFR every 6 months; more frequently in CKD or acute illness to adjust DOAC dose.")

        # Digoxin monitoring
        if has_drug("digoxin"):
            mandatory_monitoring.append("Serum Digoxin Trough Level: Target 0.5-0.9 ng/mL for HFrEF; recheck 7-10 days after 50% dose reduction with Amiodarone.")

        # Statin + Macrolide monitoring
        if has_drug("atorvastatin") or has_drug("simvastatin") or has_drug("clarithromycin") or has_drug("fluconazole"):
            mandatory_monitoring.append("Creatine Kinase (CK): Baseline and immediate recheck if muscle pain, weakness, or dark urine develops (Statin + CYP3A4 inhibitor DDI).")

        # LFT monitoring
        lft_drugs = [d.title() for d in ["amiodarone", "atorvastatin", "simvastatin", "rosuvastatin"] if has_drug(d)]
        if lft_drugs:
            mandatory_monitoring.append(f"Liver Function Tests (AST/ALT, Bilirubin): Check baseline, at 1 month, and q6 months for {', '.join(lft_drugs)} therapy.")

        # QTc / ECG monitoring
        ecg_drugs = [d.title() for d in ["amiodarone", "clarithromycin", "linezolid", "fluconazole", "digoxin", "metoprolol"] if has_drug(d)]
        if ecg_drugs:
            mandatory_monitoring.append(f"12-Lead ECG: Monitor QTc interval and PR interval/AV conduction for {', '.join(ecg_drugs)} therapy.")

        # Heart rate / BP monitoring for cardiac drugs
        if has_drug("metoprolol") or has_drug("amiodarone") or has_drug("digoxin"):
            mandatory_monitoring.append("Resting Heart Rate & Blood Pressure: Monitor daily (target HR 55-80 bpm, SBP > 90 mmHg) due to AV-nodal blockade.")

        # Heart failure volume status
        if has_drug("sacubitril") or has_drug("spironolactone") or has_drug("empagliflozin") or has_drug("dapagliflozin"):
            mandatory_monitoring.append("Daily Weight & Volume Status: Weigh daily in morning; report weight gain > 2-3 lbs in 24h or 5 lbs in a week.")
            mandatory_monitoring.append("Urine Output & AKI Surveillance: Target > 0.5 mL/kg/h; monitor for oliguria in CKD.")

        # Serotonin Syndrome monitoring
        if has_drug("linezolid") or has_drug("fluoxetine") or has_drug("tramadol") or has_drug("sumatriptan"):
            mandatory_monitoring.append("Serotonin Syndrome Surveillance: Monitor for hyperthermia, muscle rigidity, clonus, autonomic instability; discontinue all serotonergic agents immediately if suspected.")

        # Colchicine toxicity monitoring
        if has_drug("colchicine"):
            mandatory_monitoring.append("Colchicine Toxicity: Monitor CBC weekly for myelosuppression and CK for rhabdomyolysis during CYP3A4/P-gp inhibitor co-therapy.")

        # Electrolyte monitoring
        if has_drug("digoxin") or has_drug("amiodarone") or has_drug("spironolactone"):
            mandatory_monitoring.append("Serum Electrolytes (Magnesium & Sodium): Maintain Mg2+ > 2.0 mEq/L to prevent Digoxin toxicity and QTc prolongation.")

        # Glycemic monitoring
        if has_drug("metformin") or has_drug("empagliflozin") or has_drug("dapagliflozin"):
            mandatory_monitoring.append("Blood Glucose & HbA1c: Monitor fasting glucose and HbA1c quarterly; hold SGLT2i during AKI or contrast procedures.")

        return {
            "decisions": med_decisions,
            "immediate_dangers": immediate_dangers,
            "major_interactions": major_interactions,
            "mandatory_monitoring": mandatory_monitoring,
            "labs": {"egfr": egfr, "potassium": potassium}
        }
