import re
import structlog
from typing import List
from .interfaces.source_provider import NormalizedMedicalDocument, MedicalSection
from .config import ingestion_config

logger = structlog.get_logger()

class MedicalParser:
    """
    Parser to clean and standardize section titles and contents.
    Ensures all clinical text sections are properly structured.
    """
    
    # Map synonyms/variations to standard titles
    SECTION_SYNONYMS = {
        "indications and usage": "Indications",
        "dosage and administration": "Dosage",
        "warnings and precautions": "Warnings",
        "warnings & precautions": "Warnings",
        "boxed warning": "Warnings",
        "precautions": "Precautions",
        "drug interactions": "Drug Interactions",
        "pregnancy": "Pregnancy",
        "pregnancy and lactation": "Pregnancy",
        "nursing mothers": "Lactation",
        "lactation": "Lactation",
        "pediatric use": "Pediatric Use",
        "geriatric use": "Geriatric Use",
        "adverse reactions": "Adverse Reactions",
        "side effects": "Adverse Reactions",
        "overdosage": "Overdosage",
        "storage and handling": "Storage",
        "patient counseling information": "Patient Counseling Information"
    }

    def clean_text(self, text: str) -> str:
        """
        Clean whitespace, remove duplicate empty lines, and clean up HTML tags if any.
        """
        if not text:
            return ""
        # Remove any HTML tags that might have leaked
        text = re.sub(r"<[^>]*>", "", text)
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Strip trailing/leading spaces on each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        # Collapse multiple empty lines to a max of two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
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
                
            title_lower = clean_title.lower()
            
            # Standardize section title if it matches a known synonym
            standardized_title = clean_title
            for syn, std in self.SECTION_SYNONYMS.items():
                if syn == title_lower or title_lower.startswith(syn):
                    standardized_title = std
                    break
                    
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
