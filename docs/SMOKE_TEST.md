# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-14T16:58:21.717410Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Chunks Retrieved | Top Score | Latency (ms) | Status |
|---|---|---|---|---|
| `Contraindications of Metformin` | 5 | 0.6970 | 1044ms | ✅ PASS |
| `Side effects of Atorvastatin` | 5 | 0.7719 | 307ms | ✅ PASS |
| `Lisinopril warnings` | 5 | 0.6187 | 382ms | ✅ PASS |
| `Warfarin interactions` | 5 | 0.6576 | 321ms | ✅ PASS |
| `Amoxicillin dosage` | 5 | 0.7531 | 320ms | ✅ PASS |
| `Ibuprofen pregnancy` | 5 | 0.6998 | 320ms | ✅ PASS |
| `Losartan contraindications` | 5 | 0.7291 | 316ms | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Metformin" (Status: ✅ PASS)
*   **Latency:** 1044ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `848f8feb-ae5a-56be-8221-1b5b32015bcd` | 0.6970 | DailyMed | The following adverse reactions have been identified during post approval use of metformin. Because ... |
| 2 | `37dab858-d4d0-50f6-99e9-60eca436ebd2` | 0.6608 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with:  Severe ... |
| 3 | `1b0103f7-6ff5-5847-ac13-5b7472afcb5b` | 0.6605 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with: Severe R... |
| 4 | `aeb9cec5-44dd-55c5-af63-1369d103d571` | 0.6508 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |
| 5 | `9945c80b-5242-57eb-805c-02506fe2d69d` | 0.6508 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |

### Query: "Side effects of Atorvastatin" (Status: ✅ PASS)
*   **Latency:** 307ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `3a05f30e-2f5c-5f3b-9656-02303f305c22` | 0.7719 | DailyMed | Increase in blood sugar level.Your blood sugar level may increase while you are taking atorvastatin ... |
| 2 | `e196584f-82ac-5d01-a36e-b18b156f81c4` | 0.7324 | DailyMed | swelling of your face, lips, tongue or throat problems breathing or swallowing fainting or feeling d... |
| 3 | `ce9c0d4f-889d-513c-8a49-a3518c070672` | 0.6843 | DailyMed | The following adverse reactions have been identified during post-approval use of atorvastatin calciu... |
| 4 | `83a18c07-1235-5f7e-8284-00fa6e5041e1` | 0.6763 | DailyMed | What should I avoid while taking atorvastatin calcium tablets? Avoid drinking more than 1.2 liters o... |
| 5 | `c4355dc4-5d9d-5c4e-bcc1-b1e5ccaf226a` | 0.6609 | DailyMed | 7 DRUG INTERACTIONS See full prescribing information for details regarding concomitant use of atorva... |

### Query: "Lisinopril warnings" (Status: ✅ PASS)
*   **Latency:** 382ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `397808b6-d08b-5a09-beed-b0b20396b666` | 0.6187 | DailyMed | The following adverse reactions have been identified during post-approval use of lisinopril that are... |
| 2 | `c5bf03aa-13af-5036-85d4-06445c3bdef2` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 3 | `e1a90c4b-4ac7-58c5-8712-4ae93848789d` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 4 | `1c847ee4-c052-56af-81e4-3720053572ee` | 0.5875 | DailyMed | ADVERSE REACTIONS Lisinopril and hydrochlorothiazide tablets have been evaluated for safety in 930 p... |
| 5 | `6ec6dbde-fdab-5aca-8970-ff018853e731` | 0.5875 | DailyMed | ADVERSE REACTIONS Lisinopril and hydrochlorothiazide tablets have been evaluated for safety in 930 p... |

### Query: "Warfarin interactions" (Status: ✅ PASS)
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `49c2d111-efde-5d90-98ea-516c50a98ee2` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 2 | `a5e678f7-680a-5065-846d-236ab7764d80` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 3 | `300ada36-55bd-5d74-b8e4-10f06a16a58b` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 4 | `80db9b16-c614-504d-be9b-f9340af29779` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 5 | `9e505528-3560-56aa-b500-e5ad54f2f3e9` | 0.6225 | DailyMed | Closely monitor INR when starting or stopping any antibiotic or antifungal in patients taking warfar... |

### Query: "Amoxicillin dosage" (Status: ✅ PASS)
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `e921e8ed-f8b4-51ab-9f74-e3c352190e34` | 0.7531 | DailyMed | 2 DOSAGE AND ADMINISTRATION Adults and Pediatric Patients greater than 40 kg: 500 or 875 mg every 12... |
| 2 | `7059b115-b2ed-5692-a363-9bccf450a752` | 0.6792 | DailyMed | Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patie... |
| 3 | `633c542a-f828-5e59-835a-17575e84832f` | 0.6673 | DailyMed | Peak concentrations occurred approximately 1 hour after the dose. b Amoxicillin and clavulanate pota... |
| 4 | `153cb318-8e97-5c61-b47f-a2ccc3800dab` | 0.6673 | DailyMed | Peak concentrations occurred approximately 1 hour after the dose. b Amoxicillin and clavulanate pota... |
| 5 | `4b59d699-ca0c-5076-930f-d2f5025ecbdc` | 0.6651 | DailyMed | b Adults who have difficulty swallowing may be given the Amoxicillin and Clavulanate Potassium 125 m... |

### Query: "Ibuprofen pregnancy" (Status: ✅ PASS)
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `c739d011-20ae-5fc1-818d-d47e34eeeeac` | 0.6998 | DailyMed | Avoid use of NSAIDs in women at about 30 weeks gestation and later in pregnancy, because NSAIDs, inc... |
| 2 | `e2653697-56b1-5ec0-8c34-ad83f51cc548` | 0.6781 | DailyMed | Risk Summary Use of NSAIDs, including ibuprofen tablets, can cause premature closure of the fetal du... |
| 3 | `8ed6f3f7-d622-59cc-b031-aa3483fbcdd2` | 0.6758 | DailyMed | Premature Closure of Fetal Ductus Arteriosus:  Avoid use of NSAIDs, including ibuprofen tablets, in ... |
| 4 | `1cd0a16a-9251-54db-b069-9de4222e1b57` | 0.6530 | DailyMed | In rat studies with NSAIDs, as with other drugs known to inhibit prostaglandin synthesis, an increas... |
| 5 | `cd411217-3441-590c-b1f3-e7c5a8737174` | 0.6303 | DailyMed | Patients should be informed of the signs of an anaphylactoid reaction (e.g. difficulty breathing, sw... |

### Query: "Losartan contraindications" (Status: ✅ PASS)
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `ee053d81-d2b6-53a4-8ade-b6dd27ed1e61` | 0.7291 | DailyMed | Losartan potassium tablets are contraindicated:  • In patients who are hypersensitive to any compone... |
| 2 | `d4b97750-cba0-55ad-8da4-a3ddcfb71afa` | 0.6674 | DailyMed | The adverse events, regardless of drug relationship, reported with an incidence of ≥4% of patients t... |
| 3 | `10b8b874-9cfe-57a7-8d5c-60bf3b72080e` | 0.6281 | DailyMed | The following additional adverse reactions have been reported in postmarketing experience  with losa... |
| 4 | `5b8d3074-89e3-5558-aee3-3b99aac5a092` | 0.6115 | DailyMed | 12.2 Pharmacodynamics Losartan inhibits the pressor effect of angiotensin II (as well as angiotensin... |
| 5 | `713ba153-af6a-50c5-98a1-1357b41992be` | 0.5963 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |

