import datetime
from typing import Dict, Any, List, Optional
from ..interfaces.source_provider import NormalizedMedicalDocument, MedicalSection

class OpenFDAAdapter:
    """
    Adapter to convert openFDA raw JSON response to NormalizedMedicalDocument.
    """
    
    # Map openFDA keys to standard clinical section names
    SECTION_KEY_MAP = {
        "indications_and_usage": "Indications",
        "dosage_and_administration": "Dosage",
        "contraindications": "Contraindications",
        "warnings_and_cautions": "Warnings",
        "warnings": "Warnings",
        "precautions": "Precautions",
        "drug_interactions": "Drug Interactions",
        "pregnancy": "Pregnancy",
        "nursing_mothers": "Lactation",
        "pediatric_use": "Pediatric Use",
        "geriatric_use": "Geriatric Use",
        "adverse_reactions": "Adverse Reactions",
        "overdosage": "Overdosage",
        "storage_and_handling": "Storage",
        "patient_counseling_information": "Patient Counseling Information"
    }

    # Metadata keys that should not be parsed as text sections
    METADATA_KEYS = {
        "id", "set_id", "version", "effective_time", "spl_product_data_elements",
        "openfda", "package_label_principal_display_panel", "spl_unclassified_section_table"
    }

    @staticmethod
    def to_normalized(raw_results: Dict[str, Any]) -> Optional[NormalizedMedicalDocument]:
        """
        Normalize raw openFDA result.
        Expects a single result dictionary from openFDA label API response['results'][0].
        """
        if not raw_results:
            return None
            
        openfda_meta = raw_results.get("openfda", {})
        
        # Extract drug name (prefer brand name, fallback to generic name)
        brand_names = openfda_meta.get("brand_name", [])
        drug_name = brand_names[0] if brand_names else ""
        
        generic_names = openfda_meta.get("generic_name", [])
        generic_name = generic_names[0] if generic_names else ""
        
        if not drug_name:
            drug_name = generic_name
            
        # Extract version and version date details
        effective_time = raw_results.get("effective_time", "")
        # Format effective_time (YYYYMMDD) to YYYY-MM-DD
        effective_date = None
        if effective_time and len(effective_time) == 8:
            effective_date = f"{effective_time[:4]}-{effective_time[4:6]}-{effective_time[6:]}"
            
        version = raw_results.get("version", "1")
        set_id = raw_results.get("set_id", "")
        
        sections: List[MedicalSection] = []
        
        # Iterate over all raw keys and extract those that match our target mappings
        for raw_key, value in raw_results.items():
            if raw_key in OpenFDAAdapter.METADATA_KEYS:
                continue
                
            if raw_key in OpenFDAAdapter.SECTION_KEY_MAP:
                section_title = OpenFDAAdapter.SECTION_KEY_MAP[raw_key]
                # openFDA returns sections as lists of strings
                content = ""
                if isinstance(value, list):
                    content = "\n".join(value)
                elif isinstance(value, str):
                    content = value
                
                if content.strip():
                    sections.append(MedicalSection(title=section_title, content=content.strip()))
            elif raw_key.endswith("_table") or raw_key == "openfda":
                # Skip tables or openfda meta
                continue
            else:
                # Preserve unknown sections by converting snake_case key to Title Case
                section_title = raw_key.replace("_", " ").title()
                content = ""
                if isinstance(value, list):
                    content = "\n".join(value)
                elif isinstance(value, str):
                    content = value
                    
                if content.strip():
                    sections.append(MedicalSection(title=section_title, content=content.strip()))

        return NormalizedMedicalDocument(
            drug=drug_name,
            generic_name=generic_name,
            source="openFDA",
            country="US",
            version=version,
            effective_date=effective_date,
            revision=set_id,
            ingested_at=datetime.datetime.utcnow().isoformat() + "Z",
            sections=sections
        )
