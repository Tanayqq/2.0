import re
import sys
import os
import structlog
from typing import List, Dict, Any
from .interfaces.source_provider import NormalizedMedicalDocument
from .config import ingestion_config

try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from app.section_utils import get_clinical_category, get_patient_population
except ImportError:
    def get_clinical_category(sec: str) -> str:
        return "Clinical Overview"
    def get_patient_population(sec: str) -> str:
        return "general"

logger = structlog.get_logger()

class ChunkedSection:
    def __init__(self, section_title: str, content: str, chunk_index: int, token_count: int):
        self.section_title = section_title
        self.content = content
        self.chunk_index = chunk_index
        self.token_count = token_count

class MedicalSectionChunker:
    """
    Intelligent section-based chunker.
    Chunks medical documents by clinical section rather than fixed token length.
    Recursively splits oversized sections using paragraph/sentence boundaries with overlap.
    """
    def __init__(self):
        self.target_size = ingestion_config.TARGET_CHUNK_TOKENS
        self.max_size = ingestion_config.MAX_CHUNK_TOKENS
        self.min_size = ingestion_config.MIN_CHUNK_TOKENS
        self.overlap = ingestion_config.OVERLAP

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count based on word count (1 word ≈ 1.3 tokens).
        """
        if not text:
            return 0
        words = text.split()
        return int(len(words) * 1.3)

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """
        Splits text recursively using a list of separators.
        """
        if not separators:
            # Word-level fallback if we run out of separators
            return text.split(" ")
            
        separator = separators[0]
        next_separators = separators[1:]
        
        # Split by separator
        if separator == "\n\n":
            splits = text.split("\n\n")
        elif separator == "\n":
            splits = text.split("\n")
        elif separator == ". ":
            splits = text.split(". ")
            # Restore period after split
            splits = [s + "." for s in splits if s]
        elif separator == " ":
            splits = text.split(" ")
        else:
            splits = [text]
            
        final_splits = []
        for split in splits:
            split = split.strip()
            if not split:
                continue
            if self.count_tokens(split) <= self.max_size:
                final_splits.append(split)
            else:
                # Recurse with next separator
                final_splits.extend(self._split_text_recursive(split, next_separators))
                
        return final_splits

    def _build_chunks_with_overlap(self, splits: List[str]) -> List[str]:
        """
        Assembles splits into chunks near target_size, incorporating overlap if split.
        """
        chunks = []
        current_chunk = []
        
        for split in splits:
            # Check size of the combined chunk candidate
            combined_candidate = " ".join(current_chunk + [split])
            candidate_tokens = self.count_tokens(combined_candidate)
            
            # If adding this split exceeds max_size, save the current chunk
            if current_chunk and (candidate_tokens > self.max_size):
                chunks.append(" ".join(current_chunk))
                
                # Apply overlap: keep last elements of current chunk that fit within overlap limit
                overlap_chunk = []
                for item in reversed(current_chunk):
                    # Check if adding this item from the end fits in overlap
                    potential_overlap = [item] + overlap_chunk
                    if self.count_tokens(" ".join(potential_overlap)) <= self.overlap:
                        overlap_chunk.insert(0, item)
                    else:
                        break
                current_chunk = overlap_chunk
                
            current_chunk.append(split)
            
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        # Clean up chunk text
        return [c.strip() for c in chunks if c.strip()]

    def chunk_section(self, section_title: str, content: str) -> List[ChunkedSection]:
        """
        Chunk a single section.
        """
        content = content.strip()
        total_tokens = self.count_tokens(content)
        
        # Determine effective minimum size: bypass/reduce for critical clinical sections
        effective_min_size = self.min_size
        critical_sections = {
            "pregnancy", "lactation", "pediatric_use", "geriatric_use", 
            "renal_impairment", "hepatic_impairment", "contraindications", 
            "warnings", "precautions"
        }
        if section_title.lower() in critical_sections:
            effective_min_size = 5  # Allow very short warnings/lists
            
        # If the entire section fits inside the max size, return it as a single chunk
        if total_tokens <= self.max_size:
            if total_tokens >= effective_min_size:
                return [ChunkedSection(section_title, content, 0, total_tokens)]
            return []
            
        # Recursive split hierarchy: double newlines, single newlines, sentences, spaces
        separators = ["\n\n", "\n", ". ", " "]
        splits = self._split_text_recursive(content, separators)
        
        chunk_texts = self._build_chunks_with_overlap(splits)
        
        chunked_sections = []
        for idx, text in enumerate(chunk_texts):
            tokens = self.count_tokens(text)
            chunked_sections.append(ChunkedSection(section_title, text, idx, tokens))
            
        # Merging pass for short chunks (< 15 tokens) within the same section
        if len(chunked_sections) > 1:
            merged_sections = []
            for cs in chunked_sections:
                if cs.token_count < 15:
                    if merged_sections:
                        prev = merged_sections[-1]
                        prev.content += f"\n\n{cs.content}"
                        prev.token_count = self.count_tokens(prev.content)
                    else:
                        merged_sections.append(cs)
                else:
                    if merged_sections and merged_sections[-1].token_count < 15:
                        short_chunk = merged_sections.pop()
                        cs.content = f"{short_chunk.content}\n\n{cs.content}"
                        cs.token_count = self.count_tokens(cs.content)
                    merged_sections.append(cs)
            # Re-index chunks
            for i, cs in enumerate(merged_sections):
                cs.chunk_index = i
            return [c for c in merged_sections if c.token_count >= effective_min_size]
        else:
            return [c for c in chunked_sections if c.token_count >= effective_min_size]

    def _extract_structured_dosing(self, content: str, section: str) -> dict:
        """
        Parses structured dosing facts from text where available in dosage or strength sections.
        """
        dosing = {}
        if section not in ["dosage_and_administration", "maximum_dose", "strengths"]:
            return dosing
        
        # Search for maximum dose patterns
        max_dose_match = re.search(r'(?:maximum|max|do not exceed)\s+(?:daily\s+)?(?:dose|dosage|amount)?\s*(?:of|is|to)?\s*(\d+(?:\s*(?:mg|g|mcg|ml|units))\b)', content, re.IGNORECASE)
        if max_dose_match:
            dosing["maximum_dose"] = max_dose_match.group(1).strip()
            
        # Search for strengths/concentrations
        strength_matches = re.findall(r'\b(\d+(?:\s*(?:mg|g|mcg|ml))\b)', content, re.IGNORECASE)
        if strength_matches:
            dosing["strengths"] = list(dict.fromkeys(strength_matches))
            
        return dosing

    def chunk_document(self, doc: NormalizedMedicalDocument) -> List[Dict[str, Any]]:
        """
        Chunks all sections of a document and returns a list of chunk dicts ready for embedding.
        Each chunk carries: chunk_hash (SHA256 for integrity), ingestion versioning,
        source traceability fields, and authority chain metadata.
        """
        import hashlib
        import datetime
        logger.info("chunking_document", drug=doc.drug, sections_count=len(doc.sections))
        
        temp_chunks = []
        for section in doc.sections:
            chunked_secs = self.chunk_section(section.title, section.content)
            for cs in chunked_secs:
                temp_chunks.append(cs)
                
        # Generate stub chunks for missing sections to prevent cross-contamination in direct searches
        expected_sections = {
            "indications", "dosage_and_administration", "contraindications",
            "warnings", "precautions", "drug_interactions", "pregnancy",
            "lactation", "pediatric_use", "geriatric_use", "renal_impairment",
            "hepatic_impairment", "storage", "patient_counseling"
        }
        present_sections = {sec.title.lower() for sec in doc.sections}
        missing_sections = expected_sections - present_sections
        
        for missing in missing_sections:
            clean_missing = missing.replace("_", " ").title()
            stub_content = f"No specific instructions, data, or warnings regarding {clean_missing} are provided in the official FDA label for {doc.drug}."
            tokens = int(len(stub_content.split()) * 1.3)
            temp_chunks.append(ChunkedSection(missing, stub_content, 0, tokens))
                
        total_chunks = len(temp_chunks)
        chunks = []
        
        # Authority resolution — use doc.authority if populated by provider, else infer
        if doc.authority:
            authority = doc.authority
        else:
            source_lower = doc.source.lower()
            if "openfda" in source_lower:
                authority = "FDA"
            elif "dailymed" in source_lower:
                authority = "DailyMed"
            else:
                authority = doc.source

        # Resolve brands/aliases for this drug to embed them in vector space
        from app.usecases.drug_resolver import DrugNameResolver
        generic_to_brands = {}
        for brand, gen in DrugNameResolver.BRAND_TO_GENERIC.items():
            generic_to_brands.setdefault(gen.lower(), []).append(brand.title())
            
        lookup_names = [doc.drug.lower(), doc.generic_name.lower()]
        brands = []
        for name in lookup_names:
            if name in generic_to_brands:
                brands.extend(generic_to_brands[name])
        if doc.synonyms:
            brands.extend([s.title() for s in doc.synonyms])
        brands = list(dict.fromkeys(brands))

        for idx, cs in enumerate(temp_chunks):
            clean_title = cs.section_title.replace("_", " ").title()
            brand_str = f" ({', '.join(brands)})" if brands else ""
            content_with_context = f"Drug: {doc.drug}{brand_str} | Section: {clean_title} | {cs.content}"

            # SHA256 hash of content for integrity verification and deduplication
            chunk_hash = hashlib.sha256(content_with_context.encode("utf-8")).hexdigest()
            
            # Extract structured dosing
            structured_dosing = self._extract_structured_dosing(cs.content, cs.section_title)

            chunks.append({
                # Core identity
                "drug_name": doc.drug,
                "generic_name": doc.generic_name,
                "section": cs.section_title,
                "canonical_section": cs.section_title,
                "content": content_with_context,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "token_count": cs.token_count,
                
                # Source traceability (Refinement #9)
                "source": doc.source,
                "source_url": doc.source_url,
                "document_id": doc.revision,
                "label_version": doc.version,
                "retrieved_on": doc.retrieved_on,
                
                # Authority chain (Refinement #2)
                "authority": authority,
                "authority_version": doc.authority_version or doc.effective_date,
                
                # Version history (Refinement #2)
                "drug_revision": doc.drug_revision or doc.revision,
                "effective_date": doc.effective_date,
                "revision": doc.revision,
                
                # Ingestion versioning (Refinement #5)
                "pipeline_version": ingestion_config.PIPELINE_VERSION,
                "corpus_version": ingestion_config.CORPUS_VERSION,
                "parser_version": "2.1.0",
                "embedding_model": ingestion_config.EMBEDDING_MODEL_NAME,
                "ingested_at": doc.ingested_at,
                "embedded_at": None,           # Filled by embedder after embedding
                
                # Integrity & provenance
                "chunk_hash": chunk_hash,
                "paragraph_index": cs.chunk_index,
                "xml_section": None,  # For strict provenance mapping later
                
                # Clinical classification
                "clinical_category": get_clinical_category(cs.section_title),
                "patient_population": get_patient_population(cs.section_title),
                "document_type": "drug_label",
                "structured_dosing": structured_dosing,
            })
                
        logger.info("chunking_completed", drug=doc.drug, chunks_count=len(chunks))
        return chunks

