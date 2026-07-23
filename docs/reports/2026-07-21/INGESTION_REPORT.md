# MedRef Ingestion Report
Generated at: 2026-07-21T13:31:54.112072Z
Pipeline Version: 1.6.0

## Ingestion Quality Dashboard
```text
==================================================
MedRef Ingestion Report
==================================================
Total Drugs                29
Average Sections per Drug  31.4
Average Chunks per Drug    45.5
Total Chunks               1320
Complete Drugs (100%)      12
Incomplete Drugs           17

Verified Source Absences:
-------------------------
Drug: Acarbose
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Acarbose
Section: Patient Counseling
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Drug Interactions
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Geriatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Alogliptin
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Canagliflozin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Canagliflozin
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Dulaglutide
Section: Drug Interactions
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Dulaglutide
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Empagliflozin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Fludrocortisone
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Fludrocortisone
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Insulin_glargine
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Insulin_lispro
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Linagliptin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Linagliptin
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Methimazole
Section: Geriatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Methimazole
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Methimazole
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Warnings
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Lactation
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Geriatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Patient Counseling
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Pioglitazone
Section: Drug Interactions
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Propylthiouracil
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Propylthiouracil
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Saxagliptin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Saxagliptin
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Semaglutide
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Semaglutide
Section: Hepatic
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Sitagliptin
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Sitagliptin
Section: Pediatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Sitagliptin
Section: Geriatric
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Sitagliptin
Section: Renal
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Tirzepatide
Section: Drug Interactions
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Tirzepatide
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

==================================================
```

## Execution Summary
*   **Run Time:** 5m 04s (304.45 seconds)
*   **Downloaded Drugs:** 30
*   **Successfully Parsed:** 29
*   **Validation Failures:** 1
*   **Total Extracted Sections:** 911
*   **Total Chunks Created:** 1320
*   **Embeddings Generated:** 1302
*   **Uploaded Chunks:** 1302
*   **Upload Failures:** 0
*   **Duplicates Skipped:** 0

## Chunk Statistics
*   **Minimum Chunk Size:** 16 tokens
*   **Maximum Chunk Size:** 455 tokens
*   **Average Chunk Size:** 228.4 tokens
*   **Median Chunk Size:** 202.0 tokens
*   **Average Sections per Drug:** 31.4

## Validation Failures Log
1. Validation failed for 'carbimazole': Parser returned zero sections — likely corrupt or unreachable label
