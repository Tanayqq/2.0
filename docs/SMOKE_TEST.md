# MedRef Ingestion Smoke Test Results
Generated at: 2026-07-23T04:01:17.590451Z
Embedding Model: sentence-transformers/all-MiniLM-L6-v2

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Test Type | Latency (ms) | Status |
|---|---|---|---|
**Total Tests:** 208 | **Passed:** 138 | **Failed:** 70

| `Contraindications of Apixaban` | per_drug_section | 351ms | ❌ FAIL |
| `Dosage and administration of Apixaban` | per_drug_section | 406ms | ❌ FAIL |
| `Drug interactions with Apixaban` | per_drug_section | 319ms | ❌ FAIL |
| `Pregnancy safety of Apixaban` | per_drug_section | 330ms | ❌ FAIL |
| `Renal dose adjustment for Apixaban` | per_drug_section | 318ms | ❌ FAIL |
| `Pediatric use of Apixaban` | per_drug_section | 325ms | ❌ FAIL |
| `Mechanism of action of Apixaban` | per_drug_section | 2011ms | ❌ FAIL |
| `Indications for Apixaban` | per_drug_section | 352ms | ❌ FAIL |
| `Storage conditions for Apixaban` | per_drug_section | 1639ms | ❌ FAIL |
| `Patient counseling for Apixaban` | per_drug_section | 376ms | ❌ FAIL |
| `Contraindications of Rivaroxaban` | per_drug_section | 324ms | ❌ FAIL |
| `Dosage and administration of Rivaroxaban` | per_drug_section | 363ms | ❌ FAIL |
| `Drug interactions with Rivaroxaban` | per_drug_section | 435ms | ❌ FAIL |
| `Pregnancy safety of Rivaroxaban` | per_drug_section | 372ms | ❌ FAIL |
| `Renal dose adjustment for Rivaroxaban` | per_drug_section | 349ms | ❌ FAIL |
| `Pediatric use of Rivaroxaban` | per_drug_section | 340ms | ❌ FAIL |
| `Mechanism of action of Rivaroxaban` | per_drug_section | 290ms | ❌ FAIL |
| `Indications for Rivaroxaban` | per_drug_section | 314ms | ❌ FAIL |
| `Storage conditions for Rivaroxaban` | per_drug_section | 303ms | ❌ FAIL |
| `Patient counseling for Rivaroxaban` | per_drug_section | 300ms | ❌ FAIL |
| `Contraindications of Dabigatran` | per_drug_section | 293ms | ❌ FAIL |
| `Dosage and administration of Dabigatran` | per_drug_section | 307ms | ❌ FAIL |
| `Drug interactions with Dabigatran` | per_drug_section | 337ms | ❌ FAIL |
| `Pregnancy safety of Dabigatran` | per_drug_section | 393ms | ❌ FAIL |
| `Renal dose adjustment for Dabigatran` | per_drug_section | 322ms | ❌ FAIL |
| `Pediatric use of Dabigatran` | per_drug_section | 283ms | ❌ FAIL |
| `Mechanism of action of Dabigatran` | per_drug_section | 285ms | ❌ FAIL |
| `Indications for Dabigatran` | per_drug_section | 406ms | ❌ FAIL |
| `Storage conditions for Dabigatran` | per_drug_section | 318ms | ❌ FAIL |
| `Patient counseling for Dabigatran` | per_drug_section | 318ms | ❌ FAIL |
| `Contraindications of Edoxaban` | per_drug_section | 320ms | ❌ FAIL |
| `Dosage and administration of Edoxaban` | per_drug_section | 307ms | ❌ FAIL |
| `Drug interactions with Edoxaban` | per_drug_section | 317ms | ❌ FAIL |
| `Pregnancy safety of Edoxaban` | per_drug_section | 302ms | ❌ FAIL |
| `Renal dose adjustment for Edoxaban` | per_drug_section | 343ms | ❌ FAIL |
| `Pediatric use of Edoxaban` | per_drug_section | 339ms | ❌ FAIL |
| `Mechanism of action of Edoxaban` | per_drug_section | 321ms | ❌ FAIL |
| `Indications for Edoxaban` | per_drug_section | 305ms | ❌ FAIL |
| `Storage conditions for Edoxaban` | per_drug_section | 302ms | ❌ FAIL |
| `Patient counseling for Edoxaban` | per_drug_section | 327ms | ❌ FAIL |
| `Contraindications of Warfarin` | per_drug_section | 297ms | ✅ PASS |
| `Dosage and administration of Warfarin` | per_drug_section | 357ms | ✅ PASS |
| `Drug interactions with Warfarin` | per_drug_section | 305ms | ✅ PASS |
| `Pregnancy safety of Warfarin` | per_drug_section | 318ms | ✅ PASS |
| `Renal dose adjustment for Warfarin` | per_drug_section | 316ms | ✅ PASS |
| `Pediatric use of Warfarin` | per_drug_section | 291ms | ✅ PASS |
| `Mechanism of action of Warfarin` | per_drug_section | 310ms | ✅ PASS |
| `Indications for Warfarin` | per_drug_section | 290ms | ✅ PASS |
| `Storage conditions for Warfarin` | per_drug_section | 301ms | ✅ PASS |
| `Patient counseling for Warfarin` | per_drug_section | 327ms | ✅ PASS |
| `Contraindications of Clopidogrel` | per_drug_section | 321ms | ✅ PASS |
| `Dosage and administration of Clopidogrel` | per_drug_section | 326ms | ✅ PASS |
| `Drug interactions with Clopidogrel` | per_drug_section | 394ms | ✅ PASS |
| `Pregnancy safety of Clopidogrel` | per_drug_section | 314ms | ❌ FAIL |
| `Renal dose adjustment for Clopidogrel` | per_drug_section | 328ms | ✅ PASS |
| `Pediatric use of Clopidogrel` | per_drug_section | 376ms | ❌ FAIL |
| `Mechanism of action of Clopidogrel` | per_drug_section | 417ms | ✅ PASS |
| `Indications for Clopidogrel` | per_drug_section | 335ms | ✅ PASS |
| `Storage conditions for Clopidogrel` | per_drug_section | 359ms | ❌ FAIL |
| `Patient counseling for Clopidogrel` | per_drug_section | 428ms | ✅ PASS |
| `Contraindications of Ticagrelor` | per_drug_section | 357ms | ❌ FAIL |
| `Dosage and administration of Ticagrelor` | per_drug_section | 352ms | ✅ PASS |
| `Drug interactions with Ticagrelor` | per_drug_section | 567ms | ✅ PASS |
| `Pregnancy safety of Ticagrelor` | per_drug_section | 639ms | ❌ FAIL |
| `Renal dose adjustment for Ticagrelor` | per_drug_section | 496ms | ❌ FAIL |
| `Pediatric use of Ticagrelor` | per_drug_section | 513ms | ❌ FAIL |
| `Mechanism of action of Ticagrelor` | per_drug_section | 536ms | ❌ FAIL |
| `Indications for Ticagrelor` | per_drug_section | 554ms | ❌ FAIL |
| `Storage conditions for Ticagrelor` | per_drug_section | 425ms | ❌ FAIL |
| `Patient counseling for Ticagrelor` | per_drug_section | 574ms | ✅ PASS |
| `Contraindications of Prasugrel` | per_drug_section | 614ms | ❌ FAIL |
| `Dosage and administration of Prasugrel` | per_drug_section | 547ms | ❌ FAIL |
| `Drug interactions with Prasugrel` | per_drug_section | 559ms | ❌ FAIL |
| `Pregnancy safety of Prasugrel` | per_drug_section | 560ms | ❌ FAIL |
| `Renal dose adjustment for Prasugrel` | per_drug_section | 571ms | ❌ FAIL |
| `Pediatric use of Prasugrel` | per_drug_section | 640ms | ❌ FAIL |
| `Mechanism of action of Prasugrel` | per_drug_section | 477ms | ❌ FAIL |
| `Indications for Prasugrel` | per_drug_section | 603ms | ❌ FAIL |
| `Storage conditions for Prasugrel` | per_drug_section | 552ms | ❌ FAIL |
| `Patient counseling for Prasugrel` | per_drug_section | 567ms | ❌ FAIL |
| `Contraindications of Atorvastatin` | per_drug_section | 586ms | ✅ PASS |
| `Dosage and administration of Atorvastatin` | per_drug_section | 569ms | ✅ PASS |
| `Drug interactions with Atorvastatin` | per_drug_section | 539ms | ✅ PASS |
| `Pregnancy safety of Atorvastatin` | per_drug_section | 517ms | ✅ PASS |
| `Renal dose adjustment for Atorvastatin` | per_drug_section | 529ms | ✅ PASS |
| `Pediatric use of Atorvastatin` | per_drug_section | 487ms | ✅ PASS |
| `Mechanism of action of Atorvastatin` | per_drug_section | 445ms | ✅ PASS |
| `Indications for Atorvastatin` | per_drug_section | 487ms | ✅ PASS |
| `Storage conditions for Atorvastatin` | per_drug_section | 465ms | ✅ PASS |
| `Patient counseling for Atorvastatin` | per_drug_section | 453ms | ✅ PASS |
| `Contraindications of Rosuvastatin` | per_drug_section | 504ms | ✅ PASS |
| `Dosage and administration of Rosuvastatin` | per_drug_section | 449ms | ✅ PASS |
| `Drug interactions with Rosuvastatin` | per_drug_section | 495ms | ✅ PASS |
| `Pregnancy safety of Rosuvastatin` | per_drug_section | 446ms | ✅ PASS |
| `Renal dose adjustment for Rosuvastatin` | per_drug_section | 510ms | ✅ PASS |
| `Pediatric use of Rosuvastatin` | per_drug_section | 466ms | ✅ PASS |
| `Mechanism of action of Rosuvastatin` | per_drug_section | 625ms | ✅ PASS |
| `Indications for Rosuvastatin` | per_drug_section | 505ms | ✅ PASS |
| `Storage conditions for Rosuvastatin` | per_drug_section | 598ms | ✅ PASS |
| `Patient counseling for Rosuvastatin` | per_drug_section | 507ms | ✅ PASS |
| `Contraindications of Simvastatin` | per_drug_section | 495ms | ✅ PASS |
| `Dosage and administration of Simvastatin` | per_drug_section | 500ms | ✅ PASS |
| `Drug interactions with Simvastatin` | per_drug_section | 443ms | ✅ PASS |
| `Pregnancy safety of Simvastatin` | per_drug_section | 498ms | ✅ PASS |
| `Renal dose adjustment for Simvastatin` | per_drug_section | 485ms | ✅ PASS |
| `Pediatric use of Simvastatin` | per_drug_section | 600ms | ✅ PASS |
| `Mechanism of action of Simvastatin` | per_drug_section | 488ms | ✅ PASS |
| `Indications for Simvastatin` | per_drug_section | 501ms | ✅ PASS |
| `Storage conditions for Simvastatin` | per_drug_section | 533ms | ✅ PASS |
| `Patient counseling for Simvastatin` | per_drug_section | 541ms | ✅ PASS |
| `Contraindications of Pravastatin` | per_drug_section | 565ms | ✅ PASS |
| `Dosage and administration of Pravastatin` | per_drug_section | 465ms | ✅ PASS |
| `Drug interactions with Pravastatin` | per_drug_section | 503ms | ✅ PASS |
| `Pregnancy safety of Pravastatin` | per_drug_section | 478ms | ✅ PASS |
| `Renal dose adjustment for Pravastatin` | per_drug_section | 528ms | ✅ PASS |
| `Pediatric use of Pravastatin` | per_drug_section | 471ms | ✅ PASS |
| `Mechanism of action of Pravastatin` | per_drug_section | 774ms | ✅ PASS |
| `Indications for Pravastatin` | per_drug_section | 521ms | ✅ PASS |
| `Storage conditions for Pravastatin` | per_drug_section | 400ms | ✅ PASS |
| `Patient counseling for Pravastatin` | per_drug_section | 451ms | ✅ PASS |
| `Contraindications of Lovastatin` | per_drug_section | 544ms | ✅ PASS |
| `Dosage and administration of Lovastatin` | per_drug_section | 474ms | ✅ PASS |
| `Drug interactions with Lovastatin` | per_drug_section | 443ms | ✅ PASS |
| `Pregnancy safety of Lovastatin` | per_drug_section | 419ms | ✅ PASS |
| `Renal dose adjustment for Lovastatin` | per_drug_section | 436ms | ✅ PASS |
| `Pediatric use of Lovastatin` | per_drug_section | 423ms | ✅ PASS |
| `Mechanism of action of Lovastatin` | per_drug_section | 476ms | ✅ PASS |
| `Indications for Lovastatin` | per_drug_section | 428ms | ✅ PASS |
| `Storage conditions for Lovastatin` | per_drug_section | 480ms | ✅ PASS |
| `Patient counseling for Lovastatin` | per_drug_section | 477ms | ✅ PASS |
| `Contraindications of Ezetimibe` | per_drug_section | 537ms | ✅ PASS |
| `Dosage and administration of Ezetimibe` | per_drug_section | 439ms | ✅ PASS |
| `Drug interactions with Ezetimibe` | per_drug_section | 453ms | ✅ PASS |
| `Pregnancy safety of Ezetimibe` | per_drug_section | 647ms | ✅ PASS |
| `Renal dose adjustment for Ezetimibe` | per_drug_section | 428ms | ✅ PASS |
| `Pediatric use of Ezetimibe` | per_drug_section | 429ms | ✅ PASS |
| `Mechanism of action of Ezetimibe` | per_drug_section | 505ms | ✅ PASS |
| `Indications for Ezetimibe` | per_drug_section | 561ms | ✅ PASS |
| `Storage conditions for Ezetimibe` | per_drug_section | 480ms | ✅ PASS |
| `Patient counseling for Ezetimibe` | per_drug_section | 486ms | ✅ PASS |
| `Contraindications of Fenofibrate` | per_drug_section | 479ms | ✅ PASS |
| `Dosage and administration of Fenofibrate` | per_drug_section | 495ms | ✅ PASS |
| `Drug interactions with Fenofibrate` | per_drug_section | 525ms | ✅ PASS |
| `Pregnancy safety of Fenofibrate` | per_drug_section | 481ms | ✅ PASS |
| `Renal dose adjustment for Fenofibrate` | per_drug_section | 487ms | ✅ PASS |
| `Pediatric use of Fenofibrate` | per_drug_section | 548ms | ✅ PASS |
| `Mechanism of action of Fenofibrate` | per_drug_section | 543ms | ✅ PASS |
| `Indications for Fenofibrate` | per_drug_section | 592ms | ✅ PASS |
| `Storage conditions for Fenofibrate` | per_drug_section | 497ms | ✅ PASS |
| `Patient counseling for Fenofibrate` | per_drug_section | 495ms | ✅ PASS |
| `Contraindications of Gemfibrozil` | per_drug_section | 469ms | ✅ PASS |
| `Dosage and administration of Gemfibrozil` | per_drug_section | 514ms | ✅ PASS |
| `Drug interactions with Gemfibrozil` | per_drug_section | 467ms | ✅ PASS |
| `Pregnancy safety of Gemfibrozil` | per_drug_section | 513ms | ✅ PASS |
| `Renal dose adjustment for Gemfibrozil` | per_drug_section | 480ms | ✅ PASS |
| `Pediatric use of Gemfibrozil` | per_drug_section | 513ms | ✅ PASS |
| `Mechanism of action of Gemfibrozil` | per_drug_section | 467ms | ✅ PASS |
| `Indications for Gemfibrozil` | per_drug_section | 522ms | ✅ PASS |
| `Storage conditions for Gemfibrozil` | per_drug_section | 530ms | ✅ PASS |
| `Patient counseling for Gemfibrozil` | per_drug_section | 460ms | ✅ PASS |
| `Contraindications of Sacubitril_valsartan` | per_drug_section | 524ms | ❌ FAIL |
| `Dosage and administration of Sacubitril_valsartan` | per_drug_section | 468ms | ❌ FAIL |
| `Drug interactions with Sacubitril_valsartan` | per_drug_section | 518ms | ❌ FAIL |
| `Pregnancy safety of Sacubitril_valsartan` | per_drug_section | 512ms | ❌ FAIL |
| `Renal dose adjustment for Sacubitril_valsartan` | per_drug_section | 495ms | ❌ FAIL |
| `Pediatric use of Sacubitril_valsartan` | per_drug_section | 628ms | ❌ FAIL |
| `Mechanism of action of Sacubitril_valsartan` | per_drug_section | 422ms | ❌ FAIL |
| `Indications for Sacubitril_valsartan` | per_drug_section | 539ms | ❌ FAIL |
| `Storage conditions for Sacubitril_valsartan` | per_drug_section | 453ms | ❌ FAIL |
| `Patient counseling for Sacubitril_valsartan` | per_drug_section | 481ms | ❌ FAIL |
| `Contraindications of Lisinopril` | per_drug_section | 510ms | ✅ PASS |
| `Dosage and administration of Lisinopril` | per_drug_section | 621ms | ✅ PASS |
| `Drug interactions with Lisinopril` | per_drug_section | 656ms | ✅ PASS |
| `Pregnancy safety of Lisinopril` | per_drug_section | 795ms | ✅ PASS |
| `Renal dose adjustment for Lisinopril` | per_drug_section | 640ms | ✅ PASS |
| `Pediatric use of Lisinopril` | per_drug_section | 672ms | ✅ PASS |
| `Mechanism of action of Lisinopril` | per_drug_section | 761ms | ✅ PASS |
| `Indications for Lisinopril` | per_drug_section | 643ms | ✅ PASS |
| `Storage conditions for Lisinopril` | per_drug_section | 435ms | ✅ PASS |
| `Patient counseling for Lisinopril` | per_drug_section | 446ms | ✅ PASS |
| `Contraindications of Enalapril` | per_drug_section | 411ms | ✅ PASS |
| `Dosage and administration of Enalapril` | per_drug_section | 412ms | ✅ PASS |
| `Drug interactions with Enalapril` | per_drug_section | 400ms | ✅ PASS |
| `Pregnancy safety of Enalapril` | per_drug_section | 343ms | ✅ PASS |
| `Renal dose adjustment for Enalapril` | per_drug_section | 435ms | ✅ PASS |
| `Pediatric use of Enalapril` | per_drug_section | 390ms | ✅ PASS |
| `Mechanism of action of Enalapril` | per_drug_section | 446ms | ✅ PASS |
| `Indications for Enalapril` | per_drug_section | 1607ms | ✅ PASS |
| `Storage conditions for Enalapril` | per_drug_section | 358ms | ✅ PASS |
| `Patient counseling for Enalapril` | per_drug_section | 393ms | ✅ PASS |
| `Contraindications of Ramipril` | per_drug_section | 349ms | ✅ PASS |
| `Dosage and administration of Ramipril` | per_drug_section | 343ms | ✅ PASS |
| `Drug interactions with Ramipril` | per_drug_section | 423ms | ✅ PASS |
| `Pregnancy safety of Ramipril` | per_drug_section | 457ms | ✅ PASS |
| `Renal dose adjustment for Ramipril` | per_drug_section | 394ms | ✅ PASS |
| `Pediatric use of Ramipril` | per_drug_section | 411ms | ✅ PASS |
| `Mechanism of action of Ramipril` | per_drug_section | 594ms | ✅ PASS |
| `Indications for Ramipril` | per_drug_section | 926ms | ✅ PASS |
| `Storage conditions for Ramipril` | per_drug_section | 858ms | ✅ PASS |
| `Patient counseling for Ramipril` | per_drug_section | 837ms | ✅ PASS |
| `Mechanism of action of Coca-Cola` | adversarial_impossible_query | N/A | ✅ PASS |
| `Contraindications of Superman` | adversarial_wrong_drug | N/A | ✅ PASS |
| `Novamox dosage` | adversarial_brand_resolution | N/A | ✅ PASS |
| `Metoformin contraindications` | adversarial_typo_tolerance | N/A | ✅ PASS |
| `Metformin Warfarin Lisinopril indications` | adversarial_multi_drug_separation | N/A | ✅ PASS |
| `Metformin dosage` | adversarial_mixed_query | N/A | ✅ PASS |
| `Warfarin interactions` | adversarial_mixed_query | N/A | ✅ PASS |
| `Atorvastatin pregnancy` | adversarial_mixed_query | N/A | ✅ PASS |

