"""
section_utils.py
----------------
Shared utility for normalizing clinical section titles into lowercase canonical keys.
Used by both the ingestion pipeline (parser, chunker) and the retrieval layer (rag_usecase).

Canonical keys match the 38 clinical sections.
"""
import re

# ---------------------------------------------------------------------------
# Exhaustive map: raw/variant label → lowercase canonical key
# ---------------------------------------------------------------------------
SECTION_SYNONYMS: dict[str, str] = {
    # Mechanism of Action
    "mechanism of action": "mechanism_of_action",
    "mechanism": "mechanism_of_action",
    "pharmacological action": "mechanism_of_action",
    
    # Indications
    "indications and usage": "indications",
    "indications": "indications",
    "indication": "indications",
    "indicated": "indications",
    "approved uses": "indications",

    # Clinical Pharmacology
    "clinical pharmacology": "clinical_pharmacology",
    "pharmacology": "clinical_pharmacology",
    
    # Pharmacokinetics
    "pharmacokinetics": "pharmacokinetics",
    "pharmacokinetic": "pharmacokinetics",
    "pk": "pharmacokinetics",
    "absorption distribution metabolism elimination": "pharmacokinetics",
    
    # Pharmacodynamics
    "pharmacodynamics": "pharmacodynamics",
    "pharmacodynamic": "pharmacodynamics",
    
    # Adverse Reactions
    "adverse reactions": "adverse_reactions",
    "adverse reaction": "adverse_reactions",
    "side effects": "adverse_reactions",
    "side effect": "adverse_reactions",
    "undesirable effects": "adverse_reactions",
    "postmarketing experience": "adverse_reactions",
    "clinical trials experience": "adverse_reactions",
    "clinical studies experience": "adverse_reactions",
    
    # Overdosage
    "overdosage": "overdosage",
    "overdose": "overdosage",
    "acute toxicity": "overdosage",
    
    # Storage
    "storage and handling": "storage",
    "storage": "storage",
    "how supplied": "storage",
    "how supplied/storage and handling": "storage",
    "supply": "storage",
    
    # Patient Counseling
    "patient counseling information": "patient_counseling",
    "patient counseling": "patient_counseling",
    "patient information": "patient_counseling",
    "information for patients": "patient_counseling",
    "counseling": "patient_counseling",

    # Dosage & Administration — comprehensive synonym set
    "dosage and administration": "dosage_and_administration",
    "dosage": "dosage_and_administration",
    "dosages": "dosage_and_administration",
    "dosing": "dosage_and_administration",
    "dose": "dosage_and_administration",
    "posology": "dosage_and_administration",                     # EMA/European labels
    "recommended dose": "dosage_and_administration",
    "recommended dosage": "dosage_and_administration",
    "dosing information": "dosage_and_administration",
    "dosing instructions": "dosage_and_administration",
    "doses and administration": "dosage_and_administration",
    "dose and administration": "dosage_and_administration",
    "how to take": "dosage_and_administration",
    "how to use": "dosage_and_administration",
    "dose regimen": "dosage_and_administration",
    "dosage regimen": "dosage_and_administration",
    "recommended dose and administration": "dosage_and_administration",
    "dosage and use": "dosage_and_administration",
    "dose and use": "dosage_and_administration",
    
    # Administration
    "administration": "administration",
    "instructions for use": "administration",
    "method of administration": "administration",
    "how to administer": "administration",
    
    # Dosage Forms
    "dosage forms": "dosage_forms",
    "dosage forms and strengths": "dosage_forms",
    "dosage form": "dosage_forms",
    
    # Strengths
    "strengths": "strengths",
    "strength": "strengths",
    
    # Maximum Dose
    "maximum dose": "maximum_dose",
    "maximum dosage": "maximum_dose",
    "max dose": "maximum_dose",
    
    # Loading Dose
    "loading dose": "loading_dose",
    "loading dosage": "loading_dose",
    
    # Maintenance Dose
    "maintenance dose": "maintenance_dose",
    "maintenance dosage": "maintenance_dose",
    
    # Renal Dose
    "renal dose": "renal_dose",
    "renal dosing": "renal_dose",
    "dosage in renal impairment": "renal_dose",
    
    # Hepatic Dose
    "hepatic dose": "hepatic_dose",
    "hepatic dosing": "hepatic_dose",
    "dosage in hepatic impairment": "hepatic_dose",
    
    # Dose Adjustment
    "dose adjustment": "dose_adjustment",
    "dosage adjustment": "dose_adjustment",
    "dosage modifications": "dose_adjustment",
    "dose modification": "dose_adjustment",
    "adjustments": "dose_adjustment",

    # Contraindications
    "contraindications": "contraindications",
    "contraindication": "contraindications",
    "contraindicated": "contraindications",
    
    # Boxed Warning
    "boxed warning": "boxed_warning",
    "boxed warnings": "boxed_warning",
    "black box warning": "boxed_warning",
    "black box": "boxed_warning",
    
    # Warnings
    "warnings": "warnings",
    "warning": "warnings",
    
    # Warnings and Precautions
    "warnings and precautions": "warnings_and_precautions",
    "warnings & precautions": "warnings_and_precautions",
    
    # Precautions
    "precautions": "precautions",
    "precaution": "precautions",
    
    # Drug Interactions
    "drug interactions": "drug_interactions",
    "drug interaction": "drug_interactions",
    "drug-drug interactions": "drug_interactions",
    "interactions": "drug_interactions",
    "interaction": "drug_interactions",
    
    # Alcohol Interactions
    "alcohol interactions": "alcohol_interactions",
    "alcohol interaction": "alcohol_interactions",
    "interaction with alcohol": "alcohol_interactions",
    
    # Food Interactions
    "food interactions": "food_interactions",
    "food interaction": "food_interactions",
    "interaction with food": "food_interactions",
    
    # CYP Interactions
    "cyp interactions": "cyp_interactions",
    "cyp interaction": "cyp_interactions",
    "cytochrome p450": "cyp_interactions",
    
    # Laboratory Interactions
    "laboratory interactions": "laboratory_interactions",
    "laboratory interaction": "laboratory_interactions",
    "drug and laboratory test interactions": "laboratory_interactions",
    "drug & laboratory test interactions": "laboratory_interactions",
    
    # Monitoring
    "monitoring": "monitoring",
    "monitoring parameter": "monitoring",
    "patient monitoring": "monitoring",
    "therapeutic monitoring": "monitoring",
    
    # Pregnancy
    "pregnancy": "pregnancy",
    "use in pregnancy": "pregnancy",
    "pregnancy and lactation": "pregnancy",
    "pregnancy warning": "pregnancy",
    
    # Lactation
    "lactation": "lactation",
    "nursing mothers": "lactation",
    "breast-feeding mothers": "lactation",
    "breastfeeding": "lactation",
    "use in lactation": "lactation",
    
    # Pediatric Use
    "pediatric use": "pediatric_use",
    "use in children": "pediatric_use",
    "pediatric": "pediatric_use",
    "children": "pediatric_use",
    
    # Geriatric Use
    "geriatric use": "geriatric_use",
    "use in elderly": "geriatric_use",
    "use in geriatric patients": "geriatric_use",
    "geriatric": "geriatric_use",
    "elderly": "geriatric_use",
    
    # Renal Impairment
    "renal impairment": "renal_impairment",
    "patients with renal impairment": "renal_impairment",
    "renal insufficiency": "renal_impairment",
    
    # Hepatic Impairment
    "hepatic impairment": "hepatic_impairment",
    "patients with hepatic impairment": "hepatic_impairment",
    "hepatic insufficiency": "hepatic_impairment",
    
    # Dialysis
    "dialysis": "dialysis",
    "hemodialysis": "dialysis",
    
    # Pharmacogenomics
    "pharmacogenomics": "pharmacogenomics",
    "pharmacogenomic": "pharmacogenomics",
    "genetics": "pharmacogenomics",

    # SPL patient package insert — EXPLICITLY excluded (maps to nothing useful)
    "spl patient package insert": "_excluded",
    "patient package insert": "_excluded",
    "medication guide": "_excluded",
    "full prescribing information": "_excluded",
    "full prescribing information: contents": "_excluded",
    "highlights of prescribing information": "_excluded",
}

# Dynamic Grouping mappings
SECTION_CATEGORIES: dict[str, str] = {
    "mechanism_of_action": "Clinical Overview",
    "indications": "Clinical Overview",
    "clinical_pharmacology": "Clinical Overview",
    "pharmacokinetics": "Clinical Overview",
    "pharmacodynamics": "Clinical Overview",
    "adverse_reactions": "Clinical Overview",
    "overdosage": "Clinical Overview",
    "storage": "Clinical Overview",
    "patient_counseling": "Clinical Overview",

    "dosage_and_administration": "Dosing & Administration",
    "administration": "Dosing & Administration",
    "dosage_forms": "Dosing & Administration",
    "strengths": "Dosing & Administration",
    "maximum_dose": "Dosing & Administration",
    "loading_dose": "Dosing & Administration",
    "maintenance_dose": "Dosing & Administration",
    "renal_dose": "Dosing & Administration",
    "hepatic_dose": "Dosing & Administration",
    "dose_adjustment": "Dosing & Administration",

    "contraindications": "Contraindications & Safety",
    "boxed_warning": "Contraindications & Safety",
    "warnings": "Contraindications & Safety",
    "warnings_and_precautions": "Contraindications & Safety",
    "precautions": "Contraindications & Safety",

    "drug_interactions": "Co-Administration Risks",
    "alcohol_interactions": "Co-Administration Risks",
    "food_interactions": "Co-Administration Risks",
    "cyp_interactions": "Co-Administration Risks",
    "laboratory_interactions": "Co-Administration Risks",
    "monitoring": "Co-Administration Risks",

    "pregnancy": "Special Populations",
    "lactation": "Special Populations",
    "pediatric_use": "Special Populations",
    "geriatric_use": "Special Populations",
    "renal_impairment": "Special Populations",
    "hepatic_impairment": "Special Populations",
    "dialysis": "Special Populations",
    "pharmacogenomics": "Special Populations",
}

