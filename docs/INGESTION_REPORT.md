# MedRef Ingestion Report
Generated at: 2026-07-16T08:45:22.438402Z
Pipeline Version: 1.6.0

## Ingestion Quality Dashboard
```text
==================================================
MedRef Ingestion Report
==================================================
Total Drugs                29
Average Sections per Drug  40.9
Average Chunks per Drug    78.4
Total Chunks               2274
Complete Drugs (100%)      17
Incomplete Drugs           12
Missing Hepatic            10
Missing Renal              10
Missing Geriatric          1
==================================================
```

## Execution Summary
*   **Run Time:** 13m 20s (800.3 seconds)
*   **Downloaded Drugs:** 35
*   **Successfully Parsed:** 29
*   **Validation Failures:** 6
*   **Total Extracted Sections:** 1185
*   **Total Chunks Created:** 2274
*   **Embeddings Generated:** 0
*   **Uploaded Chunks:** 0
*   **Upload Failures:** 0
*   **Duplicates Skipped:** 0

## Chunk Statistics
*   **Minimum Chunk Size:** 31 tokens
*   **Maximum Chunk Size:** 453 tokens
*   **Average Chunk Size:** 302.1 tokens
*   **Median Chunk Size:** 365.0 tokens
*   **Average Sections per Drug:** 40.9

## Validation Failures Log
1. Drug 'gliclazide' could not be fetched from any active source.
2. Drug 'vildagliptin' could not be fetched from any active source.
3. Validation failed for 'carbimazole': Parser returned zero sections — likely corrupt or unreachable label
4. Drug 'glibenclamide' could not be fetched from any active source.
5. Drug 'gliquidone' could not be fetched from any active source.
6. Drug 'teneligliptin' could not be fetched from any active source.
