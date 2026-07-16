import time
import statistics
from typing import List, Dict, Any, Optional

class IngestionStatistics:
    """
    State manager to capture pipeline metrics, validation failures, 
    and chunk statistics for reporting.
    """
    def __init__(self):
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        
        self.docs_downloaded: int = 0
        self.docs_parsed: int = 0
        self.validation_failures: int = 0
        self.validation_failure_reasons: List[str] = []
        
        self.sections_extracted: int = 0
        self.chunks_created: int = 0
        self.embeddings_generated: int = 0
        self.upload_success: int = 0
        self.upload_failures: int = 0
        self.duplicates_skipped: int = 0
        
        self.chunk_sizes: List[int] = []  # Token counts
        self.section_distribution: Dict[str, int] = {}
        self.drug_chunk_counts: Dict[str, int] = {}
        self.drug_sections_counts: Dict[str, int] = {}
        self.drug_sources: Dict[str, str] = {}
        self.source_distribution: Dict[str, int] = {}
        self.country_distribution: Dict[str, int] = {}
        self.drug_completeness: Dict[str, Any] = {}

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def get_duration_sec(self) -> float:
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def log_validation_failure(self, reason: str):
        self.validation_failures += 1
        self.validation_failure_reasons.append(reason)

    def record_chunk(self, drug: str, section: str, tokens: int, source: str, country: str):
        self.chunks_created += 1
        self.chunk_sizes.append(tokens)
        
        # Distributions
        self.section_distribution[section] = self.section_distribution.get(section, 0) + 1
        self.drug_chunk_counts[drug] = self.drug_chunk_counts.get(drug, 0) + 1
        self.source_distribution[source] = self.source_distribution.get(source, 0) + 1
        self.country_distribution[country] = self.country_distribution.get(country, 0) + 1
        self.drug_sources[drug] = source

    def record_drug_sections(self, drug: str, sections_count: int):
        self.drug_sections_counts[drug] = sections_count
        self.sections_extracted += sections_count

    def get_chunk_metrics(self) -> Dict[str, Any]:
        """
        Compute min, max, average, and median chunk sizes.
        """
        if not self.chunk_sizes:
            return {"min": 0, "max": 0, "mean": 0, "median": 0}
            
        return {
            "min": min(self.chunk_sizes),
            "max": max(self.chunk_sizes),
            "mean": round(statistics.mean(self.chunk_sizes), 1),
            "median": round(statistics.median(self.chunk_sizes), 1)
        }
        
    def get_average_sections_per_drug(self) -> float:
        if not self.drug_sections_counts:
            return 0.0
        return round(statistics.mean(self.drug_sections_counts.values()), 1)

    def record_drug_completeness(self, drug: str, status_by_category: Dict[str, bool], score: int, percentage: float):
        self.drug_completeness[drug] = (status_by_category, score, percentage)
