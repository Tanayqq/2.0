import sys
sys.path.insert(0, '.')
from app.infrastructure.vector_db import QdrantAdapter

db = QdrantAdapter(
    url='https://b92d5ef7-a1fe-429b-86e0-67cb239dd428.us-west-1-0.aws.cloud.qdrant.io',
    api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MmI0NTYzY2YtNTQyOC00NDdiLWE2ZDUtYjY2YmFkNjBiYTM0In0.BODxwJ_pzKQprCOosZZcLRtrQ510diLNfOSVAtyu62U'
)

docs = db.scroll_by_drug_sections(
    drug_name='albuterol',
    canonical_sections=['dosage_and_administration', 'drug_interactions', 'indications', 'contraindications', 'warnings'],
    limit_per_section=2
)
print(f'Top-up returned {len(docs)} docs')
for d in docs:
    sec = d.metadata.get('canonical_section', 'unknown')
    print(f'  section={sec} score={d.score} content_len={len(d.content)}')
