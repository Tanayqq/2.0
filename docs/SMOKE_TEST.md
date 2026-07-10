# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-10T05:56:04.113386Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Chunks Retrieved | Top Score | Latency (ms) | Status |
|---|---|---|---|---|
| `Contraindications of Metformin` | 5 | 0.6970 | 1036ms | ✅ PASS |
| `Side effects of Atorvastatin` | 5 | 0.7378 | 348ms | ✅ PASS |
| `Lisinopril warnings` | 5 | 0.6187 | 329ms | ✅ PASS |
| `Warfarin interactions` | 5 | 0.6576 | 389ms | ✅ PASS |
| `Amoxicillin dosage` | 5 | 0.7531 | 332ms | ✅ PASS |
| `Ibuprofen pregnancy` | 5 | 0.7433 | 355ms | ✅ PASS |
| `Losartan contraindications` | 5 | 0.6281 | 321ms | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Metformin" (Status: ✅ PASS)
*   **Latency:** 1036ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `9feb4ef3-74aa-5294-9f4f-952c8dcc209c` | 0.6970 | DailyMed | The following adverse reactions have been identified during post approval use of metformin. Because ... |
| 2 | `848cb18d-a394-5257-a486-cf21c191b4be` | 0.6816 | DailyMed | Metformin is negligibly bound to plasma proteins. Metformin partitions into erythrocytes, most likel... |
| 3 | `31c7ef6a-e9d5-5b86-b0dc-e1f47119b227` | 0.6614 | DailyMed | Metformin is an antihyperglycemic agent which improves glucose tolerance in patients with type 2 dia... |
| 4 | `37dab858-d4d0-50f6-99e9-60eca436ebd2` | 0.6608 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with:  Severe ... |
| 5 | `5c212456-35fa-5e65-97a6-0525cc1237ca` | 0.6508 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |

