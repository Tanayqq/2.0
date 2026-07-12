"""
section_utils.py
----------------
Shared utility for normalizing clinical section titles into lowercase canonical keys.
Used by both the ingestion pipeline (parser, chunker) and the retrieval layer (rag_usecase).

Canonical keys match the SECTION_KEYWORDS dict keys in rag_usecase.py.
"""
import re

# Exhaustive map from raw/variant labels → lowercase canonical key
SECTION_SYNONYMS: dict[str, str] = {
    # Contraindications
    "contraindications": "contraindications",
    "contraindication": "contraindications",
    "4 contraindications": "contraindications",

    # Indications
    "indications and usage": "indications",
    "indications": "indications",
    "indication": "indications",
    "1 indications and usage": "indications",

    # Dosage
    "dosage and administration": "dosage",
    "dosage": "dosage",
    "dosages": "dosage",
    "2 dosage and administration": "dosage",

    # Warnings  (boxed warning folds into warnings)
    "warnings and precautions": "warnings",
    "warnings & precautions": "warnings",
    "boxed warning": "warnings",
    "boxed warnings": "warnings",
    "black box warning": "warnings",
    "warnings": "warnings",
    "warning": "warnings",
    "5 warnings and precautions": "warnings",

    # Precautions (distinct canonical key)
    "precautions": "precautions",
    "precaution": "precautions",

    # Drug Interactions
    "drug interactions": "drug interactions",
    "drug interaction": "drug interactions",
    "7 drug interactions": "drug interactions",

    # Pregnancy
    "pregnancy": "pregnancy",
    "use in pregnancy": "pregnancy",
    "pregnancy and lactation": "pregnancy",
    "8.1 pregnancy": "pregnancy",

    # Lactation
    "lactation": "lactation",
    "nursing mothers": "lactation",
    "breast-feeding mothers": "lactation",
    "use in lactation": "lactation",
    "8.2 lactation": "lactation",

    # Pediatric Use
    "pediatric use": "pediatric use",
    "8.4 pediatric use": "pediatric use",
    "use in children": "pediatric use",

    # Geriatric Use
    "geriatric use": "geriatric use",
    "8.5 geriatric use": "geriatric use",
    "use in elderly": "geriatric use",
    "use in geriatric patients": "geriatric use",

    # Adverse Reactions
    "adverse reactions": "adverse reactions",
    "adverse reaction": "adverse reactions",
    "side effects": "adverse reactions",
    "6 adverse reactions": "adverse reactions",

    # Overdosage
    "overdosage": "overdosage",
    "overdose": "overdosage",
    "10 overdosage": "overdosage",

    # Storage
    "storage and handling": "storage",
    "storage": "storage",
    "how supplied": "storage",
    "how supplied/storage and handling": "storage",
    "16 how supplied": "storage",

    # Patient Counseling
    "patient counseling information": "patient counseling information",
    "patient information": "patient counseling information",
    "17 patient counseling information": "patient counseling information",

    # SPL patient package insert — EXPLICITLY excluded (maps to nothing useful)
    "spl patient package insert": "_excluded",
    "patient package insert": "_excluded",
    "medication guide": "_excluded",
    "full prescribing information": "_excluded",
    "full prescribing information: contents": "_excluded",
    "highlights of prescribing information": "_excluded",
}


def normalize_section(title: str) -> str:
    """
    Convert any raw section title into a lowercase canonical key.

    Examples:
        "4 Contraindications"             → "contraindications"
        "CONTRAINDICATIONS"               → "contraindications"
        "Warnings and Precautions"        → "warnings"
        "Boxed Warning"                   → "warnings"
        "SPL Patient Package Insert"      → "_excluded"
        "Unknown section"                 → "unknown section"  (passthrough)

    Returns "_excluded" for noise sections that should be discarded.
    Returns the lowercase passthrough for unrecognised sections.
    """
    if not title:
        return ""

    # Strip leading FDA numbering: "4 Contraindications", "4. Contraindications", "4.1 Sub"
    cleaned = re.sub(r'^\d+[\s\.\-\:]*\d*[\s\.\-\:]*', '', title.strip()).strip()
    lower = cleaned.lower()

    # Exact match first
    if lower in SECTION_SYNONYMS:
        return SECTION_SYNONYMS[lower]

    # Prefix/substring match (handles minor suffix variants)
    for syn, canonical in SECTION_SYNONYMS.items():
        if lower.startswith(syn) or syn in lower:
            return canonical

    # Passthrough — preserve the lowercased title so logs are readable
    return lower
