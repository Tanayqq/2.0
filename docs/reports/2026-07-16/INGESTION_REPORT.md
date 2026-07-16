# MedRef Ingestion Report
Generated at: 2026-07-16T16:14:09.891767Z
Pipeline Version: 1.6.0

## Ingestion Quality Dashboard
```text
==================================================
MedRef Ingestion Report
==================================================
Total Drugs                29
Average Sections per Drug  31.4
Average Chunks per Drug    42.7
Total Chunks               1237
Complete Drugs (100%)      12
Incomplete Drugs           17

Verified Source Absences:
-------------------------
Drug: Pioglitazone
Section: Drug Interactions
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

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

Drug: Empagliflozin
Section: Pregnancy
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

Drug: Insulin glargine
Section: Pregnancy
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Insulin lispro
Section: Pregnancy
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

Drug: Orlistat
Section: Contraindications
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Warnings
Status: Not present in FDA label
Authority: DailyMed
Reason: Verified source absence

Drug: Orlistat
Section: Drug Interactions
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

==================================================
```

## Execution Summary
*   **Run Time:** 6m 08s (368.49 seconds)
*   **Downloaded Drugs:** 35
*   **Successfully Parsed:** 29
*   **Validation Failures:** 6
*   **Total Extracted Sections:** 911
*   **Total Chunks Created:** 1237
*   **Embeddings Generated:** 243
*   **Uploaded Chunks:** 243
*   **Upload Failures:** 0
*   **Duplicates Skipped:** 0

## Chunk Statistics
*   **Minimum Chunk Size:** 31 tokens
*   **Maximum Chunk Size:** 449 tokens
*   **Average Chunk Size:** 242.2 tokens
*   **Median Chunk Size:** 226 tokens
*   **Average Sections per Drug:** 31.4

## Validation Failures Log
1. Drug 'gliclazide' could not be fetched from any active source.
2. Drug 'vildagliptin' could not be fetched from any active source.
3. Validation failed for 'carbimazole': Parser returned zero sections — likely corrupt or unreachable label
4. Drug 'glibenclamide' could not be fetched from any active source.
5. Drug 'gliquidone' could not be fetched from any active source.
6. Drug 'teneligliptin' could not be fetched from any active source.
