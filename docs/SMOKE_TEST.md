# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-14T17:09:54.016726Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Chunks Retrieved | Top Score | Latency (ms) | Status |
|---|---|---|---|---|
| `Contraindications of Metformin` | 5 | 0.6970 | 960ms | ✅ PASS |
| `Side effects of Atorvastatin` | 5 | 0.7719 | 347ms | ✅ PASS |
| `Lisinopril warnings` | 5 | 0.6187 | 399ms | ✅ PASS |
| `Warfarin interactions` | 5 | 0.6576 | 288ms | ✅ PASS |
| `Amoxicillin dosage` | 5 | 0.7531 | 357ms | ✅ PASS |
| `Ibuprofen pregnancy` | 5 | 0.6998 | 307ms | ✅ PASS |
| `Losartan contraindications` | 5 | 0.7291 | 297ms | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Metformin" (Status: ✅ PASS)
*   **Latency:** 960ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `848f8feb-ae5a-56be-8221-1b5b32015bcd` | 0.6970 | DailyMed | The following adverse reactions have been identified during post approval use of metformin. Because ... |
| 2 | `37dab858-d4d0-50f6-99e9-60eca436ebd2` | 0.6608 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with:  Severe ... |
| 3 | `1b0103f7-6ff5-5847-ac13-5b7472afcb5b` | 0.6605 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with: Severe R... |
| 4 | `aeb9cec5-44dd-55c5-af63-1369d103d571` | 0.6508 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |
| 5 | `9945c80b-5242-57eb-805c-02506fe2d69d` | 0.6508 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |

### Query: "Side effects of Atorvastatin" (Status: ✅ PASS)
*   **Latency:** 347ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `3a05f30e-2f5c-5f3b-9656-02303f305c22` | 0.7719 | DailyMed | Increase in blood sugar level.Your blood sugar level may increase while you are taking atorvastatin ... |
| 2 | `e196584f-82ac-5d01-a36e-b18b156f81c4` | 0.7324 | DailyMed | swelling of your face, lips, tongue or throat problems breathing or swallowing fainting or feeling d... |
| 3 | `ce9c0d4f-889d-513c-8a49-a3518c070672` | 0.6843 | DailyMed | The following adverse reactions have been identified during post-approval use of atorvastatin calciu... |
| 4 | `83a18c07-1235-5f7e-8284-00fa6e5041e1` | 0.6763 | DailyMed | What should I avoid while taking atorvastatin calcium tablets? Avoid drinking more than 1.2 liters o... |
| 5 | `c4355dc4-5d9d-5c4e-bcc1-b1e5ccaf226a` | 0.6609 | DailyMed | 7 DRUG INTERACTIONS See full prescribing information for details regarding concomitant use of atorva... |

### Query: "Lisinopril warnings" (Status: ✅ PASS)
*   **Latency:** 399ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `397808b6-d08b-5a09-beed-b0b20396b666` | 0.6187 | DailyMed | The following adverse reactions have been identified during post-approval use of lisinopril that are... |
| 2 | `c2dece87-18d7-587d-a672-960e7034bca6` | 0.6187 | DailyMed | The following adverse reactions have been identified during post-approval use of lisinopril that are... |
| 3 | `1d8c6d0b-dee1-5c3e-ad68-9c820d91195b` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 4 | `e1a90c4b-4ac7-58c5-8712-4ae93848789d` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 5 | `c5bf03aa-13af-5036-85d4-06445c3bdef2` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |

### Query: "Warfarin interactions" (Status: ✅ PASS)
*   **Latency:** 288ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `49c2d111-efde-5d90-98ea-516c50a98ee2` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 2 | `a5e678f7-680a-5065-846d-236ab7764d80` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 3 | `300ada36-55bd-5d74-b8e4-10f06a16a58b` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 4 | `80db9b16-c614-504d-be9b-f9340af29779` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 5 | `9e505528-3560-56aa-b500-e5ad54f2f3e9` | 0.6225 | DailyMed | Closely monitor INR when starting or stopping any antibiotic or antifungal in patients taking warfar... |

### Query: "Amoxicillin dosage" (Status: ✅ PASS)
*   **Latency:** 357ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `e921e8ed-f8b4-51ab-9f74-e3c352190e34` | 0.7531 | DailyMed | 2 DOSAGE AND ADMINISTRATION Adults and Pediatric Patients greater than 40 kg: 500 or 875 mg every 12... |
| 2 | `b0b01afc-9dd5-5e1e-9755-ed89a1872330` | 0.7531 | DailyMed | 2 DOSAGE AND ADMINISTRATION Adults and Pediatric Patients greater than 40 kg: 500 or 875 mg every 12... |
| 3 | `7059b115-b2ed-5692-a363-9bccf450a752` | 0.6792 | DailyMed | Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patie... |
| 4 | `50a2d831-c436-59db-a750-c922fcc4b5ec` | 0.6692 | DailyMed | 3 DOSAGE FORMS AND STRENGTHS Amoxicillin and Clavulanate Potassium Tabl ets, USP : 250 mg/125 mg Tab... |
| 5 | `153cb318-8e97-5c61-b47f-a2ccc3800dab` | 0.6673 | DailyMed | Peak concentrations occurred approximately 1 hour after the dose. b Amoxicillin and clavulanate pota... |

### Query: "Ibuprofen pregnancy" (Status: ✅ PASS)
*   **Latency:** 307ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `c739d011-20ae-5fc1-818d-d47e34eeeeac` | 0.6998 | DailyMed | Avoid use of NSAIDs in women at about 30 weeks gestation and later in pregnancy, because NSAIDs, inc... |
| 2 | `98da2297-a02a-5843-b772-ea738b5217f5` | 0.6998 | DailyMed | Avoid use of NSAIDs in women at about 30 weeks gestation and later in pregnancy, because NSAIDs, inc... |
| 3 | `34dfedb3-ba55-559d-8c6f-18bd52b4a74e` | 0.6781 | DailyMed | Risk Summary Use of NSAIDs, including ibuprofen tablets, can cause premature closure of the fetal du... |
| 4 | `e2653697-56b1-5ec0-8c34-ad83f51cc548` | 0.6781 | DailyMed | Risk Summary Use of NSAIDs, including ibuprofen tablets, can cause premature closure of the fetal du... |
| 5 | `8ed6f3f7-d622-59cc-b031-aa3483fbcdd2` | 0.6758 | DailyMed | Premature Closure of Fetal Ductus Arteriosus:  Avoid use of NSAIDs, including ibuprofen tablets, in ... |

### Query: "Losartan contraindications" (Status: ✅ PASS)
*   **Latency:** 297ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `ee053d81-d2b6-53a4-8ade-b6dd27ed1e61` | 0.7291 | DailyMed | Losartan potassium tablets are contraindicated:  • In patients who are hypersensitive to any compone... |
| 2 | `2a97b3d5-1781-5733-b690-aad888d30200` | 0.7291 | DailyMed | Losartan potassium tablets are contraindicated: • In patients who are hypersensitive to any componen... |
| 3 | `aa474f48-ddd7-55da-9338-9333d7d1b164` | 0.6674 | DailyMed | The adverse events, regardless of drug relationship, reported with an incidence of ≥4% of patients t... |
| 4 | `d4b97750-cba0-55ad-8da4-a3ddcfb71afa` | 0.6674 | DailyMed | The adverse events, regardless of drug relationship, reported with an incidence of ≥4% of patients t... |
| 5 | `10b8b874-9cfe-57a7-8d5c-60bf3b72080e` | 0.6281 | DailyMed | The following additional adverse reactions have been reported in postmarketing experience  with losa... |

