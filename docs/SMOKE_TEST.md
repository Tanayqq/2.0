# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-16T16:18:02.105905Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Test Type | Latency (ms) | Status |
|---|---|---|---|
**Total Tests:** 208 | **Passed:** 183 | **Failed:** 25

| `Contraindications of Glimepiride` | per_drug_section | 974ms | ✅ PASS |
| `Dosage and administration of Glimepiride` | per_drug_section | 2053ms | ✅ PASS |
| `Drug interactions with Glimepiride` | per_drug_section | 316ms | ✅ PASS |
| `Pregnancy safety of Glimepiride` | per_drug_section | 325ms | ✅ PASS |
| `Renal dose adjustment for Glimepiride` | per_drug_section | 319ms | ✅ PASS |
| `Pediatric use of Glimepiride` | per_drug_section | 314ms | ✅ PASS |
| `Mechanism of action of Glimepiride` | per_drug_section | 1107ms | ✅ PASS |
| `Indications for Glimepiride` | per_drug_section | 332ms | ✅ PASS |
| `Storage conditions for Glimepiride` | per_drug_section | 320ms | ✅ PASS |
| `Patient counseling for Glimepiride` | per_drug_section | 643ms | ✅ PASS |
| `Contraindications of Glipizide` | per_drug_section | 315ms | ✅ PASS |
| `Dosage and administration of Glipizide` | per_drug_section | 326ms | ✅ PASS |
| `Drug interactions with Glipizide` | per_drug_section | 558ms | ✅ PASS |
| `Pregnancy safety of Glipizide` | per_drug_section | 315ms | ✅ PASS |
| `Renal dose adjustment for Glipizide` | per_drug_section | 400ms | ✅ PASS |
| `Pediatric use of Glipizide` | per_drug_section | 1074ms | ✅ PASS |
| `Mechanism of action of Glipizide` | per_drug_section | 530ms | ✅ PASS |
| `Indications for Glipizide` | per_drug_section | 316ms | ✅ PASS |
| `Storage conditions for Glipizide` | per_drug_section | 276ms | ✅ PASS |
| `Patient counseling for Glipizide` | per_drug_section | 366ms | ✅ PASS |
| `Contraindications of Gliclazide` | per_drug_section | 276ms | ❌ FAIL |
| `Dosage and administration of Gliclazide` | per_drug_section | 362ms | ❌ FAIL |
| `Drug interactions with Gliclazide` | per_drug_section | 327ms | ❌ FAIL |
| `Pregnancy safety of Gliclazide` | per_drug_section | 300ms | ❌ FAIL |
| `Renal dose adjustment for Gliclazide` | per_drug_section | 334ms | ❌ FAIL |
| `Pediatric use of Gliclazide` | per_drug_section | 318ms | ❌ FAIL |
| `Mechanism of action of Gliclazide` | per_drug_section | 1899ms | ❌ FAIL |
| `Indications for Gliclazide` | per_drug_section | 747ms | ❌ FAIL |
| `Storage conditions for Gliclazide` | per_drug_section | 636ms | ❌ FAIL |
| `Patient counseling for Gliclazide` | per_drug_section | 641ms | ❌ FAIL |
| `Contraindications of Pioglitazone` | per_drug_section | 325ms | ✅ PASS |
| `Dosage and administration of Pioglitazone` | per_drug_section | 279ms | ✅ PASS |
| `Drug interactions with Pioglitazone` | per_drug_section | 294ms | ✅ PASS |
| `Pregnancy safety of Pioglitazone` | per_drug_section | 376ms | ✅ PASS |
| `Renal dose adjustment for Pioglitazone` | per_drug_section | 322ms | ✅ PASS |
| `Pediatric use of Pioglitazone` | per_drug_section | 318ms | ✅ PASS |
| `Mechanism of action of Pioglitazone` | per_drug_section | 297ms | ✅ PASS |
| `Indications for Pioglitazone` | per_drug_section | 342ms | ✅ PASS |
| `Storage conditions for Pioglitazone` | per_drug_section | 303ms | ✅ PASS |
| `Patient counseling for Pioglitazone` | per_drug_section | 655ms | ✅ PASS |
| `Contraindications of Acarbose` | per_drug_section | 326ms | ✅ PASS |
| `Dosage and administration of Acarbose` | per_drug_section | 312ms | ✅ PASS |
| `Drug interactions with Acarbose` | per_drug_section | 321ms | ✅ PASS |
| `Pregnancy safety of Acarbose` | per_drug_section | 320ms | ✅ PASS |
| `Renal dose adjustment for Acarbose` | per_drug_section | 319ms | ✅ PASS |
| `Pediatric use of Acarbose` | per_drug_section | 328ms | ✅ PASS |
| `Mechanism of action of Acarbose` | per_drug_section | 631ms | ✅ PASS |
| `Indications for Acarbose` | per_drug_section | 326ms | ✅ PASS |
| `Storage conditions for Acarbose` | per_drug_section | 293ms | ✅ PASS |
| `Patient counseling for Acarbose` | per_drug_section | 312ms | ✅ PASS |
| `Contraindications of Sitagliptin` | per_drug_section | 348ms | ✅ PASS |
| `Dosage and administration of Sitagliptin` | per_drug_section | 278ms | ✅ PASS |
| `Drug interactions with Sitagliptin` | per_drug_section | 299ms | ✅ PASS |
| `Pregnancy safety of Sitagliptin` | per_drug_section | 300ms | ✅ PASS |
| `Renal dose adjustment for Sitagliptin` | per_drug_section | 398ms | ✅ PASS |
| `Pediatric use of Sitagliptin` | per_drug_section | 330ms | ✅ PASS |
| `Mechanism of action of Sitagliptin` | per_drug_section | 313ms | ✅ PASS |
| `Indications for Sitagliptin` | per_drug_section | 317ms | ✅ PASS |
| `Storage conditions for Sitagliptin` | per_drug_section | 1442ms | ✅ PASS |
| `Patient counseling for Sitagliptin` | per_drug_section | 325ms | ✅ PASS |
| `Contraindications of Vildagliptin` | per_drug_section | 317ms | ❌ FAIL |
| `Dosage and administration of Vildagliptin` | per_drug_section | 354ms | ❌ FAIL |
| `Drug interactions with Vildagliptin` | per_drug_section | 442ms | ❌ FAIL |
| `Pregnancy safety of Vildagliptin` | per_drug_section | 323ms | ❌ FAIL |
| `Renal dose adjustment for Vildagliptin` | per_drug_section | 314ms | ❌ FAIL |
| `Pediatric use of Vildagliptin` | per_drug_section | 319ms | ❌ FAIL |
| `Mechanism of action of Vildagliptin` | per_drug_section | 320ms | ❌ FAIL |
| `Indications for Vildagliptin` | per_drug_section | 326ms | ❌ FAIL |
| `Storage conditions for Vildagliptin` | per_drug_section | 1214ms | ❌ FAIL |
| `Patient counseling for Vildagliptin` | per_drug_section | 385ms | ❌ FAIL |
| `Contraindications of Linagliptin` | per_drug_section | 321ms | ✅ PASS |
| `Dosage and administration of Linagliptin` | per_drug_section | 313ms | ✅ PASS |
| `Drug interactions with Linagliptin` | per_drug_section | 318ms | ✅ PASS |
| `Pregnancy safety of Linagliptin` | per_drug_section | 320ms | ❌ FAIL |
| `Renal dose adjustment for Linagliptin` | per_drug_section | 320ms | ❌ FAIL |
| `Pediatric use of Linagliptin` | per_drug_section | 325ms | ✅ PASS |
| `Mechanism of action of Linagliptin` | per_drug_section | 313ms | ✅ PASS |
| `Indications for Linagliptin` | per_drug_section | 320ms | ✅ PASS |
| `Storage conditions for Linagliptin` | per_drug_section | 323ms | ✅ PASS |
| `Patient counseling for Linagliptin` | per_drug_section | 281ms | ✅ PASS |
| `Contraindications of Empagliflozin` | per_drug_section | 289ms | ✅ PASS |
| `Dosage and administration of Empagliflozin` | per_drug_section | 385ms | ✅ PASS |
| `Drug interactions with Empagliflozin` | per_drug_section | 319ms | ✅ PASS |
| `Pregnancy safety of Empagliflozin` | per_drug_section | 320ms | ✅ PASS |
| `Renal dose adjustment for Empagliflozin` | per_drug_section | 319ms | ✅ PASS |
| `Pediatric use of Empagliflozin` | per_drug_section | 321ms | ✅ PASS |
| `Mechanism of action of Empagliflozin` | per_drug_section | 323ms | ✅ PASS |
| `Indications for Empagliflozin` | per_drug_section | 315ms | ✅ PASS |
| `Storage conditions for Empagliflozin` | per_drug_section | 320ms | ✅ PASS |
| `Patient counseling for Empagliflozin` | per_drug_section | 321ms | ✅ PASS |
| `Contraindications of Dapagliflozin` | per_drug_section | 322ms | ✅ PASS |
| `Dosage and administration of Dapagliflozin` | per_drug_section | 315ms | ✅ PASS |
| `Drug interactions with Dapagliflozin` | per_drug_section | 301ms | ✅ PASS |
| `Pregnancy safety of Dapagliflozin` | per_drug_section | 291ms | ✅ PASS |
| `Renal dose adjustment for Dapagliflozin` | per_drug_section | 291ms | ✅ PASS |
| `Pediatric use of Dapagliflozin` | per_drug_section | 398ms | ✅ PASS |
| `Mechanism of action of Dapagliflozin` | per_drug_section | 801ms | ✅ PASS |
| `Indications for Dapagliflozin` | per_drug_section | 324ms | ✅ PASS |
| `Storage conditions for Dapagliflozin` | per_drug_section | 309ms | ✅ PASS |
| `Patient counseling for Dapagliflozin` | per_drug_section | 323ms | ✅ PASS |
| `Contraindications of Canagliflozin` | per_drug_section | 321ms | ✅ PASS |
| `Dosage and administration of Canagliflozin` | per_drug_section | 327ms | ✅ PASS |
| `Drug interactions with Canagliflozin` | per_drug_section | 311ms | ✅ PASS |
| `Pregnancy safety of Canagliflozin` | per_drug_section | 320ms | ❌ FAIL |
| `Renal dose adjustment for Canagliflozin` | per_drug_section | 319ms | ✅ PASS |
| `Pediatric use of Canagliflozin` | per_drug_section | 326ms | ✅ PASS |
| `Mechanism of action of Canagliflozin` | per_drug_section | 315ms | ✅ PASS |
| `Indications for Canagliflozin` | per_drug_section | 316ms | ✅ PASS |
| `Storage conditions for Canagliflozin` | per_drug_section | 329ms | ✅ PASS |
| `Patient counseling for Canagliflozin` | per_drug_section | 319ms | ✅ PASS |
| `Contraindications of Semaglutide` | per_drug_section | 315ms | ✅ PASS |
| `Dosage and administration of Semaglutide` | per_drug_section | 318ms | ✅ PASS |
| `Drug interactions with Semaglutide` | per_drug_section | 1759ms | ✅ PASS |
| `Pregnancy safety of Semaglutide` | per_drug_section | 639ms | ✅ PASS |
| `Renal dose adjustment for Semaglutide` | per_drug_section | 641ms | ✅ PASS |
| `Pediatric use of Semaglutide` | per_drug_section | 636ms | ✅ PASS |
| `Mechanism of action of Semaglutide` | per_drug_section | 641ms | ✅ PASS |
| `Indications for Semaglutide` | per_drug_section | 321ms | ✅ PASS |
| `Storage conditions for Semaglutide` | per_drug_section | 324ms | ✅ PASS |
| `Patient counseling for Semaglutide` | per_drug_section | 282ms | ✅ PASS |
| `Contraindications of Liraglutide` | per_drug_section | 2111ms | ✅ PASS |
| `Dosage and administration of Liraglutide` | per_drug_section | 298ms | ✅ PASS |
| `Drug interactions with Liraglutide` | per_drug_section | 286ms | ✅ PASS |
| `Pregnancy safety of Liraglutide` | per_drug_section | 277ms | ✅ PASS |
| `Renal dose adjustment for Liraglutide` | per_drug_section | 368ms | ✅ PASS |
| `Pediatric use of Liraglutide` | per_drug_section | 369ms | ✅ PASS |
| `Mechanism of action of Liraglutide` | per_drug_section | 292ms | ✅ PASS |
| `Indications for Liraglutide` | per_drug_section | 285ms | ✅ PASS |
| `Storage conditions for Liraglutide` | per_drug_section | 379ms | ✅ PASS |
| `Patient counseling for Liraglutide` | per_drug_section | 330ms | ✅ PASS |
| `Contraindications of Exenatide` | per_drug_section | 309ms | ✅ PASS |
| `Dosage and administration of Exenatide` | per_drug_section | 325ms | ✅ PASS |
| `Drug interactions with Exenatide` | per_drug_section | 314ms | ✅ PASS |
| `Pregnancy safety of Exenatide` | per_drug_section | 320ms | ✅ PASS |
| `Renal dose adjustment for Exenatide` | per_drug_section | 296ms | ✅ PASS |
| `Pediatric use of Exenatide` | per_drug_section | 344ms | ✅ PASS |
| `Mechanism of action of Exenatide` | per_drug_section | 321ms | ✅ PASS |
| `Indications for Exenatide` | per_drug_section | 316ms | ✅ PASS |
| `Storage conditions for Exenatide` | per_drug_section | 321ms | ✅ PASS |
| `Patient counseling for Exenatide` | per_drug_section | 332ms | ✅ PASS |
| `Contraindications of Dulaglutide` | per_drug_section | 308ms | ✅ PASS |
| `Dosage and administration of Dulaglutide` | per_drug_section | 326ms | ✅ PASS |
| `Drug interactions with Dulaglutide` | per_drug_section | 958ms | ✅ PASS |
| `Pregnancy safety of Dulaglutide` | per_drug_section | 636ms | ❌ FAIL |
| `Renal dose adjustment for Dulaglutide` | per_drug_section | 318ms | ✅ PASS |
| `Pediatric use of Dulaglutide` | per_drug_section | 317ms | ✅ PASS |
| `Mechanism of action of Dulaglutide` | per_drug_section | 322ms | ✅ PASS |
| `Indications for Dulaglutide` | per_drug_section | 280ms | ✅ PASS |
| `Storage conditions for Dulaglutide` | per_drug_section | 299ms | ✅ PASS |
| `Patient counseling for Dulaglutide` | per_drug_section | 282ms | ✅ PASS |
| `Contraindications of Insulin glargine` | per_drug_section | 431ms | ✅ PASS |
| `Dosage and administration of Insulin glargine` | per_drug_section | 316ms | ✅ PASS |
| `Drug interactions with Insulin glargine` | per_drug_section | 307ms | ✅ PASS |
| `Pregnancy safety of Insulin glargine` | per_drug_section | 323ms | ✅ PASS |
| `Renal dose adjustment for Insulin glargine` | per_drug_section | 320ms | ✅ PASS |
| `Pediatric use of Insulin glargine` | per_drug_section | 322ms | ✅ PASS |
| `Mechanism of action of Insulin glargine` | per_drug_section | 325ms | ✅ PASS |
| `Indications for Insulin glargine` | per_drug_section | 312ms | ✅ PASS |
| `Storage conditions for Insulin glargine` | per_drug_section | 324ms | ✅ PASS |
| `Patient counseling for Insulin glargine` | per_drug_section | 319ms | ✅ PASS |
| `Contraindications of Insulin lispro` | per_drug_section | 314ms | ✅ PASS |
| `Dosage and administration of Insulin lispro` | per_drug_section | 321ms | ✅ PASS |
| `Drug interactions with Insulin lispro` | per_drug_section | 270ms | ✅ PASS |
| `Pregnancy safety of Insulin lispro` | per_drug_section | 285ms | ✅ PASS |
| `Renal dose adjustment for Insulin lispro` | per_drug_section | 301ms | ✅ PASS |
| `Pediatric use of Insulin lispro` | per_drug_section | 424ms | ✅ PASS |
| `Mechanism of action of Insulin lispro` | per_drug_section | 314ms | ✅ PASS |
| `Indications for Insulin lispro` | per_drug_section | 301ms | ✅ PASS |
| `Storage conditions for Insulin lispro` | per_drug_section | 332ms | ✅ PASS |
| `Patient counseling for Insulin lispro` | per_drug_section | 325ms | ✅ PASS |
| `Contraindications of Insulin aspart` | per_drug_section | 321ms | ✅ PASS |
| `Dosage and administration of Insulin aspart` | per_drug_section | 318ms | ✅ PASS |
| `Drug interactions with Insulin aspart` | per_drug_section | 320ms | ✅ PASS |
| `Pregnancy safety of Insulin aspart` | per_drug_section | 279ms | ✅ PASS |
| `Renal dose adjustment for Insulin aspart` | per_drug_section | 283ms | ✅ PASS |
| `Pediatric use of Insulin aspart` | per_drug_section | 395ms | ✅ PASS |
| `Mechanism of action of Insulin aspart` | per_drug_section | 321ms | ✅ PASS |
| `Indications for Insulin aspart` | per_drug_section | 325ms | ✅ PASS |
| `Storage conditions for Insulin aspart` | per_drug_section | 314ms | ✅ PASS |
| `Patient counseling for Insulin aspart` | per_drug_section | 322ms | ✅ PASS |
| `Contraindications of Insulin detemir` | per_drug_section | 317ms | ✅ PASS |
| `Dosage and administration of Insulin detemir` | per_drug_section | 321ms | ✅ PASS |
| `Drug interactions with Insulin detemir` | per_drug_section | 319ms | ✅ PASS |
| `Pregnancy safety of Insulin detemir` | per_drug_section | 323ms | ✅ PASS |
| `Renal dose adjustment for Insulin detemir` | per_drug_section | 316ms | ✅ PASS |
| `Pediatric use of Insulin detemir` | per_drug_section | 323ms | ✅ PASS |
| `Mechanism of action of Insulin detemir` | per_drug_section | 317ms | ✅ PASS |
| `Indications for Insulin detemir` | per_drug_section | 280ms | ✅ PASS |
| `Storage conditions for Insulin detemir` | per_drug_section | 368ms | ✅ PASS |
| `Patient counseling for Insulin detemir` | per_drug_section | 284ms | ✅ PASS |
| `Contraindications of Insulin degludec` | per_drug_section | 348ms | ✅ PASS |
| `Dosage and administration of Insulin degludec` | per_drug_section | 323ms | ✅ PASS |
| `Drug interactions with Insulin degludec` | per_drug_section | 315ms | ✅ PASS |
| `Pregnancy safety of Insulin degludec` | per_drug_section | 270ms | ✅ PASS |
| `Renal dose adjustment for Insulin degludec` | per_drug_section | 279ms | ✅ PASS |
| `Pediatric use of Insulin degludec` | per_drug_section | 1050ms | ✅ PASS |
| `Mechanism of action of Insulin degludec` | per_drug_section | 321ms | ✅ PASS |
| `Indications for Insulin degludec` | per_drug_section | 288ms | ✅ PASS |
| `Storage conditions for Insulin degludec` | per_drug_section | 350ms | ✅ PASS |
| `Patient counseling for Insulin degludec` | per_drug_section | 313ms | ✅ PASS |
| `Mechanism of action of Coca-Cola` | adversarial_impossible_query | N/A | ✅ PASS |
| `Contraindications of Superman` | adversarial_wrong_drug | N/A | ✅ PASS |
| `Novamox dosage` | adversarial_brand_resolution | N/A | ❌ FAIL |
| `Metoformin contraindications` | adversarial_typo_tolerance | N/A | ✅ PASS |
| `Metformin Warfarin Lisinopril indications` | adversarial_multi_drug_separation | N/A | ✅ PASS |
| `Metformin dosage` | adversarial_mixed_query | N/A | ✅ PASS |
| `Warfarin interactions` | adversarial_mixed_query | N/A | ✅ PASS |
| `Atorvastatin pregnancy` | adversarial_mixed_query | N/A | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 974ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 2053ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1107ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 332ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Glimepiride" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 643ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 558ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 400ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1074ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 530ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 276ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Glipizide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 366ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 276ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 362ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 327ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 300ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 334ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 1899ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 747ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 636ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Gliclazide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 641ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 279ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 294ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 376ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 297ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 342ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 303ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Pioglitazone" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 655ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 312ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 328ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 631ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 293ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Acarbose" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 312ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 348ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 278ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 299ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 300ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 398ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 330ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 313ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1442ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Sitagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 354ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 442ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 1214ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Vildagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 385ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 313ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Linagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Linagliptin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 313ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Linagliptin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 281ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 289ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 385ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Empagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 301ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 291ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 291ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 398ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 801ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 324ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 309ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Dapagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 327ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 311ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Canagliflozin" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 329ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Canagliflozin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1759ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 639ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 641ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 636ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 641ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 324ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Semaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 282ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 2111ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 298ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 286ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 277ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 368ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 369ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 292ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 285ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 379ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Liraglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 330ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 309ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 296ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 344ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Exenatide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 332ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 308ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 958ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Dulaglutide" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 636ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 280ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 299ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Dulaglutide" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 282ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 431ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 307ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 312ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 324ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Insulin glargine" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 270ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 285ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 301ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 424ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 301ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 332ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Insulin lispro" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 279ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 283ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 395ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Insulin aspart" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 280ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 368ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Insulin detemir" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 284ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 348ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 323ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 315ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 270ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 279ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1050ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 288ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 350ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Insulin degludec" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 313ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Coca-Cola" (Status: ✅ PASS)
*   **Test Type:** adversarial_impossible_query
*   **Expected:** No high-confidence match
*   **Top Score:** 0.3289

### Query: "Contraindications of Superman" (Status: ✅ PASS)
*   **Test Type:** adversarial_wrong_drug
*   **Expected:** No high-confidence match
*   **Top Score:** 0.4793

### Query: "Novamox dosage" (Status: ❌ FAIL)
*   **Test Type:** adversarial_brand_resolution
*   **Expected:** Amoxicillin content in results

### Query: "Metoformin contraindications" (Status: ✅ PASS)
*   **Test Type:** adversarial_typo_tolerance
*   **Expected:** Metformin content in results

### Query: "Metformin Warfarin Lisinopril indications" (Status: ✅ PASS)
*   **Test Type:** adversarial_multi_drug_separation
*   **Expected:** Multiple separate drug chunks returned

### Query: "Metformin dosage" (Status: ✅ PASS)
*   **Test Type:** adversarial_mixed_query

### Query: "Warfarin interactions" (Status: ✅ PASS)
*   **Test Type:** adversarial_mixed_query

### Query: "Atorvastatin pregnancy" (Status: ✅ PASS)
*   **Test Type:** adversarial_mixed_query

