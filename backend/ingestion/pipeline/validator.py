import os
import json
import datetime
import structlog
from typing import Dict, Any, Tuple
from .interfaces.source_provider import NormalizedMedicalDocument
from .config import ingestion_config

logger = structlog.get_logger()

class MedicalValidator:
    """
    Validation layer for normalized medical documents.
    Rejects malformed, incomplete, or corrupted records.
    Saves failed documents to the Dead Letter Queue (DLQ).
    """
    
    def validate(self, doc: NormalizedMedicalDocument) -> Tuple[bool, str]:
        """
        Validate a NormalizedMedicalDocument.
        Returns:
            Tuple of (is_valid: bool, error_reason: str)
        """
        if not doc:
            return False, "Document is None"
            
        # 1. Verify drug name
        if not doc.drug or not doc.drug.strip():
            return False, "Missing or empty drug name"
            
        # 2. Verify source and metadata
        if not doc.source or not doc.source.strip():
            return False, "Missing or empty data source metadata"
            
        if not doc.country or not doc.country.strip():
            return False, "Missing country metadata"
            
        if not doc.version or not doc.version.strip():
            return False, "Missing document version"
            
        # 3. Verify sections exist
        if not doc.sections:
            return False, "Document has no parsed text sections"
            
        # 4. Check section data quality
        total_content_length = 0
        for section in doc.sections:
            if not section.title or not section.title.strip():
                return False, "Found section with missing title"
                
            if not section.content or not section.content.strip():
                return False, f"Section '{section.title}' has empty content"
                
            content_len = len(section.content.strip())
            total_content_length += content_len
            
            # Warn/Reject extremely small sections (e.g. less than 10 characters)
            if content_len < 10:
                return False, f"Section '{section.title}' is too short ({content_len} characters)"
                
            # Reject extremely oversized sections (e.g. more than 200,000 chars)
            if content_len > 250000:
                return False, f"Section '{section.title}' is too large ({content_len} characters)"

        # 5. Verify total document size
        if total_content_length < 50:
            return False, f"Total document content is too short ({total_content_length} characters)"

        return True, ""

    def send_to_dlq(self, doc: NormalizedMedicalDocument, error_reason: str):
        """
        Saves a failed document to the Dead Letter Queue directory for inspection.
        """
        drug_safe = doc.drug.lower().replace(" ", "_") if doc and doc.drug else "unknown_drug"
        source_safe = doc.source.lower() if doc and doc.source else "unknown_source"
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{drug_safe}_{source_safe}_failed_{timestamp}.json"
        filepath = os.path.join(ingestion_config.DLQ_DIR, filename)
        
        # Structure the DLQ record
        dlq_record = {
            "error_reason": error_reason,
            "failed_at": datetime.datetime.utcnow().isoformat() + "Z",
            "document": doc.model_dump() if doc else None
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dlq_record, f, indent=2, ensure_ascii=False)
            logger.warning("sent_document_to_dlq", path=filepath, error=error_reason)
        except Exception as e:
            logger.error("failed_writing_to_dlq", path=filepath, error=str(e))

    def validate_chunks(self, chunks: list) -> Tuple[list, dict]:
        """
        Validates all chunk dictionaries before they are embedded.
        Checks for min/max tokens, empty content, duplicates, valid section names, and metadata completeness.
        Returns:
            Tuple of (valid_chunks: list, stats: dict)
        """
        valid_chunks = []
        stats = {
            "total_chunks_received": len(chunks),
            "valid_chunks": 0,
            "rejected_empty": 0,
            "rejected_too_short": 0,
            "rejected_too_long": 0,
            "rejected_duplicate": 0,
            "rejected_invalid_section": 0,
            "rejected_invalid_metadata": 0
        }
        
        seen_hashes = set()
        required_keys = ["drug_name", "generic_name", "section", "source", "document_id", "chunk_index", "total_chunks", "version", "ingested_at"]
        
        for chunk in chunks:
            # 1. Check empty chunk
            content = chunk.get("content", "")
            if not content or not content.strip():
                stats["rejected_empty"] += 1
                logger.warning("chunk_validation_failed_empty", drug=chunk.get("drug_name"))
                continue
                
            # 2. Check token bounds
            token_count = chunk.get("token_count", 0)
            if token_count < ingestion_config.MIN_CHUNK_TOKENS:
                stats["rejected_too_short"] += 1
                logger.warning("chunk_validation_failed_too_short", drug=chunk.get("drug_name"), tokens=token_count, min=ingestion_config.MIN_CHUNK_TOKENS)
                continue
                
            if token_count > ingestion_config.MAX_CHUNK_TOKENS:
                stats["rejected_too_long"] += 1
                logger.warning("chunk_validation_failed_too_long", drug=chunk.get("drug_name"), tokens=token_count, max=ingestion_config.MAX_CHUNK_TOKENS)
                continue
                
            # 3. Check section name
            section = chunk.get("section", "")
            if not section or not section.strip():
                stats["rejected_invalid_section"] += 1
                logger.warning("chunk_validation_failed_no_section", drug=chunk.get("drug_name"))
                continue
                
            # 4. Check metadata completeness
            meta_valid = True
            for k in required_keys:
                if k not in chunk or chunk[k] is None or (isinstance(chunk[k], str) and not chunk[k].strip()):
                    meta_valid = False
                    logger.warning("chunk_validation_failed_metadata", missing_key=k, drug=chunk.get("drug_name"))
                    break
            if not meta_valid:
                stats["rejected_invalid_metadata"] += 1
                continue
                
            # 5. Check duplicates (content hash per drug & section)
            import hashlib
            content_hash = hashlib.md5(f"{chunk.get('drug_name', '')}_{chunk.get('section', '')}_{content.strip()}".encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                stats["rejected_duplicate"] += 1
                logger.warning("chunk_validation_failed_duplicate", drug=chunk.get("drug_name"), section=section)
                continue
                
            seen_hashes.add(content_hash)
            valid_chunks.append(chunk)
            stats["valid_chunks"] += 1
            
        return valid_chunks, stats
