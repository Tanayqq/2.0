# Implementation Plan — Structured Clinical Knowledge Engine (Version 5)

This plan outlines the streamlined, production-ready architecture to upgrade MedRef into a structured clinical knowledge engine. Every indexed drug will contain two complementary layers: **Structured Entity Profile** (deterministic metadata stored in Qdrant) and **Evidence-based RAG Sections** (vector chunks).

---

## User Review Required

> [!IMPORTANT]
> - **Milestone Division**: Execution will be split into modular phases:
>   *   **Phase A**: Identity Engine & Registry (Generic, Brand, Aliases, Class, ATC, RxNorm, UNII, Manufacturer).
>   *   **Phase B**: Clinical Profile (Mechanism, Indications, Dosing, Contraindications, Warnings, Structured Side Effects/Interactions, Storage, Patient Counseling).
>   *   **Phase C**: Intent Router & Retrieval Routing (Identity -> Profile; Clinical -> RAG).
>   *   **Phase D**: Authority & Future Expansion (CDSCO, EMA, non-drug entities - postponed for Version 2).
> - **Categorical Confidence & Evidence Strength**: Replace float scores with categorical strings (`"deterministic"`, `"validated"`, `"fallback_llm"`, `"missing"`) and introduce `evidence_strength` (`"HIGH"` for Official Label, `"MEDIUM"` for Clinical Study).
> - **Structured Side Effects & Interactions**:
>   *   *Side Effects*: categorised into `Common`, `Less Common`, `Rare`, and `Life-threatening`.
>   *   *Interactions*: categorised into `Contraindicated`, `Major`, `Moderate`, `Minor`, and `Monitoring Required`.
> - **Citation-to-Profile Linking**: Structured fields link to the exact vector `chunk_id` for deep clinician auditing.

---

## Proposed Changes

### 1. Simplified Schema & Provenance Models
We will define Pydantic models with categorical confidence, evidence strength, and chunk linking.

#### [NEW] [profile_schema.py](file:///C:/Users/Tanay%20Kumar/Desktop/2.0/backend/ingestion/pipeline/profile_schema.py)
Defines the schema for each profile field:
```python
from pydantic import BaseModel
from typing import Any, Optional, List, Dict

class ProfileField(BaseModel):
    value: Any = None
    source: str = ""  # e.g., "DailyMed", "openFDA"
    authority: str = "FDA"  # Default to "FDA" for Phase A/B
    section: str = ""  # e.g., "Dosage and Administration"
    chunk_id: Optional[str] = None  # Exact chunk UUID producing this field
    confidence: str = "deterministic"  # "deterministic", "validated", "fallback_llm", "missing"
    evidence_strength: str = "HIGH"  # "HIGH" (Official Label), "MEDIUM" (Clinical Study)
    status: str = "present"  # "present", "missing", "not_applicable", "not_ingested"
    reason: Optional[str] = None
    
    # Ingestion Lineage & Freshness
    parser_version: str = "4.0"
    pipeline_version: str = "3.5"
    document_checksum: str = ""
    last_verified: str = ""  # ISO Date YYYY-MM-DD
```
Defines:
- **RegistryEntry**: `entity_id` (e.g. `drug:metformin`), `entity_type: str = "drug"`, `generic_name`, `preferred_authority: str = "FDA"`, `aliases` (List).
- **DrugIdentityProfile**: `entity_id`, `generic_name`, `brand_names` (List), `drug_class`, `prescription_status`, `atc_code`, `rxnorm_id`, `unii`, `manufacturer`.
- **DrugClinicalProfile**: `entity_id`, `mechanism`, `indications` (List), `dosing` (dict), `contraindications` (List), `warnings` (List), `side_effects` (dict with keys: `common`, `less_common`, `rare`, `life_threatening`), `drug_interactions` (dict with keys: `contraindicated`, `major`, `moderate`, `minor`, `monitoring_required`), `special_populations` (dict), `storage` (dict), `patient_counseling` (dict).

---

### 2. Ingestion Pipeline (Phase A & B)
We will implement parsing rules to extract fields deterministically.

#### [NEW] [profile_parser.py](file:///C:/Users/Tanay%20Kumar/Desktop/2.0/backend/ingestion/pipeline/profile_parser.py)
- **DeterministicProfileParser**:
  - Extracts identity metadata (generic name, brand names, drug class) from DailyMed and openFDA.
  - Implements regex-based segment scrapers to extract Clinical Profile fields.
  - Extracts side effects and interactions and categorises them strictly.
  - Falls back to the LLM (using Groq) only if deterministic parsing confidence is low (marked as `"fallback_llm"`).

---

### 3. Qdrant Registry, Profile Store & Versioning
We will store profiles and registries in separate collections in Qdrant.

#### [NEW] [profile_store.py](file:///C:/Users/Tanay%20Kumar/Desktop/2.0/backend/app/infrastructure/profile_store.py)
- **StructuredProfileStore**:
  - Manages `entity_registry`, `drug_profiles` (separated into identity and clinical), and `drug_aliases` collections.
  - On startup, loads brand aliases into memory cache for **O(1) brand-to-generic resolution**.
  - Checks document checksums during ingestion to perform **incremental updates**.

---

### 4. Query Intent Classifier & Router (Phase C)
 we will optimize retrieval routing to resolve brands instantly and bypass RAG for identity queries.

#### [MODIFY] [rag_usecase.py](file:///C:/Users/Tanay%20Kumar/Desktop/2.0/backend/app/usecases/rag_usecase.py)
- **Query Intent Classifier**:
  - Parses query text to detect intent (`identity` vs `clinical`).
- **Retrieval Router**:
  - Step 1: Resolves brand using in-memory `drug_aliases` cache.
  - Step 2: Checks query intent. If `identity`, retrieves from the structured identity index directly and returns.
  - Step 3: If `clinical`, executes vector RAG using the resolved `entity_id` and `authority="FDA"`.
- **Latency Tracker**:
  - Returns millisecond latency splits for `alias_resolution_ms`, `identity_lookup_ms`, `vector_search_ms`, `rerank_ms`, and `generation_ms`.

---

### 5. Ingestion Confidence Dashboard & Health Score
We will report detailed completeness scores.

#### [MODIFY] [validator.py](file:///C:/Users/Tanay%20Kumar/Desktop/2.0/backend/ingestion/pipeline/validator.py)
- Calculates split completeness scores:
  - `Identity Score` (100% if generic, brands, and class exist)
  - `Clinical Score` (based on core categories)
  - `Metadata Score` (for provenance tags)
  - `Sources Score` (for source tracking)
- Compiles the **Ingestion Confidence Dashboard** in `INGESTION_REPORT.md` (e.g., listing completeness splits and missing reasons per drug).

---

## Verification Plan

### Automated Tests
- Run `pytest backend/tests/test_profile_builder.py` to verify brand resolution, intent classification, validation rules, and schema formatting.
- Run `pytest backend/tests/` to verify overall system integrity.

### Manual Verification
1. Run ingestion on all 105 drugs to generate the structured profiles:
   ```bash
   python backend/scripts/run_all_drugs_ingestion.py
   ```
2. Verify that Qdrant contains the `entity_registry`, `drug_profiles`, and `drug_aliases` collections.
3. Query `Novamox` and verify it resolves instantly to `Amoxicillin` and displays the structured identity/RAG clinical data correctly.
