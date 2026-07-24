from typing import Dict, Any, List, Optional

class DrugClassEngine:
    """
    Pharmacological Drug Class Knowledge Engine for MedRef v6.0.
    Indexes drug classes, mechanisms, member drugs, shared warnings, and comparative hierarchy.
    """

    DRUG_CLASSES: Dict[str, Dict[str, Any]] = {
        "sglt2_inhibitors": {
            "class_name": "SGLT2 Inhibitors (Sodium-Glucose Cotransporter-2 Inhibitors)",
            "mechanism": "Inhibits SGLT2 in proximal renal tubules, reducing glucose reabsorption and inducing glucosuria, natriuresis, and osmotic diuresis.",
            "member_drugs": ["Empagliflozin (Jardiance)", "Dapagliflozin (Farxiga)", "Canagliflozin (Invokana)", "Ertugliflozin (Steglatro)"],
            "indications": ["Type 2 Diabetes Mellitus", "Heart Failure (HFrEF & HFpEF)", "Chronic Kidney Disease (CKD)"],
            "cardiorenal_benefits": "Proven reduction in CV death, HF hospitalization, and CKD progression independent of baseline HbA1c.",
            "shared_warnings": ["Euglycemic DKA risk", "Genitourinary fungal infections / Fournier's gangrene", "Volume depletion / Hypotension", "Ketoacidosis in T1D (Contraindicated)"],
            "egfr_cutoffs": "Initiation: eGFR >=20 mL/min for Dapagliflozin/Empagliflozin (EMPA-KIDNEY, DAPA-CKD). Continue down to dialysis."
        },
        "arnis": {
            "class_name": "ARNI (Angiotensin Receptor-Neprilysin Inhibitor)",
            "mechanism": "Sacubitril inhibits neprilysin (increasing natriuretic peptides, bradykinin); Valsartan blocks AT1 receptor (suppressing RAAS).",
            "member_drugs": ["Sacubitril / Valsartan (Entresto)"],
            "indications": ["Heart Failure with Reduced Ejection Fraction (HFrEF, LVEF <=40%)", "Hypertension"],
            "cardiorenal_benefits": "PARADIGM-HF: 20% reduction in CV death or HF hospitalization vs Enalapril.",
            "shared_warnings": ["Angioedema risk", "Hyperkalemia", "Hypotension", "Fetal toxicity (Contraindicated in pregnancy)"],
            "washout_period": "CRITICAL: 36-hour washout period required when switching from ACE inhibitor to Entresto to avoid severe angioedema."
        },
        "glp1_agonists": {
            "class_name": "GLP-1 Receptor Agonists & Dual GIP/GLP-1 Agonists",
            "mechanism": "Mimics incretin GLP-1/GIP: enhances glucose-dependent insulin secretion, suppresses glucagon, delays gastric emptying, promotes satiety.",
            "member_drugs": ["Semaglutide (Ozempic, Wegovy, Rybelsus)", "Tirzepatide (Mounjaro, Zepbound - Dual GIP/GLP-1)", "Dulaglutide (Trulicity)", "Liraglutide (Victoza, Saxenda)"],
            "indications": ["Type 2 Diabetes Mellitus", "Chronic Weight Management / Obesity", "CKD with T2D (FLOW Trial)", "ASCVD risk reduction"],
            "shared_warnings": ["Pancreatitis risk", "Medullary Thyroid Carcinoma (MTC) risk (Boxed Warning)", "Severe gastroparesis", "Gallbladder disease"],
            "comparative_efficacy": "Weight loss: Tirzepatide > Semaglutide > Dulaglutide. A1c reduction: Tirzepatide > Semaglutide."
        },
        "doacs": {
            "class_name": "Direct Oral Anticoagulants (DOACs / NOACs)",
            "mechanism": "Direct Factor Xa inhibition (Apixaban, Rivaroxaban, Edoxaban) or Direct Thrombin/Factor IIa inhibition (Dabigatran).",
            "member_drugs": ["Apixaban (Eliquis)", "Rivaroxaban (Xarelto)", "Dabigatran (Pradaxa)", "Edoxaban (Savaysa)"],
            "indications": ["Non-valvular Atrial Fibrillation stroke prevention", "DVT / PE treatment & secondary prevention"],
            "shared_warnings": ["Major bleeding", "Epidural / spinal hematoma risk with neuraxial anesthesia", "Avoid abrupt discontinuation without alternative anticoagulant"],
            "reversal_agents": "Andexanet alfa for Apixaban/Rivaroxaban; Idarucizumab (Praxbind) for Dabigatran."
        }
    }

    @classmethod
    def get_class_info(cls, class_query: str) -> Optional[Dict[str, Any]]:
        query_lower = class_query.lower().strip()
        if "sglt2" in query_lower:
            return cls.DRUG_CLASSES.get("sglt2_inhibitors")
        if "arni" in query_lower or "entresto" in query_lower:
            return cls.DRUG_CLASSES.get("arnis")
        if "glp-1" in query_lower or "glp1" in query_lower or "tirzepatide" in query_lower:
            return cls.DRUG_CLASSES.get("glp1_agonists")
        if "doac" in query_lower or "noac" in query_lower or "anticoagulant" in query_lower:
            return cls.DRUG_CLASSES.get("doacs")
        return None