SECTION_POPULATIONS: dict[str, str] = {
    "pregnancy": "pregnancy",
    "lactation": "lactation",
    "pediatric_use": "pediatric",
    "geriatric_use": "geriatric",
    "renal_impairment": "renal",
    "hepatic_impairment": "hepatic",
    "dialysis": "dialysis",
}

# Pre-built sorted list: longest key first, so prefix matching is greedy-safe
_SORTED_SYNONYMS = sorted(SECTION_SYNONYMS.items(), key=lambda kv: -len(kv[0]))

# Regex to strip leading FDA numbering: "4 Contra", "4. Contra", "4.1 Contra", "12.3 Contra"
_LEADING_NUM_RE = re.compile(r'^\d+(?:\.\d+)?\s*[\.\-\:]?\s*')


def normalize_section(title: str) -> str:
    """
    Convert any raw section title into a lowercase canonical key.
    """
    if not title or not title.strip():
        return ""

    # Step 1: strip leading FDA numbering
    cleaned = _LEADING_NUM_RE.sub("", title.strip()).strip()

    # Step 2: remove extra punctuation and spaces for comparison
    # Replace & with and to handle "Warnings & Precautions" -> "Warnings and Precautions"
    cleaned_comparison = cleaned.replace("&", "and")
    cleaned_comparison = re.sub(r'[^\w\s-]', '', cleaned_comparison).strip()
    cleaned_comparison = re.sub(r'\s+', ' ', cleaned_comparison)

    # Step 3: lowercase
    lower = cleaned_comparison.lower()

    # Step 4: exact match (O(1))
    if lower in SECTION_SYNONYMS:
        return SECTION_SYNONYMS[lower]

    # Step 5: prefix match — longest key first to prevent short-key shadowing
    for syn, canonical in _SORTED_SYNONYMS:
        if lower.startswith(syn):
            return canonical

    # Step 6: passthrough — readable in logs, but replace spaces with underscores for canonical style
    # if it maps to any common category, we can normalize it
    normalized_passthrough = re.sub(r'[\s-]+', '_', lower)
    return normalized_passthrough


def get_clinical_category(canonical_key: str) -> str:
    """
    Get the clinical category for a given canonical section key.
    Defaults to 'Clinical Overview'.
    """
    return SECTION_CATEGORIES.get(canonical_key, "Clinical Overview")


def get_patient_population(canonical_key: str) -> str:
    """
    Get the target patient population for a given canonical section key.
    Defaults to 'general'.
    """
    return SECTION_POPULATIONS.get(canonical_key, "general")
