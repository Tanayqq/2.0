# Retrieval Quality Evaluation Report

## Summary Metrics
- **Total Test Cases**: 15

### Full-Match Metrics (Drug & Section)
- **Mean Recall@5**: 73.33%
- **Mean Recall@10**: 80.00%
- **MRR (Mean Reciprocal Rank)**: 0.5178
- **Top-1 Match Accuracy**: 33.33%

### NDCG Metrics
- **Mean NDCG@5**: 0.9253
- **Mean NDCG@10**: 0.9533

### Drug-Only Metrics
- **Mean Recall@5**: 100.00%
- **Mean Recall@10**: 100.00%
- **MRR**: 1.0000

## Detailed Query Analysis
| Query | Expected Drug | Expected Section | Full Match Rank | Drug Match Rank | Top Retrieved Drug / Section | NDCG@5 | MRR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Pregnancy safety of Acetaminophen` | Acetaminophen | `pregnancy` | Rank 1 | Rank 1 | Acetaminophen / pregnancy | 1.0000 | 1.0000 |
| `Omeprazole pregnancy safety` | Omeprazole | `pregnancy` | Rank 1 | Rank 1 | Omeprazole / pregnancy | 0.7602 | 1.0000 |
| `Renal dose adjustment for Furosemide` | Furosemide | `renal_impairment` | Rank 2 | Rank 1 | Furosemide / dosage_and_administration | 0.9065 | 0.5000 |
| `Pediatric use of Furosemide` | Furosemide | `pediatric_use` | Rank 10 | Rank 1 | Furosemide / lactation | 0.7467 | 0.1000 |
| `Indications for Furosemide` | Furosemide | `indications` | Rank 2 | Rank 1 | Furosemide / adverse_reactions | 0.9065 | 0.5000 |
| `Storage conditions for Furosemide` | Furosemide | `storage` | Rank 1 | Rank 1 | Furosemide / storage | 1.0000 | 1.0000 |
| `Contraindications of Lisinopril` | Lisinopril | `contraindications` | Rank 3 | Rank 1 | Lisinopril / adverse_reactions | 0.8734 | 0.3333 |
| `Metformin dosage` | Metformin | `dosage_and_administration` | Rank 2 | Rank 1 | Metformin / pharmacokinetics | 0.9065 | 0.5000 |
| `Warfarin interactions` | Warfarin | `drug_interactions` | Not in top 10 | Rank 1 | Warfarin / general_information | 1.0000 | 0.0000 |
| `Novamox dosage` | Amoxicillin | `dosage_and_administration` | Not in top 10 | Rank 1 | Amoxicillin / renal_impairment | 1.0000 | 0.0000 |
| `Amoxicillin renal safety` | Amoxicillin | `renal_impairment` | Rank 3 | Rank 1 | Amoxicillin / precautions | 0.8734 | 0.3333 |
| `Atorvastatin pregnancy` | Atorvastatin | `pregnancy` | Rank 1 | Rank 1 | Atorvastatin / pregnancy | 1.0000 | 1.0000 |
| `Ibuprofen pediatric dose` | Ibuprofen | `pediatric_use` | Not in top 10 | Rank 1 | Ibuprofen / precautions | 1.0000 | 0.0000 |
| `Gabapentin precautions` | Gabapentin | `precautions` | Rank 2 | Rank 1 | Gabapentin / adverse_reactions | 0.9065 | 0.5000 |
| `Levothyroxine storage` | Levothyroxine | `storage` | Rank 1 | Rank 1 | Levothyroxine / storage | 1.0000 | 1.0000 |