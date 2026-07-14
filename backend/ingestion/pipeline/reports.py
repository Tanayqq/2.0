import os
import json
import datetime
import structlog
from typing import List, Dict, Any
from .statistics import IngestionStatistics
from .config import ingestion_config

logger = structlog.get_logger()

class ReportGenerator:
    """
    Auto-generates INGESTION_REPORT.md, CORPUS_REPORT.md, manifest.json, and SMOKE_TEST.md.
    """
    def __init__(self, stats: IngestionStatistics):
        self.stats = stats
        self.docs_dir = os.path.join(os.path.dirname(os.path.dirname(ingestion_config.BASE_DIR)), "docs")
        os.makedirs(self.docs_dir, exist_ok=True)

    def generate_manifest(self):
        """
        Generates manifest.json.
        """
        filepath = os.path.join(self.docs_dir, "manifest.json")
        
        manifest_data = {
            "manifest_version": "1.0",
            "pipeline_version": ingestion_config.PIPELINE_VERSION,
            "embedding_model": ingestion_config.EMBEDDING_MODEL_NAME,
            "embedding_dimension": ingestion_config.EMBEDDING_DIMENSION,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "total_drugs": len(self.stats.drug_chunk_counts),
                "total_chunks": self.stats.chunks_created,
                "total_sections": self.stats.sections_extracted,
                "source_counts": self.stats.source_distribution
            }
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, ensure_ascii=False)
            logger.info("pipeline_manifest_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_pipeline_manifest", path=filepath, error=str(e))

    def get_text_quality_report(self) -> str:
        """
        Produces the exact textual Dataset Quality Report representation.
        """
        total_drugs = len(self.stats.drug_chunk_counts)
        avg_sections = self.stats.get_average_sections_per_drug()
        
        # Calculate chunks per drug average
        if total_drugs > 0:
            avg_chunks = round(self.stats.chunks_created / total_drugs, 1)
        else:
            avg_chunks = 0.0
            
        total_chunks = self.stats.chunks_created
        
        # Completeness statistics
        complete_count = 0
        incomplete_count = 0
        missing_counts = {}
        
        for drug, comp_data in self.stats.drug_completeness.items():
            status_by_category, score, percentage = comp_data
            if score == 13:
                complete_count += 1
            else:
                incomplete_count += 1
                
            for category, present in status_by_category.items():
                if not present:
                    missing_counts[category] = missing_counts.get(category, 0) + 1
                    
        report_lines = [
            "==================================================",
            "MedRef Ingestion Report",
            "==================================================",
            f"Total Drugs                {total_drugs}",
            f"Average Sections per Drug  {avg_sections}",
            f"Average Chunks per Drug    {avg_chunks}",
            f"Total Chunks               {total_chunks}",
            f"Complete Drugs (100%)      {complete_count}",
            f"Incomplete Drugs           {incomplete_count}"
        ]
        
        for category, count in sorted(missing_counts.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"Missing {category:<18} {count}")
            
        report_lines.append("==================================================")
        return "\n".join(report_lines)

    def generate_ingestion_report(self):
        """
        Generates docs/INGESTION_REPORT.md.
        """
        filepath = os.path.join(self.docs_dir, "INGESTION_REPORT.md")
        
        duration = self.stats.get_duration_sec()
        m, s = divmod(int(duration), 60)
        duration_str = f"{m}m {s:02d}s"
        
        chunk_metrics = self.stats.get_chunk_metrics()
        avg_sections = self.stats.get_average_sections_per_drug()
        
        text_quality_report = self.get_text_quality_report()
        
        md = f"""# MedRef Ingestion Report
Generated at: {datetime.datetime.utcnow().isoformat()}Z
Pipeline Version: {ingestion_config.PIPELINE_VERSION}

## Ingestion Quality Dashboard
```text
{text_quality_report}
```

## Execution Summary
*   **Run Time:** {duration_str} ({round(duration, 2)} seconds)
*   **Downloaded Drugs:** {self.stats.docs_downloaded}
*   **Successfully Parsed:** {self.stats.docs_parsed}
*   **Validation Failures:** {self.stats.validation_failures}
*   **Total Extracted Sections:** {self.stats.sections_extracted}
*   **Total Chunks Created:** {self.stats.chunks_created}
*   **Embeddings Generated:** {self.stats.embeddings_generated}
*   **Uploaded Chunks:** {self.stats.upload_success}
*   **Upload Failures:** {self.stats.upload_failures}
*   **Duplicates Skipped:** {self.stats.duplicates_skipped}

## Chunk Statistics
*   **Minimum Chunk Size:** {chunk_metrics['min']} tokens
*   **Maximum Chunk Size:** {chunk_metrics['max']} tokens
*   **Average Chunk Size:** {chunk_metrics['mean']} tokens
*   **Median Chunk Size:** {chunk_metrics['median']} tokens
*   **Average Sections per Drug:** {avg_sections}

## Validation Failures Log
"""
        if self.stats.validation_failure_reasons:
            for idx, reason in enumerate(self.stats.validation_failure_reasons, 1):
                md += f"{idx}. {reason}\n"
        else:
            md += "*No validation failures recorded during this run.*\n"
            
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("ingestion_report_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_ingestion_report", path=filepath, error=str(e))

    def generate_corpus_report(self):
        """
        Generates docs/CORPUS_REPORT.md.
        """
        filepath = os.path.join(self.docs_dir, "CORPUS_REPORT.md")
        chunk_metrics = self.stats.get_chunk_metrics()
        avg_sections = self.stats.get_average_sections_per_drug()
        
        md = f"""# MedRef Corpus Report
Generated at: {datetime.datetime.utcnow().isoformat()}Z

## Overall Corpus Summary
*   **Total Drugs:** {len(self.stats.drug_chunk_counts)}
*   **Total Sections:** {self.stats.sections_extracted}
*   **Total Chunks:** {self.stats.chunks_created}
*   **Average Sections per Drug:** {avg_sections}
*   **Average Chunk Length:** {chunk_metrics['mean']} tokens
*   **Median Chunk Length:** {chunk_metrics['median']} tokens

## Source Distribution
| Source | Chunks Count | Percentage |
|---|---|---|
"""
        total = max(1, self.stats.chunks_created)
        for src, count in self.stats.source_distribution.items():
            pct = round((count / total) * 100, 1)
            md += f"| {src} | {count} | {pct}% |\n"
            
        md += """
## Country Distribution
| Country | Chunks Count | Percentage |
|---|---|---|
"""
        for country, count in self.stats.country_distribution.items():
            pct = round((count / total) * 100, 1)
            md += f"| {country} | {count} | {pct}% |\n"
            
        md += """
## Clinical Section Distribution
| Section Title | Chunks Count |
|---|---|
"""
        # Sort sections by count descending
        sorted_sections = sorted(self.stats.section_distribution.items(), key=lambda x: x[1], reverse=True)
        for section, count in sorted_sections:
            md += f"| {section} | {count} |\n"
            
        md += """
## Drug Completeness & Chunk Breakdown
| Drug | Total Sections | Chunks Created | Completeness Score | Status |
|---|---|---|---|---|
"""
        for drug in sorted(self.stats.drug_chunk_counts.keys()):
            sections = self.stats.drug_sections_counts.get(drug, 0)
            chunks = self.stats.drug_chunk_counts.get(drug, 0)
            
            # Retrieve completeness score details
            comp_data = self.stats.drug_completeness.get(drug)
            if comp_data:
                _, score, pct = comp_data
                status = "✅ Complete" if score == 13 else "❌ Incomplete"
                score_str = f"{score}/13 ({pct}%)"
            else:
                score_str = "N/A"
                status = "N/A"
                
            md += f"| {drug} | {sections} | {chunks} | {score_str} | {status} |\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("corpus_report_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_corpus_report", path=filepath, error=str(e))

    def generate_smoke_test_report(self, results: List[Dict[str, Any]]):
        """
        Generates docs/SMOKE_TEST.md from search execution results.
        """
        filepath = os.path.join(self.docs_dir, "SMOKE_TEST.md")
        
        md = f"""# MedRef Ingestion Smoke Test Results
Generated at: {datetime.datetime.utcnow().isoformat()}Z
Embedding Model: {ingestion_config.EMBEDDING_MODEL_NAME}

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Chunks Retrieved | Top Score | Latency (ms) | Status |
|---|---|---|---|---|
"""
        for r in results:
            status_emoji = "✅ PASS" if r["pass"] else "❌ FAIL"
            top_score = r["retrieved_chunks"][0]["score"] if r["retrieved_chunks"] else 0.0
            md += f"| `{r['query']}` | {len(r['retrieved_chunks'])} | {top_score:.4f} | {int(r['latency_sec'] * 1000)}ms | {status_emoji} |\n"
            
        md += "\n---\n\n## Detailed Query Logs\n"
        
        for r in results:
            status_emoji = "✅ PASS" if r["pass"] else "❌ FAIL"
            md += f"### Query: \"{r['query']}\" (Status: {status_emoji})\n"
            md += f"*   **Latency:** {int(r['latency_sec'] * 1000)}ms\n"
            md += f"*   **Chunks Retrieved:** {len(r['retrieved_chunks'])}\n\n"
            
            if r["retrieved_chunks"]:
                md += "| Rank | Chunk ID | Similarity Score | Source | Content Snippet |\n"
                md += "|---|---|---|---|---|\n"
                for rank, chunk in enumerate(r["retrieved_chunks"], 1):
                    snippet = chunk["content"][:100].replace("\n", " ") + "..."
                    md += f"| {rank} | `{chunk['id']}` | {chunk['score']:.4f} | {chunk['source']} | {snippet} |\n"
            else:
                md += "*No documents retrieved for this query.*\n"
            md += "\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("smoke_test_report_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_smoke_test_report", path=filepath, error=str(e))
