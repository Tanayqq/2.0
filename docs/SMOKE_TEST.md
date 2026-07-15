# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-15T05:02:45.069091Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Chunks Retrieved | Top Score | Latency (ms) | Status |
|---|---|---|---|---|
| `Contraindications of Metformin` | 5 | 0.6966 | 1671ms | ✅ PASS |
| `Side effects of Atorvastatin` | 5 | 0.7719 | 371ms | ✅ PASS |
| `Lisinopril warnings` | 5 | 0.6187 | 424ms | ✅ PASS |
| `Warfarin interactions` | 5 | 0.6576 | 418ms | ✅ PASS |
| `Amoxicillin dosage` | 5 | 0.6850 | 601ms | ✅ PASS |
| `Ibuprofen pregnancy` | 5 | 0.6998 | 354ms | ✅ PASS |
| `Losartan contraindications` | 5 | 0.7291 | 344ms | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Metformin" (Status: ✅ PASS)
*   **Latency:** 1671ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `aeb9cec5-44dd-55c5-af63-1369d103d571` | 0.6966 | DailyMed | The following adverse reactions are also discussed elsewhere in the labeling: Lactic Acidosis [see B... |
| 2 | `1b0103f7-6ff5-5847-ac13-5b7472afcb5b` | 0.6605 | DailyMed | Metformin hydrochloride extended-release tablets, USP are contraindicated in patients with: Severe R... |
| 3 | `8a7bb77e-4d41-5b17-b1ab-31769216a566` | 0.6487 | DailyMed | In the event of an overdose with metformin hydrochloride extended-release tablets, consider contacti... |
| 4 | `414eb597-41c0-5f51-8b58-08a3a5c1463e` | 0.6461 | DailyMed | Metformin is an antihyperglycemic agent which improves glucose tolerance in patients with type 2 dia... |
| 5 | `7512ac5b-3d8c-5c96-8e4e-419e1fd69809` | 0.6410 | DailyMed | Absorption The absolute bioavailability of a Metformin Hydrochloride Tablets 500 mg given under fast... |

### Query: "Side effects of Atorvastatin" (Status: ✅ PASS)
*   **Latency:** 371ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `9aa75455-85f4-56c1-86a3-1b22e084209a` | 0.7719 | DailyMed | Increase in blood sugar level.Your blood sugar level may increase while you are taking atorvastatin ... |
| 2 | `324ba367-fe87-5cef-a02e-291bd8dbaf5e` | 0.6843 | DailyMed | The following adverse reactions have been identified during post-approval use of atorvastatin calciu... |
| 3 | `3a05f30e-2f5c-5f3b-9656-02303f305c22` | 0.6763 | DailyMed | What should I avoid while taking atorvastatin calcium tablets? Avoid drinking more than 1.2 liters o... |
| 4 | `a495c5ba-cfd4-57d6-9541-4c76db907888` | 0.6499 | DailyMed | Increases in serum transaminases have been reported with use of atorvastatin calcium tablets [see Ad... |
| 5 | `b727214e-991f-5ac1-aee8-c7c41736bd6e` | 0.6364 | DailyMed | Atorvastatin, as well as some of its metabolites, are pharmacologically active in humans. The liver ... |

### Query: "Lisinopril warnings" (Status: ✅ PASS)
*   **Latency:** 424ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `c2dece87-18d7-587d-a672-960e7034bca6` | 0.6187 | DailyMed | The following adverse reactions have been identified during post-approval use of lisinopril that are... |
| 2 | `c151365e-c53c-5bc5-9cfe-c652dd772a6a` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 3 | `1a0b961b-2588-5878-8eb6-74a4e2251998` | 0.6046 | DailyMed | Other adverse reactions that have been reported with the individual components are listed below: Lis... |
| 4 | `002a74f1-2cb5-5963-8e82-03c647f4d436` | 0.5875 | DailyMed | ADVERSE REACTIONS Lisinopril and hydrochlorothiazide tablets have been evaluated for safety in 930 p... |
| 5 | `31724e97-314b-5f71-b22a-34615402d176` | 0.5875 | DailyMed | ADVERSE REACTIONS Lisinopril and hydrochlorothiazide tablets have been evaluated for safety in 930 p... |

### Query: "Warfarin interactions" (Status: ✅ PASS)
*   **Latency:** 418ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `a5e678f7-680a-5065-846d-236ab7764d80` | 0.6576 | DailyMed | Drugs may interact with warfarin sodium through pharmacodynamic or pharmacokinetic mechanisms. Pharm... |
| 2 | `300ada36-55bd-5d74-b8e4-10f06a16a58b` | 0.6257 | DailyMed | 7 DRUG INTERACTIONS Concomitant use of drugs that increase bleeding risk, antibiotics, antifungals, ... |
| 3 | `0166e3f7-059a-513d-af3c-668187fca017` | 0.6238 | DailyMed | Warfarin sodium is a racemic mixture of the R- and S-enantiomers of warfarin. The S-enantiomer exhib... |
| 4 | `9e505528-3560-56aa-b500-e5ad54f2f3e9` | 0.6225 | DailyMed | Closely monitor INR when starting or stopping any antibiotic or antifungal in patients taking warfar... |
| 5 | `55b14f68-cbdd-5049-97f2-b31eded7579b` | 0.6194 | DailyMed | Warfarin No significant effect of moxifloxacin (400 mg once daily for eight days) on the pharmacokin... |

### Query: "Amoxicillin dosage" (Status: ✅ PASS)
*   **Latency:** 601ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `48e18c58-3d8a-5777-83e2-6f9850a6682a` | 0.6850 | DailyMed | 2.2 Adult Patients See dosing regimens of Amoxicillin and Clavulanate Potassium (based on the amoxic... |
| 2 | `da5a84e6-9749-500f-b954-44007bb9d1fd` | 0.6778 | DailyMed | Peak concentrations occurred approximately 1.5 hours after the dose. b Amoxicillin and clavulanate p... |
| 3 | `d9253b27-4890-54ab-9fea-d13614f9f158` | 0.6673 | DailyMed | Peak concentrations occurred approximately 1 hour after the dose. b Amoxicillin and clavulanate pota... |
| 4 | `50a2d831-c436-59db-a750-c922fcc4b5ec` | 0.6624 | DailyMed | Amoxicillin: Tablets: 500 mg, 875 mg. Each tablet contains 500 mg or 875 mg amoxicillin as the trihy... |
| 5 | `f19079ec-5512-5268-823c-385257b372c9` | 0.6580 | DailyMed | Distribution: Amoxicillin diffuses readily into most body tissues and fluids, with the exception of ... |

### Query: "Ibuprofen pregnancy" (Status: ✅ PASS)
*   **Latency:** 354ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `98da2297-a02a-5843-b772-ea738b5217f5` | 0.6998 | DailyMed | Avoid use of NSAIDs in women at about 30 weeks gestation and later in pregnancy, because NSAIDs, inc... |
| 2 | `34dfedb3-ba55-559d-8c6f-18bd52b4a74e` | 0.6781 | DailyMed | Risk Summary Use of NSAIDs, including ibuprofen tablets, can cause premature closure of the fetal du... |
| 3 | `117d3924-d47d-5f31-aaea-df653a39782b` | 0.6758 | DailyMed | Premature Closure of Fetal Ductus Arteriosus:  Avoid use of NSAIDs, including ibuprofen tablets, in ... |
| 4 | `856c1703-3d3d-54ad-ab04-4243c153a28c` | 0.6530 | DailyMed | In rat studies with NSAIDs, as with other drugs known to inhibit prostaglandin synthesis, an increas... |
| 5 | `7294a333-f58e-5f26-9254-6d0c778fa24f` | 0.6005 | DailyMed | Controlled studies have demonstrated that ibuprofen tablets are a more effective analgesic than prop... |

### Query: "Losartan contraindications" (Status: ✅ PASS)
*   **Latency:** 344ms
*   **Chunks Retrieved:** 5

| Rank | Chunk ID | Similarity Score | Source | Content Snippet |
|---|---|---|---|---|
| 1 | `2a97b3d5-1781-5733-b690-aad888d30200` | 0.7291 | DailyMed | Losartan potassium tablets are contraindicated: • In patients who are hypersensitive to any componen... |
| 2 | `da1eaaa2-fd00-5bb3-9c88-e6f5f6a95bd4` | 0.6674 | DailyMed | The adverse events, regardless of drug relationship, reported with an incidence of ≥4% of patients t... |
| 3 | `e0ae4c94-2903-5034-ac1b-636f080997ea` | 0.6266 | DailyMed | The 4 studies of losartan monotherapy included a total of 1075 patients randomized to several doses ... |
| 4 | `a6658dda-9c57-5e63-bd8c-8e76047143d3` | 0.6115 | DailyMed | 12.2 Pharmacodynamics Losartan inhibits the pressor effect of angiotensin II (as well as angiotensin... |
| 5 | `79df0317-0a89-5839-a11d-1dcf1dbaa830` | 0.5963 | DailyMed | Because clinical trials are conducted under widely varying conditions, adverse reaction rates observ... |

