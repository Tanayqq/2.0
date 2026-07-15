from qdrant_client import QdrantClient
from collections import defaultdict

QDRANT_URL = 'https://b92d5ef7-a1fe-429b-86e0-67cb239dd428.us-west-1-0.aws.cloud.qdrant.io'
QDRANT_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MmI0NTYzY2YtNTQyOC00NDdiLWE2ZDUtYjY2YmFkNjBiYTM0In0.BODxwJ_pzKQprCOosZZcLRtrQ510diLNfOSVAtyu62U'

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Scroll all chunks
all_chunks = []
offset = None
while True:
    res, next_offset = client.scroll('openfda_labels', limit=250, offset=offset, with_payload=True, with_vectors=False)
    all_chunks.extend(res)
    if next_offset is None:
        break
    offset = next_offset

print(f'Total chunks: {len(all_chunks)}')

drug_sections = defaultdict(set)
drug_counts = defaultdict(int)
for p in all_chunks:
    drug = p.payload.get('drug_name', '').lower()
    sec = p.payload.get('canonical_section', 'unknown')
    drug_sections[drug].add(sec)
    drug_counts[drug] += 1

print(f'Total unique drugs with chunks: {len(drug_counts)}')
print()

print('DRUGS MISSING DOSING OR INTERACTIONS:')
print('-' * 80)
bad_drugs = []
for drug in sorted(drug_counts.keys()):
    secs = drug_sections[drug]
    has_dos = any('dos' in s for s in secs)
    has_int = any('interact' in s or 'co_admin' in s for s in secs)
    cnt = drug_counts[drug]
    if not has_dos or not has_int:
        bad_drugs.append(drug)
        print(f"{drug:<30} chunks={cnt:<5} has_dosing={str(has_dos):<6} has_interactions={str(has_int)}")

print()
print(f'Drugs missing dosing or interactions: {len(bad_drugs)} / {len(drug_counts)}')
print()

# Also show what sections Albuterol has
print('ALBUTEROL sections:', sorted(drug_sections.get('albuterol', set())))
print('METFORMIN sections:', sorted(drug_sections.get('metformin', set())))
print('WARFARIN sections:', sorted(drug_sections.get('warfarin', set())))
