import os
import sys
import datetime
from collections import defaultdict
from typing import Dict, Any, List
import structlog

# Allow running from command line with correct import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from qdrant_client import QdrantClient
from backend.app.core.config import settings
from backend.ingestion.pipeline.config import ingestion_config

logger = structlog.get_logger()

def fetch_all_records() -> List[Any]:
    """Scroll Qdrant to retrieve all points and their payloads."""
    client = QdrantClient(url=ingestion_config.QDRANT_URL, api_key=ingestion_config.QDRANT_API_KEY)
    
    # Check if collection exists
    try:
        collections = [c.name for c in client.get_collections().collections]
        if ingestion_config.QDRANT_COLLECTION not in collections:
            logger.error("qdrant_collection_not_found", collection=ingestion_config.QDRANT_COLLECTION)
            return []
    except Exception as e:
        logger.error("failed_connecting_to_qdrant", error=str(e))
        return []

    logger.info("scrolling_qdrant_collection", collection=ingestion_config.QDRANT_COLLECTION)
    records = []
    offset = None
    while True:
        response, next_offset = client.scroll(
            collection_name=ingestion_config.QDRANT_COLLECTION,
            limit=100,
            with_payload=True,
            with_vectors=True, # Fetch vectors to check dimensions
            offset=offset
        )
        records.extend(response)
        if not next_offset:
            break
        offset = next_offset
        
    logger.info("scrolling_completed", total_points=len(records))
    return records

def generate_reports():
    records = fetch_all_records()
    if not records:
        logger.warning("no_records_fetched_reports_generation_skipped")
        return
        
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(ingestion_config.BASE_DIR)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    # Mappings for compiling coverage and retrieval stats
    drug_sections = defaultdict(set)
    drug_chunks = defaultdict(int)
    drug_last_updated = {}
    source_counts = defaultdict(int)
    section_counts = defaultdict(int)
    total_chars = 0
    vector_dims = set()
    
    # Duplicate check
    seen_contents = set()
    duplicate_count = 0
    
    for record in records:
        payload = record.payload or {}
        drug_name = payload.get("drug_name", payload.get("drug", "Unknown"))
        section = payload.get("section", "Unknown")
        source = payload.get("source", "Unknown")
        ingested_at = payload.get("ingested_at", "Unknown")
        content = payload.get("content", "")
        
        # Track expected/extracted metrics
        if drug_name:
            drug_sections[drug_name].add(section)
            drug_chunks[drug_name] += 1
            if ingested_at and ingested_at != "Unknown":
                drug_last_updated[drug_name] = ingested_at
                
        if source:
            source_counts[source] += 1
            
        if section:
            section_counts[section] += 1
            
        if content:
            total_chars += len(content)
            # Duplicate check by content hash
            import hashlib
            content_hash = hashlib.md5(content.strip().encode("utf-8")).hexdigest()
            if content_hash in seen_contents:
                duplicate_count += 1
            seen_contents.add(content_hash)
            
        if record.vector and isinstance(record.vector, dict) and "dense" in record.vector:
            vector_dims.add(len(record.vector["dense"]))
        elif record.vector and isinstance(record.vector, list):
            vector_dims.add(len(record.vector))

    # --- 1. CORPUS_COVERAGE.md ---
    expected_sections = ingestion_config.TARGET_SECTIONS
    expected_count = len(expected_sections)
    
    coverage_md = f"""# MedRef Corpus Coverage Report
Generated at: {datetime.datetime.utcnow().isoformat()}Z

## Coverage Summary
This report shows the completeness of clinical sections parsed for each ingested drug.

| Drug | Expected Sections | Present | Coverage | Total Chunks | Last Updated |
| :--- | :---: | :---: | :---: | :---: | :--- |
"""
    for drug in sorted(drug_sections.keys()):
        sections_present = len(drug_sections[drug])
        coverage_pct = round((sections_present / expected_count) * 100, 1)
        last_upd = drug_last_updated.get(drug, "N/A")
        chunks_cnt = drug_chunks[drug]
        coverage_md += f"| {drug.capitalize()} | {expected_count} | {sections_present} | {coverage_pct}% | {chunks_cnt} | {last_upd} |\n"
        
    coverage_path = os.path.join(docs_dir, "CORPUS_COVERAGE.md")
    with open(coverage_path, "w", encoding="utf-8") as f:
        f.write(coverage_md)
    logger.info("corpus_coverage_report_generated", path=coverage_path)

    # --- 2. RETRIEVAL_REPORT.md ---
    top_20_drugs = sorted(drug_chunks.items(), key=lambda x: x[1], reverse=True)[:20]
    avg_chunk_size_chars = round(total_chars / len(records), 1) if records else 0
    dim_str = ", ".join(str(d) for d in vector_dims) if vector_dims else "384"
    
    # Identify missing sections per drug
    missing_sections_count = 0
    for drug, sections in drug_sections.items():
        missing_sections_count += sum(1 for s in expected_sections if s not in sections)
        
    retrieval_md = f"""# MedRef Retrieval Report
Generated at: {datetime.datetime.utcnow().isoformat()}Z

## Overall Corpus Statistics
*   **Total Unique Drugs:** {len(drug_sections)}
*   **Total Points/Chunks in Qdrant:** {len(records)}
*   **Active Vector Dimensions:** {dim_str}
*   **Average Chunk Size (Characters):** {avg_chunk_size_chars}
*   **Total Duplicate Chunks Found:** {duplicate_count}
*   **Missing Sections Count (Cumulative):** {missing_sections_count}

## Source Distribution
| Source | Chunk Count | Percentage |
| :--- | :---: | :---: |
"""
    total_pts = len(records) or 1
    for src, cnt in source_counts.items():
        pct = round((cnt / total_pts) * 100, 1)
        retrieval_md += f"| {src} | {cnt} | {pct}% |\n"
        
    retrieval_md += """
## Top 20 Drugs by Chunk Count
| Drug Name | Sections Present | Chunk Count |
| :--- | :---: | :---: |
"""
    for drug, count in top_20_drugs:
        secs = len(drug_sections[drug])
        retrieval_md += f"| {drug.capitalize()} | {secs} | {count} |\n"
        
    retrieval_md += """
## Section Distribution
| Section Title | Total Chunks | Percentage |
| :--- | :---: | :---: |
"""
    for sec, cnt in sorted(section_counts.items(), key=lambda x: x[1], reverse=True):
        pct = round((cnt / total_pts) * 100, 1)
        retrieval_md += f"| {sec} | {cnt} | {pct}% |\n"
        
    retrieval_path = os.path.join(docs_dir, "RETRIEVAL_REPORT.md")
    with open(retrieval_path, "w", encoding="utf-8") as f:
        f.write(retrieval_md)
    logger.info("retrieval_report_generated", path=retrieval_path)

if __name__ == "__main__":
    generate_reports()
