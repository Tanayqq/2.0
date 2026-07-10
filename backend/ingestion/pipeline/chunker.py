import re
import structlog
from typing import List, Dict, Any
from .interfaces.source_provider import NormalizedMedicalDocument
from .config import ingestion_config

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
        self.target_size = ingestion_config.CHUNK_TARGET_SIZE
        self.max_size = ingestion_config.CHUNK_MAX_SIZE
        self.min_size = ingestion_config.CHUNK_MIN_SIZE
        self.overlap = ingestion_config.CHUNK_OVERLAP

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
        
        # If the entire section fits inside the max size, return it as a single chunk
        if total_tokens <= self.max_size:
            if total_tokens >= self.min_size:
                return [ChunkedSection(section_title, content, 0, total_tokens)]
            return []
            
        # Recursive split hierarchy: double newlines, single newlines, sentences, spaces
        separators = ["\n\n", "\n", ". ", " "]
        splits = self._split_text_recursive(content, separators)
        
        chunk_texts = self._build_chunks_with_overlap(splits)
        
        chunked_sections = []
        for idx, text in enumerate(chunk_texts):
            tokens = self.count_tokens(text)
            if tokens >= self.min_size:
                chunked_sections.append(ChunkedSection(section_title, text, idx, tokens))
                
        return chunked_sections

    def chunk_document(self, doc: NormalizedMedicalDocument) -> List[Dict[str, Any]]:
        """
        Chunks all sections of a document and returns a list of chunk dicts ready for embedding.
        """
        logger.info("chunking_document", drug=doc.drug, sections_count=len(doc.sections))
        
        chunks = []
        for section in doc.sections:
            chunked_secs = self.chunk_section(section.title, section.content)
            for cs in chunked_secs:
                chunks.append({
                    "drug": doc.drug,
                    "generic_name": doc.generic_name,
                    "source": doc.source,
                    "country": doc.country,
                    "version": doc.version,
                    "effective_date": doc.effective_date,
                    "revision": doc.revision,
                    "ingested_at": doc.ingested_at,
                    "section": cs.section_title,
                    "chunk_index": cs.chunk_index,
                    "token_count": cs.token_count,
                    "content": cs.content
                })
                
        logger.info("chunking_completed", drug=doc.drug, chunks_count=len(chunks))
        return chunks
