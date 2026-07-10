import datetime
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from ..interfaces.source_provider import NormalizedMedicalDocument, MedicalSection

class DailyMedAdapter:
    """
    Adapter to parse HL7 SPL XML format from DailyMed and convert to NormalizedMedicalDocument.
    """
    
    # Map LOINC codes to standard clinical section names
    LOINC_MAP = {
        "34067-9": "Indications",                  # Indications and Usage
        "34068-7": "Dosage",                       # Dosage and Administration
        "34070-3": "Contraindications",            # Contraindications
        "34066-1": "Warnings",                     # Boxed Warning
        "43685-7": "Warnings",                     # Warnings and Precautions
        "34088-5": "Precautions",                  # Precautions
        "34073-7": "Drug Interactions",            # Drug Interactions
        "34080-2": "Pregnancy",                    # Pregnancy
        "34081-0": "Lactation",                    # Lactation
        "34083-6": "Pediatric Use",                # Pediatric Use
        "34082-8": "Geriatric Use",                # Geriatric Use
        "34084-4": "Adverse Reactions",            # Adverse Reactions
        "34087-7": "Overdosage",                   # Overdosage
        "44425-7": "Storage",                      # Storage and Handling
        "34076-0": "Patient Counseling Information" # Patient Counseling Information
    }

    # XML namespaces for HL7 v3
    NAMESPACES = {"hl7": "urn:hl7-org:v3"}

    @staticmethod
    def _extract_all_text(element: ET.Element) -> str:
        """
        Recursively extract text from an XML element, preserving layout spacing and linebreaks.
        """
        parts = []
        if element.text:
            parts.append(element.text)
            
        for child in element:
            tag_localname = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            
            # Handle linebreaks or paragraph tags by adding newlines
            if tag_localname in ["paragraph", "br", "item"]:
                parts.append("\n")
                
            parts.append(DailyMedAdapter._extract_all_text(child))
            
            if child.tail:
                parts.append(child.tail)
                
        return "".join(parts)

    @staticmethod
    def to_normalized(xml_content: str, drug_name: str) -> Optional[NormalizedMedicalDocument]:
        """
        Parse raw HL7 XML SPL document from DailyMed.
        """
        if not xml_content:
            return None
            
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")
            
        # Get metadata
        # SPL XML has a <setid root="..."/> tag under root
        setid_elem = root.find(".//hl7:setId", DailyMedAdapter.NAMESPACES)
        set_id = setid_elem.attrib.get("root", "") if setid_elem is not None else ""
        
        version_elem = root.find(".//hl7:versionNumber", DailyMedAdapter.NAMESPACES)
        version = version_elem.attrib.get("value", "1") if version_elem is not None else "1"
        
        effective_elem = root.find(".//hl7:effectiveTime", DailyMedAdapter.NAMESPACES)
        effective_time = effective_elem.attrib.get("value", "") if effective_elem is not None else ""
        effective_date = None
        if effective_time and len(effective_time) >= 8:
            effective_date = f"{effective_time[:4]}-{effective_time[4:6]}-{effective_time[6:8]}"
            
        # Extract generic and brand names
        # Usually found in hl7:manufacturedProduct -> hl7:manufacturedMedicine -> hl7:name
        generic_elem = root.find(".//hl7:manufacturedMedicine/hl7:name", DailyMedAdapter.NAMESPACES)
        generic_name = generic_elem.text if generic_elem is not None else drug_name.capitalize()
        
        sections: List[MedicalSection] = []
        
        # Find all <section> elements
        xml_sections = root.findall(".//hl7:section", DailyMedAdapter.NAMESPACES)
        for sec in xml_sections:
            code_elem = sec.find("hl7:code", DailyMedAdapter.NAMESPACES)
            title_elem = sec.find("hl7:title", DailyMedAdapter.NAMESPACES)
            text_elem = sec.find("hl7:text", DailyMedAdapter.NAMESPACES)
            
            if code_elem is not None and text_elem is not None:
                code = code_elem.attrib.get("code", "")
                
                # Retrieve title
                title = title_elem.text if title_elem is not None else ""
                
                # Map LOINC codes to normalized section titles
                if code in DailyMedAdapter.LOINC_MAP:
                    section_title = DailyMedAdapter.LOINC_MAP[code]
                    content = DailyMedAdapter._extract_all_text(text_elem)
                    if content.strip():
                        sections.append(MedicalSection(title=section_title, content=content.strip()))
                elif title:
                    # Capture other/unknown sections that have titles
                    section_title = title.strip().title()
                    content = DailyMedAdapter._extract_all_text(text_elem)
                    if content.strip():
                        sections.append(MedicalSection(title=section_title, content=content.strip()))
                        
        # Deduplicate sections (sometimes sub-components are nested and get parsed twice)
        unique_sections: Dict[str, str] = {}
        for sec in sections:
            # If section title exists, keep the longest content
            if sec.title not in unique_sections or len(sec.content) > len(unique_sections[sec.title]):
                unique_sections[sec.title] = sec.content
                
        final_sections = [MedicalSection(title=k, content=v) for k, v in unique_sections.items()]

        return NormalizedMedicalDocument(
            drug=drug_name.capitalize(),
            generic_name=generic_name,
            source="DailyMed",
            country="US",
            version=version,
            effective_date=effective_date,
            revision=set_id,
            ingested_at=datetime.datetime.utcnow().isoformat() + "Z",
            sections=final_sections
        )