---

## Detailed Query Logs
### Query: "Contraindications of Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 351ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 406ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 319ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 330ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 325ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 2011ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 352ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 1639ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Apixaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 376ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 324ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 363ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 435ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 372ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 349ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 340ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 290ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 303ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Rivaroxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 300ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 293ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 307ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 337ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 393ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 322ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 283ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 285ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 406ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Dabigatran" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 320ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 307ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 317ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 302ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 343ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 339ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 305ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 302ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Edoxaban" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 327ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 297ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 357ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 305ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 318ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 316ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 291ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 310ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 290ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 301ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Warfarin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 327ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 321ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 326ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 394ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Clopidogrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 314ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 328ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Clopidogrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 376ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 417ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 335ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Clopidogrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 359ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Clopidogrel" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 428ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 357ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Ticagrelor" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 352ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Ticagrelor" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 567ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 639ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 496ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 513ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 536ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 554ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Ticagrelor" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 425ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Ticagrelor" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 574ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 614ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 547ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 559ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 560ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 571ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 640ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 477ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 603ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 552ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Prasugrel" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 567ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 586ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 569ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 539ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 517ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 529ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 487ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 445ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 487ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 465ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Atorvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 453ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 504ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 449ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 495ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 446ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 510ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 466ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 625ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 505ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 598ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Rosuvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 507ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 495ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 500ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 443ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 498ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 485ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 600ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 488ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 501ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 533ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Simvastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 541ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 565ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 465ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 503ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 478ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 528ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 471ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 774ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 521ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 400ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Pravastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 451ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 544ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 474ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 443ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 419ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 436ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 423ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 476ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 428ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 480ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Lovastatin" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 477ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 537ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 439ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 453ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 647ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 428ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 429ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 505ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 561ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 480ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Ezetimibe" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 486ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 479ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 495ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 525ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 481ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 487ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 548ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 543ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 592ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 497ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Fenofibrate" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 495ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 469ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 514ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 467ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 513ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 480ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 513ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 467ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 522ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 530ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Gemfibrozil" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 460ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 524ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 468ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 518ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 512ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 495ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 628ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 422ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 539ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 453ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Sacubitril_valsartan" (Status: ❌ FAIL)
*   **Test Type:** per_drug_section
*   **Latency:** 481ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 510ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 621ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 656ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 795ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 640ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 672ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 761ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 643ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 435ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Lisinopril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 446ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 411ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 412ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 400ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 343ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 435ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 390ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 446ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 1607ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 358ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Enalapril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 393ms
*   **Chunks Retrieved:** 5