### Query: "Side effects of Atorvastatin" (Status: ✅ PASS)
*   **Latency:** 348ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `fec0c075-46dd-524c-8408-61f21aa08194` | 0.7378 | DailyMed | feel tired or weak nausea or vomiting loss of appetite upper belly pain dark amber colored urine yel... |
| 2 | `40faa80c-c026-5068-b798-5fff105fb39b` | 0.7143 | DailyMed | fainting or feeling dizzy very rapid heartbeat severe skin rash or itching flu-like symptoms includi... |
| 3 | `7f7d159d-df3c-5b85-a76e-f742ad67039d` | 0.6843 | DailyMed | The following adverse reactions have been identified during post-approval use of atorvastatin calciu... |
| 4 | `c4355dc4-5d9d-5c4e-bcc1-b1e5ccaf226a` | 0.6609 | DailyMed | 7 DRUG INTERACTIONS See full prescribing information for details regarding concomitant use of atorva... |
| 5 | `5cc2af27-4d86-5770-8f2c-a69088c1d8aa` | 0.6499 | DailyMed | Increases in serum transaminases have been reported with use of atorvastatin calcium tablets  [see A... |

### Query: "Lisinopril warnings" (Status: ✅ PASS)
*   **Latency:** 329ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `7fddd95b-f393-5f01-954f-9ead62d39c7d` | 0.6187 | DailyMed | The following adverse reactions have been identified during post-approval use of lisinopril that are... |
| 2 | `e1a90c4b-4ac7-58c5-8712-4ae93848789d` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 3 | `c5bf03aa-13af-5036-85d4-06445c3bdef2` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 4 | `4f67f6ac-0a43-56cb-bda7-38b7e4098fd0` | 0.6046 | openFDA | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 5 | `1c847ee4-c052-56af-81e4-3720053572ee` | 0.5875 | DailyMed | ADVERSE REACTIONS Lisinopril and hydrochlorothiazide tablets have been evaluated for safety in 930 p... |

### Query: "Warfarin interactions" (Status: ✅ PASS)
*   **Latency:** 389ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `70f12c0b-68d3-561a-be96-a5bd1ae10a77` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 2 | `80db9b16-c614-504d-be9b-f9340af29779` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 3 | `fd427ffa-7c66-5652-a741-4780bdf6f03b` | 0.6238 | DailyMed | Warfarin sodium is a racemic mixture of the R- and S-enantiomers of warfarin. The S-enantiomer exhib... |
| 4 | `729bf450-8bd1-5283-a548-eb9fef338506` | 0.6035 | DailyMed | 12 CLINICAL PHARMACOLOGY 12.1 Mechanism of Action Warfarin acts by inhibiting the synthesis of vitam... |
| 5 | `6d235218-16fe-5361-b695-04c4ada8486f` | 0.6011 | DailyMed | Fluoroquinolones, including moxifloxacin hydrochloride, have been reported to enhance the anticoagul... |

### Query: "Amoxicillin dosage" (Status: ✅ PASS)
*   **Latency:** 332ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `e921e8ed-f8b4-51ab-9f74-e3c352190e34` | 0.7531 | DailyMed | 2 DOSAGE AND ADMINISTRATION Adults and Pediatric Patients greater than 40 kg: 500 or 875 mg every 12... |
| 2 | `e1757bd5-3c69-5a91-aad6-f22f45272fc2` | 0.6792 | DailyMed | Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patie... |
| 3 | `153cb318-8e97-5c61-b47f-a2ccc3800dab` | 0.6726 | DailyMed | The areas under the serum concentration curves obtained during the first 4 hours after dosing were 1... |
| 4 | `633c542a-f828-5e59-835a-17575e84832f` | 0.6726 | DailyMed | The areas under the serum concentration curves obtained during the first 4 hours after dosing were 1... |
| 5 | `dd5693e2-0e6b-582f-82b0-1b2b28847aab` | 0.6692 | DailyMed | 3 DOSAGE FORMS AND STRENGTHS Amoxicillin and Clavulanate Potassium Tabl ets, USP : 250 mg/125 mg Tab... |

### Query: "Ibuprofen pregnancy" (Status: ✅ PASS)
*   **Latency:** 355ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `c739d011-20ae-5fc1-818d-d47e34eeeeac` | 0.7433 | DailyMed | (see WARNINGS; Fetal Toxicity) . Data Human Data There are no adequate, well-controlled studies in p... |
| 2 | `e2653697-56b1-5ec0-8c34-ad83f51cc548` | 0.6781 | DailyMed | Risk Summary Use of NSAIDs, including ibuprofen tablets, can cause premature closure of the fetal du... |
| 3 | `8ed6f3f7-d622-59cc-b031-aa3483fbcdd2` | 0.6758 | DailyMed | Premature Closure of Fetal Ductus Arteriosus:  Avoid use of NSAIDs, including ibuprofen tablets, in ... |
| 4 | `1cd0a16a-9251-54db-b069-9de4222e1b57` | 0.6530 | DailyMed | In rat studies with NSAIDs, as with other drugs known to inhibit prostaglandin synthesis, an increas... |
| 5 | `cd411217-3441-590c-b1f3-e7c5a8737174` | 0.6303 | DailyMed | Patients should be informed of the signs of an anaphylactoid reaction (e.g. difficulty breathing, sw... |

### Query: "Losartan contraindications" (Status: ✅ PASS)
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `5542a89b-9116-501a-92b8-d0e675057c95` | 0.6281 | DailyMed | The following additional adverse reactions have been reported in postmarketing experience  with losa... |
| 2 | `5b8d3074-89e3-5558-aee3-3b99aac5a092` | 0.6115 | DailyMed | 12.2 Pharmacodynamics Losartan inhibits the pressor effect of angiotensin II (as well as angiotensin... |
| 3 | `d4b97750-cba0-55ad-8da4-a3ddcfb71afa` | 0.6015 | DailyMed | General Disorders and Administration Site Conditions: Malaise. Hematologic: Thrombocytopenia. Hypers... |
| 4 | `96a9b517-72e9-5d68-8ae7-f9e5295bccc7` | 0.5963 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |
| 5 | `1dfebef4-b2e7-528b-98c1-bba3a4aac426` | 0.5856 | DailyMed | Losartan inhibits the pressor effect of angiotensin II (as well as angiotensin I) infusions. A dose ... |

