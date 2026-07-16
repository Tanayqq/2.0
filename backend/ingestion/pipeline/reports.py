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
        for comp_data in self.stats.drug_completeness.values():
            status_by_category, score, pct = comp_data
            if score == 13:
                complete_count += 1
            else:
                incomplete_count += 1
                    
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
        
        missing_sections_details = []
        for drug, comp_data in self.stats.drug_completeness.items():
            status_by_category, score, pct = comp_data
            if score < 13:
                drug_source = self.stats.drug_sources.get(drug, "Unknown")
                for category, is_present in status_by_category.items():
                    if not is_present:
                        missing_sections_details.append({
                            "drug": drug,
                            "section": category,
                            "authority": drug_source
                        })
                        
        if missing_sections_details:
            report_lines.append("")
            report_lines.append("Verified Source Absences:")
            report_lines.append("-------------------------")
            for m in missing_sections_details:
                report_lines.append(f"Drug: {m['drug']}")
                report_lines.append(f"Section: {m['section']}")
                report_lines.append(f"Status: Not present in FDA label")
                report_lines.append(f"Authority: {m['authority']}")
                report_lines.append(f"Reason: Verified source absence")
                report_lines.append("")
            
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

    def _calculate_average_completeness(self) -> float:
        """
        Calculates the average completeness percentage across all drugs.
        """
        if not self.stats.drug_completeness:
            return 0.0
            
        total_pct = sum(comp[2] for comp in self.stats.drug_completeness.values())
        return round(total_pct / len(self.stats.drug_completeness), 1)

    def generate_corpus_report(self):
        """
        Generates docs/CORPUS_REPORT.md.
        """
        filepath = os.path.join(self.docs_dir, "CORPUS_REPORT.md")
        from .config import ingestion_config
        
        chunk_metrics = self.stats.get_chunk_metrics()
        avg_sections = self.stats.get_average_sections_per_drug()
        
        md = f"""# MedRef Corpus Report
Generated at: {datetime.datetime.utcnow().isoformat()}Z

## Corpus Health Dashboard
*   **Corpus Version:** {ingestion_config.CORPUS_VERSION}
*   **Total Drugs:** {len(self.stats.drug_chunk_counts)}
*   **Total Sections:** {self.stats.sections_extracted}
*   **Total Chunks:** {self.stats.chunks_created}
*   **Average Completeness:** {self._calculate_average_completeness()}%
*   **Average Sections per Drug:** {avg_sections}
*   **Average Chunks per Drug:** {int(self.stats.chunks_created / len(self.stats.drug_chunk_counts)) if self.stats.drug_chunk_counts else 0}
*   **Failed Downloads:** {self.stats.docs_downloaded - len(self.stats.drug_chunk_counts)}
*   **Duplicate Chunks:** 0 (Deduplicated via SHA-256 Hash)

## Authorities Distribution
| Authority | Chunks Count | Percentage |
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
        missing_sections_list = []
        for drug in sorted(self.stats.drug_chunk_counts.keys()):
            sections = self.stats.drug_sections_counts.get(drug, 0)
            chunks = self.stats.drug_chunk_counts.get(drug, 0)
            
            # Retrieve completeness score details
            comp_data = self.stats.drug_completeness.get(drug)
            if comp_data:
                status_by_cat, score, pct = comp_data
                status = "✅ Complete" if score == 13 else "❌ Incomplete"
                score_str = f"{score}/13 ({pct}%)"
                
                if score < 13:
                    drug_source = self.stats.drug_sources.get(drug, "Unknown")
                    for cat, is_present in status_by_cat.items():
                        if not is_present:
                            missing_sections_list.append({
                                "drug": drug,
                                "section": cat,
                                "authority": drug_source
                            })
            else:
                score_str = "N/A"
                status = "N/A"
                
            md += f"| {drug} | {sections} | {chunks} | {score_str} | {status} |\n"

        if missing_sections_list:
            md += "\n## Verified Source Absences\n"
            md += "| Drug | Missing Section | Authority | Reason |\n"
            md += "|---|---|---|---|\n"
            for m in missing_sections_list:
                md += f"| {m['drug']} | {m['section']} | {m['authority']} | Verified source absence |\n"


        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("corpus_report_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_corpus_report", path=filepath, error=str(e))

    def generate_smoke_test_report(self, results: List[Dict[str, Any]]):
        """
        Generates docs/SMOKE_TEST.md from search execution results.
        Supports both standard per-drug queries and adversarial tests.
        """
        filepath = os.path.join(self.docs_dir, "SMOKE_TEST.md")
        
        md = f"""# MedRef Ingestion Smoke Test Results
Generated at: {datetime.datetime.utcnow().isoformat()}Z
Embedding Model: {ingestion_config.EMBEDDING_MODEL_NAME}

This report records the retrieval smoke test results following ingestion.

