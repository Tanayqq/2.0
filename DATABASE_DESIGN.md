# Database Design

## Vector Database: Qdrant

### Collections
Qdrant is designed for multiple collections from the start to support modular expansion:
- `openfda_labels`: Collection for drug label data from openFDA/DailyMed.
- `clinical_guidelines`: Future collection for standard treatment guidelines.
- `drug_interactions`: Future collection for interaction references.

### Metadata Schema (Payload)
Every embedded chunk in Qdrant will store the following structured payload to enable hybrid filtering and precise attribution:
```json
{
  "document_id": "uuid",
  "source": "openFDA",          // openFDA, DailyMed, RxNorm, etc.
  "category": "drug_label",     // guideline, drug_label, interaction
  "title": "Lisinopril 10mg Tablets",
  "section": "Contraindications",
  "url": "https://...",
  "chunk_index": 2,
  "last_updated": "2023-10-01T00:00:00Z"
}
```

### Indexes
- **Vector Index**: HNSW index for high-performance vector similarity search.
- **Payload Indexes**: Create exact-match indexes on `source` and `category` to allow fast pre-filtering (e.g., "Only search DailyMed").

## Future Collections
- `patient_guidelines`: For simplified patient-facing documents, kept separate to avoid mixing clinical depth with patient education.
- `hospital_protocols`: Specific to offline hospital deployments to store internal SOPs.

## Migration Strategy
- Store original raw documents in Object Storage (e.g., S3 / MinIO).
- If embedding models change (e.g., upgrading MedCPT), re-embed from the raw text in Object Storage into a new Qdrant collection, then atomically swap the alias to point to the new collection to ensure zero downtime.