### Query: "Contraindications of Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 349ms
*   **Chunks Retrieved:** 5

### Query: "Dosage and administration of Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 343ms
*   **Chunks Retrieved:** 5

### Query: "Drug interactions with Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 423ms
*   **Chunks Retrieved:** 5

### Query: "Pregnancy safety of Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 457ms
*   **Chunks Retrieved:** 5

### Query: "Renal dose adjustment for Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 394ms
*   **Chunks Retrieved:** 5

### Query: "Pediatric use of Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 411ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 594ms
*   **Chunks Retrieved:** 5

### Query: "Indications for Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 926ms
*   **Chunks Retrieved:** 5

### Query: "Storage conditions for Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 858ms
*   **Chunks Retrieved:** 5

### Query: "Patient counseling for Ramipril" (Status: ✅ PASS)
*   **Test Type:** per_drug_section
*   **Latency:** 837ms
*   **Chunks Retrieved:** 5

### Query: "Mechanism of action of Coca-Cola" (Status: ✅ PASS)
*   **Test Type:** adversarial_impossible_query
*   **Expected:** No high-confidence match
*   **Top Score:** 0.3082

### Query: "Contraindications of Superman" (Status: ✅ PASS)
*   **Test Type:** adversarial_wrong_drug
*   **Expected:** No high-confidence match
*   **Top Score:** 0.4456

### Query: "Novamox dosage" (Status: ✅ PASS)
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