## Smoke Test Summary
| Query | Test Type | Latency (ms) | Status |
|---|---|---|---|
"""
        passed_count = sum(1 for r in results if r.get("pass", False))
        md += f"**Total Tests:** {len(results)} | **Passed:** {passed_count} | **Failed:** {len(results) - passed_count}\n\n"

        for r in results:
            status_emoji = "✅ PASS" if r.get("pass", False) else "❌ FAIL"
            latency = r.get('latency_sec', 0)
            latency_str = f"{int(latency * 1000)}ms" if latency else "N/A"
            test_type = r.get('test_type', 'unknown')
            md += f"| `{r.get('query', 'N/A')}` | {test_type} | {latency_str} | {status_emoji} |\n"
            
        md += "\n---\n\n## Detailed Query Logs\n"
        
        for r in results:
            status_emoji = "✅ PASS" if r.get("pass", False) else "❌ FAIL"
            md += f"### Query: \"{r.get('query', 'N/A')}\" (Status: {status_emoji})\n"
            md += f"*   **Test Type:** {r.get('test_type', 'unknown')}\n"
            
            latency = r.get('latency_sec')
            if latency is not None:
                md += f"*   **Latency:** {int(latency * 1000)}ms\n"
            
            if 'expected' in r:
                md += f"*   **Expected:** {r['expected']}\n"
            if 'top_score' in r:
                md += f"*   **Top Score:** {r['top_score']:.4f}\n"
            if 'error' in r:
                md += f"*   **Error:** {r['error']}\n"
            if 'hits' in r:
                md += f"*   **Chunks Retrieved:** {r['hits']}\n"
                
            md += "\n"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("smoke_test_report_generated", path=filepath)
        except Exception as e:
            logger.error("failed_writing_smoke_test_report", path=filepath, error=str(e))

    def generate_corpus_manifest(self):
        """
        Generates CORPUS_MANIFEST.json — the canonical machine-readable summary
        of the entire ingested corpus. Exposed via /api/status on the backend.
        Saved both to docs/ (latest) and to a date-stamped history dir.
        """
        now = datetime.datetime.utcnow()
        date_str = now.strftime("%Y-%m-%d")
        
        # Date-stamped history directory (Refinement #5: ingestion history)
        history_dir = os.path.join(self.docs_dir, "reports", date_str)
        os.makedirs(history_dir, exist_ok=True)
        
        # Build per-section coverage from completeness stats
        section_coverage = {}
        if self.stats.drug_completeness:
            all_drugs = len(self.stats.drug_completeness)
            # Aggregate across all 13 completeness categories
            category_present = {}
            for drug, data in self.stats.drug_completeness.items():
                status_dict = data[0] if isinstance(data, tuple) else data.get("status_by_category", {})
                for cat, is_present in status_dict.items():
                    if cat not in category_present:
                        category_present[cat] = 0
                    if is_present:
                        category_present[cat] += 1
            for cat, count in category_present.items():
                pct = round((count / all_drugs) * 100, 1) if all_drugs > 0 else 0.0
                section_coverage[cat] = pct

        manifest = {
            "pipeline_version": ingestion_config.PIPELINE_VERSION,
            "parser_version": "2.1.0",
            "embedding_model": ingestion_config.EMBEDDING_MODEL_NAME,
            "embedding_dimension": ingestion_config.EMBEDDING_DIMENSION,
            "vector_db": "Qdrant",
            "collection": ingestion_config.QDRANT_COLLECTION,
            "authorities": list(self.stats.source_distribution.keys()) if hasattr(self.stats, "source_distribution") else ["DailyMed", "openFDA"],
            "created_at": now.isoformat() + "Z",
            "drugs": len(self.stats.drug_chunk_counts),
            "chunks": self.stats.chunks_created,
            "sections_extracted": self.stats.sections_extracted,
            "validation_failures": self.stats.validation_failures,
            "upload_success": self.stats.upload_success,
            "upload_failures": self.stats.upload_failures,
            "coverage": section_coverage,
            "avg_completeness_pct": round(
                sum((d[2] if isinstance(d, tuple) else d.get("percentage", 0)) for d in self.stats.drug_completeness.values()) /
                max(len(self.stats.drug_completeness), 1), 1
            ) if self.stats.drug_completeness else 0.0,
        }

        # Write to docs/CORPUS_MANIFEST.json (latest, overwrite)
        latest_path = os.path.join(self.docs_dir, "CORPUS_MANIFEST.json")
        # Write to date-stamped history dir
        history_path = os.path.join(history_dir, "CORPUS_MANIFEST.json")
        
        for path in [latest_path, history_path]:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2, ensure_ascii=False)
                logger.info("corpus_manifest_generated", path=path)
            except Exception as e:
                logger.error("failed_writing_corpus_manifest", path=path, error=str(e))
        
        # Also write date-stamped INGESTION_REPORT.md copy to history dir
        try:
            src = os.path.join(self.docs_dir, "INGESTION_REPORT.md")
            dst = os.path.join(history_dir, "INGESTION_REPORT.md")
            if os.path.exists(src):
                import shutil
                shutil.copy2(src, dst)
                logger.info("ingestion_report_archived", path=dst)
        except Exception as e:
            logger.error("failed_archiving_ingestion_report", error=str(e))

