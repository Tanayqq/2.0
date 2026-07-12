"""
section_utils.py
----------------
Shared utility for normalizing clinical section titles into lowercase canonical keys.
Used by both the ingestion pipeline (parser, chunker) and the retrieval layer (rag_usecase).

Canonical keys match the SECTION_KEYWORDS dict keys in rag_usecase.py.

Design rules
============
1. The normalizer MUST be deterministic and side-effect free.
2. Exact match is always tried first (fastest, most specific).
3. Prefix match is tried second (handles "4 Contraindications").
4. Substring match is intentionally NOT used — it causes false positives
   e.g. "indication" substring-matching inside "contraindications".
5. Fallback: strip numbering, lowercase, and return as-is so logs stay readable.
"""
import re

# ---------------------------------------------------------------------------
# Exhaustive map: raw/variant label → lowercase canonical key
# ---------------------------------------------------------------------------
SECTION_SYNONYMS: dict[str, str] = {
    # Contraindications
    "contraindications": "contraindications",
    "contraindication": "contraindications",
    "contraindicated": "contraindications",

    # Indications
    "indications and usage": "indications",
    "indications": "indications",
    "indication": "indications",

    # Dosage
    "dosage and administration": "dosage",
    "dosage": "dosage",
    "dosages": "dosage",

    # Warnings  (boxed warning folds into warnings)
    "warnings and precautions": "warnings",
    "warnings & precautions": "warnings",
    "boxed warning": "warnings",
    "boxed warnings": "warnings",
    "black box warning": "warnings",
    "black box": "warnings",
    "warnings": "warnings",
    "warning": "warnings",

    # Precautions (distinct canonical key)
    "precautions": "precautions",
    "precaution": "precautions",

    # Drug Interactions
    "drug interactions": "drug interactions",
    "drug interaction": "drug interactions",
    "drug-drug interactions": "drug interactions",

    # Pregnancy
    "pregnancy": "pregnancy",
    "use in pregnancy": "pregnancy",
    "pregnancy and lactation": "pregnancy",

    # Lactation
    "lactation": "lactation",
    "nursing mothers": "lactation",
    "breast-feeding mothers": "lactation",
    "use in lactation": "lactation",

    # Pediatric Use
    "pediatric use": "pediatric use",
    "use in children": "pediatric use",

    # Geriatric Use
    "geriatric use": "geriatric use",
    "use in elderly": "geriatric use",
    "use in geriatric patients": "geriatric use",

    # Adverse Reactions
    "adverse reactions": "adverse reactions",
    "adverse reaction": "adverse reactions",
    "side effects": "adverse reactions",

    # Overdosage
    "overdosage": "overdosage",
    "overdose": "overdosage",

    # Storage
    "storage and handling": "storage",
    "storage": "storage",
    "how supplied": "storage",
    "how supplied/storage and handling": "storage",

    # Patient Counseling
    "patient counseling information": "patient counseling information",
    "patient information": "patient counseling information",

    # SPL patient package insert — EXPLICITLY excluded (maps to nothing useful)
    "spl patient package insert": "_excluded",
    "patient package insert": "_excluded",
    "medication guide": "_excluded",
    "full prescribing information": "_excluded",
    "full prescribing information: contents": "_excluded",
    "highlights of prescribing information": "_excluded",
}

# Pre-built sorted list: longest key first, so prefix matching is greedy-safe
_SORTED_SYNONYMS = sorted(SECTION_SYNONYMS.items(), key=lambda kv: -len(kv[0]))

# Regex to strip leading FDA numbering: "4 Contra", "4. Contra", "4.1 Contra", "12.3 Contra"
_LEADING_NUM_RE = re.compile(r'^\d+(?:\.\d+)?\s*[\.\-\:]?\s*')


def normalize_section(title: str) -> str:
    """
    Convert any raw section title into a lowercase canonical key.

    Algorithm
    ---------
    1. Strip whitespace.
    2. Strip leading FDA section numbers (4, 4., 4.1, 12.3 …).
    3. Lowercase.
    4. Exact match against SECTION_SYNONYMS.
    5. Prefix match (longest-key-first to avoid short-key false positives).
    6. Passthrough (return lowercased stripped form).

    NOTE: Substring match is intentionally absent to prevent false positives
    such as "indication" matching inside "contraindications".

    Examples
    --------
    "4 Contraindications"             → "contraindications"
    "CONTRAINDICATIONS"               → "contraindications"
    "Warnings and Precautions"        → "warnings"
    "Boxed Warning"                   → "warnings"
    "SPL Patient Package Insert"      → "_excluded"
    "Adverse Reactions"               → "adverse reactions"
    "Unknown section"                 → "unknown section"   (passthrough)
    """
    if not title or not title.strip():
        return ""

    # Step 1: strip leading FDA numbering
    cleaned = _LEADING_NUM_RE.sub("", title.strip()).strip()

    # Step 2: lowercase
    lower = cleaned.lower()

    # Step 3: exact match (O(1))
    if lower in SECTION_SYNONYMS:
        return SECTION_SYNONYMS[lower]

    # Step 4: prefix match — longest key first to prevent short-key shadowing
    for syn, canonical in _SORTED_SYNONYMS:
        if lower.startswith(syn):
            return canonical

    # Step 5: passthrough — readable in logs
    return lower
