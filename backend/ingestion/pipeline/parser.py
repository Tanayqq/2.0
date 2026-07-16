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
    Normalizes all section titles to lowercase canonical keys.
    Splits nested subsections (e.g. Renal Impairment, Hepatic Impairment) from parent sections.
    """

    SUBSECTION_PATTERNS = [
        # Renal Impairment
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:patients?\s+with\s+)?(?:acute\s+or\s+chronic\s+)?(renal\s+(?:impairment|insufficiency|dysfunction|failure|function))\b', re.IGNORECASE), "renal_impairment"),
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(adults?\s+with\s+impaired\s+renal\s+function)\b', re.IGNORECASE), "renal_impairment"),
        # Hepatic Impairment
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:patients?\s+with\s+)?(?:acute\s+or\s+chronic\s+)?(hepatic\s+(?:impairment|insufficiency|dysfunction|failure|function))\b', re.IGNORECASE), "hepatic_impairment"),
        # Geriatric Use
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(geriatric(?:s|\s+patients|\s+use)?)\b', re.IGNORECASE), "geriatric_use"),
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(elderly)\b', re.IGNORECASE), "geriatric_use"),
        # Pediatric Use
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(pediatric(?:s|\s+patients|\s+use)?)\b', re.IGNORECASE), "pediatric_use"),
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(children)\b', re.IGNORECASE), "pediatric_use"),
        # Pregnancy
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(pregnancy)\b', re.IGNORECASE), "pregnancy"),
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(females\s+and\s+males\s+of\s+reproductive\s+potential)\b', re.IGNORECASE), "pregnancy"),
        # Lactation
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(?:use\s+in\s+)?(lactation)\b', re.IGNORECASE), "lactation"),
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(nursing\s+mothers)\b', re.IGNORECASE), "lactation"),
        # Patient Counseling
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(patient\s+counseling)\b', re.IGNORECASE), "patient_counseling"),
        # Storage
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(how\s+supplied|storage\s+and\s+handling|storage)\b', re.IGNORECASE), "storage"),
        # Drug Interactions
        (re.compile(r'(?:^|\.\s+|\n+)(?:[•*·\-\s\d.]+)?(drug\s+interactions)\b', re.IGNORECASE), "drug_interactions"),
    ]

    def normalize_section_title(self, title: str) -> str:
        """
        Normalize any section title into a lowercase canonical form using the shared utility.
        """
        return normalize_section(title)

    def clean_text(self, text: str) -> str:
        """
        Clean whitespace, remove duplicate empty lines, clean HTML tags, and resolve DailyMed artifacts.
        """
        if not text:
            return ""
        # Remove any HTML tags that might have leaked
        text = re.sub(r"<[^>]*>", "", text)
        
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Clean DailyMed/OCR unit artifacts
        text = re.sub(r'1\.73\s*m\s*[\u2022•·*·\s]*', '1.73 m² ', text)
        
        # Space out bullets at line/phrase starts
        text = re.sub(r'(^|\s)•(?=\S)', r'\1• ', text)
        
        # Resolve broken line wraps
        paragraphs = text.split("\n\n")
        cleaned_paragraphs = []
        for p in paragraphs:
            cleaned_p = re.sub(r'\s+', ' ', p.replace("\n", " ")).strip()
            if cleaned_p:
                cleaned_paragraphs.append(cleaned_p)
        text = "\n\n".join(cleaned_paragraphs)
        
        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def _split_nested_sections(self, parent_title: str, content: str) -> List[MedicalSection]:
        """
        Scan content paragraph by paragraph and split out nested subsections.
        """
        if parent_title not in [
            "dosage_and_administration",
            "warnings_and_precautions",
            "use_in_specific_populations",
            "precautions",
            "warnings",
            "clinical_pharmacology",
            "adverse_reactions"
        ]:
            return [MedicalSection(title=parent_title, content=content)]

        matches = []
        for pattern, canonical in self.SUBSECTION_PATTERNS:
            for m in pattern.finditer(content):
                # Ensure we only split out the FIRST occurrence of a subsection to avoid splintering the text
                if not any(x[1] == canonical for x in matches):
                    matches.append((m.start(1), canonical))

        if not matches:
            return [MedicalSection(title=parent_title, content=content)]

        matches.sort(key=lambda x: x[0])
        sections = []
        last_idx = 0
        last_title = parent_title

        for start_idx, can in matches:
            sec_content = content[last_idx:start_idx].strip()
            if sec_content:
                # Strip trailing punctuation (like periods or bullets) that belonged to the start of the next section
                sec_content = re.sub(r'[\.\s\-\*•\d]+$', '', sec_content).strip()
                sections.append(MedicalSection(title=last_title, content=sec_content))
            last_idx = start_idx
            last_title = can

        if last_idx < len(content):
            sec_content = content[last_idx:].strip()
            sections.append(MedicalSection(title=last_title, content=sec_content))

        return sections

    def parse(self, doc: NormalizedMedicalDocument) -> NormalizedMedicalDocument:
        """
        Clean, standardize, split, and filter document sections.
        """
        logger.info("parsing_document", drug=doc.drug, source=doc.source)
        
        raw_sections: List[MedicalSection] = []
        
        # First pass: split nested sections
        for section in doc.sections:
            clean_title = section.title.strip()
            if not clean_title:
                continue
                
            standardized_title = normalize_section(clean_title)
            
            if standardized_title == "_excluded" or not standardized_title:
                continue
                
            split_secs = self._split_nested_sections(standardized_title, section.content)
            raw_sections.extend(split_secs)

        parsed_sections: List[MedicalSection] = []
        seen_titles = set()
        
        # Second pass: clean text and deduplicate/merge contents
        for r_sec in raw_sections:
            clean_content = self.clean_text(r_sec.content)
            
            # Discard empty or extremely short sections
            if not clean_content or len(clean_content) < 10:
                continue
                
            if r_sec.title in seen_titles:
                for existing_sec in parsed_sections:
                    if existing_sec.title == r_sec.title:
                        # Merge if not already present
                        if clean_content not in existing_sec.content:
                            existing_sec.content += "\n\n" + clean_content
                        break
                continue
                
            parsed_sections.append(MedicalSection(title=r_sec.title, content=clean_content))
            seen_titles.add(r_sec.title)
            
        doc.sections = parsed_sections
        return doc
