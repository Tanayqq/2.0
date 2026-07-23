"""
Quality Gate Pipeline for MedRef Ingestion (Corpus v4.0)

Enforces strict clinical data quality checks prior to vector embedding & Qdrant upload:
1. DocumentValidator
2. ChunkValidator
3. AliasValidator
4. MetadataValidator
"""

import re
import structlog
from typing import Dict, Any, List, Tuple, Optional

logger = structlog.get_logger()

MIN_CHUNK_CHARS = 40
MAX_CHUNK_CHARS = 4000
CORPUS_VERSION = "v4.0"


class QualityGateValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __bool__(self):
        return self.is_valid


class QualityGatePipeline:
    """
    Pre-Qdrant Quality Gate Suite.
    Runs Document, Chunk, Alias, and Metadata validation on extracted labels.
    """

    def validate_document(self, doc: Any) -> QualityGateValidationResult:
        """
        Validate document object before chunking.
        """
        errors = []
        warnings = []

        if not doc:
            return QualityGateValidationResult(False, ["Document is None or empty"])

        drug_name = getattr(doc, "drug", None) or (doc.metadata.get("drug_name") if hasattr(doc, "metadata") and doc.metadata else None)
        if not drug_name or not str(drug_name).strip():
            errors.append("Document missing valid drug name")

        sections = getattr(doc, "sections", {})
        if not sections or len(sections) < 1:
            errors.append(f"Document '{drug_name}' has 0 clinical sections")
        elif len(sections) < 3:
            warnings.append(f"Document '{drug_name}' has fewer than 3 sections ({len(sections)})")

        authority = getattr(doc, "authority", None) or (doc.metadata.get("authority") if hasattr(doc, "metadata") and doc.metadata else "DailyMed")
        if authority not in ["DailyMed", "openFDA", "RxNorm", "FDA"]:
            warnings.append(f"Document '{drug_name}' has unrecognized authority: {authority}")

        return QualityGateValidationResult(len(errors) == 0, errors, warnings)

    def validate_chunk(self, chunk_text: str, chunk_index: int, drug_name: str) -> QualityGateValidationResult:
        """
        Validate chunk text content and token length.
        """
        errors = []
        warnings = []

        if not chunk_text or not chunk_text.strip():
            return QualityGateValidationResult(False, [f"Chunk {chunk_index} for '{drug_name}' is empty"])

        char_len = len(chunk_text.strip())
        if char_len < MIN_CHUNK_CHARS:
            errors.append(f"Chunk {chunk_index} for '{drug_name}' too short ({char_len} chars < {MIN_CHUNK_CHARS})")
        elif char_len > MAX_CHUNK_CHARS:
            warnings.append(f"Chunk {chunk_index} for '{drug_name}' unusually long ({char_len} chars)")

        # Check for unparsed XML/HTML tags
        if "<xhtml:" in chunk_text or "xmlns=" in chunk_text:
            warnings.append(f"Chunk {chunk_index} for '{drug_name}' contains raw unparsed XML namespaces")

        return QualityGateValidationResult(len(errors) == 0, errors, warnings)

    def validate_alias(self, drug_name: str, aliases: List[str]) -> QualityGateValidationResult:
        """
        Validate alias mapping integrity.
        """
        errors = []
        warnings = []

        if not aliases:
            warnings.append(f"No brand aliases found for drug '{drug_name}'")

        cleaned_aliases = []
        for a in aliases:
            if not isinstance(a, str) or not a.strip():
                continue
            if len(a.strip()) < 2:
                continue
            cleaned_aliases.append(a.strip())

        return QualityGateValidationResult(True, errors, warnings)

    def validate_metadata(self, metadata: Dict[str, Any], drug_name: str) -> QualityGateValidationResult:
        """
        Validate chunk metadata dictionary before FastEmbed embedding and Qdrant payload creation.
        """
        errors = []
        warnings = []

        required_keys = ["drug_name", "section", "authority"]
        for key in required_keys:
            if key not in metadata or metadata[key] is None:
                errors.append(f"Metadata for '{drug_name}' missing required field: '{key}'")

        # Enforce Corpus Version v4.0
        metadata["corpus_version"] = CORPUS_VERSION

        return QualityGateValidationResult(len(errors) == 0, errors, warnings)


quality_gate_pipeline = QualityGatePipeline()
