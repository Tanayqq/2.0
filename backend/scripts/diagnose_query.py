"""
Diagnostic script: simulate the section detection and normalization pipeline
for the exact query shown in the screenshot.

Run from project root:
    python backend/scripts/diagnose_query.py
"""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.app.section_utils import normalize_section

SECTION_KEYWORDS = {
    "contraindications": ["contraindication", "contraindications", "contraindicated"],
    "warnings": ["warning", "warnings", "boxed warning", "boxed warnings", "black box", "blackbox"],
    "precautions": ["precaution", "precautions"],
    "pregnancy": ["pregnancy", "pregnant", "teratogenic", "fetus", "fetal"],
    "lactation": ["lactation", "nursing", "breast milk", "breastfeeding", "human milk"],
    "pediatric use": ["pediatric", "pediatrics", "child", "children", "infant", "infants", "adolescent", "adolescents"],
    "geriatric use": ["geriatric", "geriatrics", "elderly", "older patients", "aging"],
    "adverse reactions": ["adverse", "adverse reaction", "adverse reactions", "side effect", "side effects"],
    "overdosage": ["overdosage", "overdose", "overdoses"],
    "storage": ["storage", "handling", "supplied", "store", "keep"],
    "drug interactions": ["interaction", "interactions", "drug interaction", "drug interactions", "concomitant"],
    "dosage": ["dosage", "dosages", "administration", "dosing", "dose", "doses"],
    "indications": ["indication", "indications", "indicated"],
    "patient counseling information": ["counseling", "patient counseling"]
}

queries = [
    "Using ONLY the indexed corpus Summarize Metformin contraindications. Every inline citation must exist in Sources Referenced. Every bibliography entry must be referenced at least once. Never include unused sources.",
    "Summarize Metformin contraindications",
    "What are the contraindications of Metformin?",
    "contraindications of metformin",
]

print("=" * 80)
print("SECTION DETECTION DIAGNOSTIC")
print("=" * 80)

for q in queries:
    q_lower = q.lower()
    detected = []
    for canonical_sec, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', q_lower):
                detected.append(canonical_sec)
                break
    detected = list(set(detected))
    print(f"\nQuery: {q[:90]}")
    print(f"  Detected sections: {detected}")
    if not detected:
        print("  WARNING: NO SECTIONS DETECTED")
    elif "contraindications" in detected:
        print("  OK: 'contraindications' correctly detected")
    else:
        print(f"  WRONG sections detected: {detected}")

print("\n" + "=" * 80)
print("NORMALIZE_SECTION TESTS (simulating Qdrant payload values)")
print("=" * 80)

qdrant_section_values = [
    "Contraindications",
    "contraindications",
    "CONTRAINDICATIONS",
    "4 Contraindications",
    "4. Contraindications",
    "Contraindication",
    "Warnings",
    "Warnings and Precautions",
    "Adverse Reactions",
    "SPL Patient Package Insert",
    "drug_label",
    "",
]

requested = ["contraindications"]
print(f"\nRequested sections: {requested}\n")

for raw in qdrant_section_values:
    normalized = normalize_section(raw)
    passes = normalized in requested
    if not raw:
        status = "SKIP (empty)"
    elif passes:
        status = "PASS"
    else:
        status = "DROP"
    print(f"  raw='{raw:<42}'  normalized='{normalized:<30}'  {status}")

print()
print("KEY: If 'drug_label' normalizes to something not in requested -> it gets DROPped (CORRECT)")
print("KEY: The _resolve_raw_section() helper reads 'section' key FIRST, not 'category'")
