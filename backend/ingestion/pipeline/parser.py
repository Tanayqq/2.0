import re
import sys
import os
import structlog
from typing import List
from .interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from .config import ingestion_config

logger = structlog.get_logger()

# Import shared section normalizer from app package
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from app.section_utils import normalize_section
except ImportError:
    # Fallback: inline passthrough if app package not available during standalone runs
    def normalize_section(title: str) -> str:  # type: ignore
        return title.strip().lower() if title else ""

class MedicalParser:
    """
    Parser to clean and standardize section titles and contents.
    Normalizes all section titles to lowercase canonical keys (e.g. 'contraindications',
    'warnings', 'adverse reactions') so that Qdrant metadata is consistent with
    the SECTION_KEYWORDS filter used during retrieval.
    Noise sections (patient package insert, highlights, etc.) are discarded.
    """

    def normalize_section_title(self, title: str) -> str:
        """
        Normalize any section title into a lowercase canonical form using the shared utility.
        """
        return normalize_section(title)

    def clean_text(self, text: str) -> str:
        """
        Clean whitespace, remove duplicate empty lines, clean HTML tags, and resolve OCR/DailyMed artifacts.
        """
        if not text:
            return ""
        # Remove any HTML tags that might have leaked
        text = re.sub(r"<[^>]*>", "", text)
        
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Clean DailyMed/OCR unit artifacts (e.g., "1.73m •", "1.73m•", "1.73m *") to "1.73 m²"
        # Handles various unicode bullets like • (\u2022), · (\u00b7)
        text = re.sub(r'1\.73\s*m\s*[\u2022•·*·\s]*', '1.73 m² ', text)
        
        # Space out bullets at line/phrase starts (e.g. "•Severe" -> "• Severe")
        text = re.sub(r'(^|\s)•(?=\S)', r'\1• ', text)
        
        # Resolve broken line wraps: Join single newlines with a space, preserving double newlines for paragraphs
        paragraphs = text.split("\n\n")
        cleaned_paragraphs = []
        for p in paragraphs:
            # For each paragraph, replace single newlines with spaces and collapse spaces
            cleaned_p = re.sub(r'\s+', ' ', p.replace("\n", " ")).strip()
            if cleaned_p:
                cleaned_paragraphs.append(cleaned_p)
        text = "\n\n".join(cleaned_paragraphs)
        
        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def parse(self, doc: NormalizedMedicalDocument) -> NormalizedMedicalDocument:
        """
        Clean, standardize, and filter document sections.
        """
        logger.info("parsing_document", drug=doc.drug, source=doc.source)
        
        parsed_sections: List[MedicalSection] = []
        seen_titles = set()
        
        for section in doc.sections:
            clean_title = section.title.strip()
            if not clean_title:
                continue
                
            # Normalize to lowercase canonical key (e.g. "4 Contraindications" -> "contraindications")
            standardized_title = normalize_section(clean_title)
            
            # Discard noise sections that pollute retrieval results
            if standardized_title == "_excluded" or not standardized_title:
                logger.debug(
                    "parser_discarding_noise_section",
                    original=clean_title,
                    normalized=standardized_title,
                    drug=doc.drug
                )
                continue
                    
            clean_content = self.clean_text(section.content)
            
            # Discard empty or extremely short/junk sections (< 10 chars)
            if not clean_content or len(clean_content) < 10:
                continue
                
            # Prevent duplicate standard sections (take the first one, or the one with longest content)
            if standardized_title in seen_titles:
                # Find existing section and merge/replace if longer
                for existing_sec in parsed_sections:
                    if existing_sec.title == standardized_title:
                        if len(clean_content) > len(existing_sec.content):
                            existing_sec.content = clean_content
                        break
                continue
                
            parsed_sections.append(MedicalSection(title=standardized_title, content=clean_content))
            seen_titles.add(standardized_title)
            
        doc.sections = parsed_sections
        return doc
