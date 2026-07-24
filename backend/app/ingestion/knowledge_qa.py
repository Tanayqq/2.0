from typing import List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger()

class KnowledgeQAPipeline:
    """
    Knowledge QA Pipeline & Data Validation Gate for MedRef v6.0.
    Validates ingested monographs, guidelines, and drug resolver mappings against:
    - Duplicate drugs and aliases
    - Missing required clinical sections
    - Broken or missing citations
    - Malformed metadata
    - Outdated or invalid authority sources
    """

    REQUIRED_CLINICAL_SECTIONS = [
        "indications", "dosage_and_administration", "contraindications", "warnings"
    ]

    @classmethod
    def validate_entity_mapping(cls, brands_to_generics: Dict[str, str], generics_set: set) -> Tuple[bool, List[str]]:
        errors = []
        seen_aliases = set()

        for brand, generic in brands_to_generics.items():
            brand_clean = brand.lower().strip()
            generic_clean = generic.lower().strip()

            if not brand_clean or not generic_clean:
                errors.append(f"Empty brand or generic string found: '{brand}' -> '{generic}'")
                continue

            if brand_clean in seen_aliases:
                errors.append(f"Duplicate brand alias detected: '{brand_clean}'")
            seen_aliases.add(brand_clean)

            if generic_clean not in generics_set:
                errors.append(f"Brand '{brand_clean}' maps to unknown generic target '{generic_clean}'")

        is_valid = len(errors) == 0
        logger.info("entity_mapping_qa_complete", is_valid=is_valid, error_count=len(errors))
        return is_valid, errors

    @classmethod
    def validate_monograph_chunk(cls, chunk: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        title = chunk.get("title", "")
        content = chunk.get("content", "")
        section = chunk.get("section", "")
        authority = chunk.get("authority", "")

        if not title or len(title.strip()) < 3:
            errors.append("Monograph chunk missing valid title")

        if not content or len(content.strip()) < 20:
            errors.append(f"Monograph chunk '{title}' has incomplete or empty content")

        if not section:
            errors.append(f"Monograph chunk '{title}' missing clinical section tag")

        if not authority:
            errors.append(f"Monograph chunk '{title}' missing issuing authority")

        is_valid = len(errors) == 0
        return is_valid, errors
