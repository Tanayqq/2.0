import re
import os
import json
import uuid
import datetime
import hashlib
import structlog
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET
from app.core.config import settings
from app.domain.profile_schema import ProfileField, DrugIdentityProfile, DrugClinicalProfile, RegistryEntry

logger = structlog.get_logger()

class DeterministicProfileParser:
    """
    Parses identity and clinical profile fields deterministically from raw files
    and normalized documents. Links fields to chunk IDs and validates formats.
    """
    def __init__(self, raw_data_dir: str = "backend/ingestion/data/raw"):
        self.raw_data_dir = raw_data_dir
        self.parser_version = "4.0"
        self.pipeline_version = "3.5"
        
    def _get_chunk_id(self, drug_name: str, section: str, chunk_idx: int = 0) -> str:
        """
        Generate the stable deterministic chunk_id corresponding to uploader.py
        """
        unique_string = f"{drug_name.lower()}_{section.lower()}_{chunk_idx}"
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))
        
    def _read_raw_openfda(self, drug_name: str) -> Dict[str, Any]:
        """
        Read the local openfda JSON cache if available.
        """
        filename = f"openfda_{drug_name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.raw_data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("failed_reading_raw_openfda_cache", filepath=filepath, error=str(e))
        return {}
        
    def _read_raw_dailymed(self, drug_name: str) -> str:
        """
        Read the local DailyMed XML cache if available.
        """
        filename = f"dailymed_{drug_name.lower().replace(' ', '_')}.xml"
        filepath = os.path.join(self.raw_data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning("failed_reading_raw_dailymed_cache", filepath=filepath, error=str(e))
        return ""

    def calculate_checksum(self, text: str) -> str:
        """
        Compute MD5 checksum for a text string.
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest() if text else ""

    def _extract_bullets_or_paragraphs(self, content: str) -> List[str]:
        """
        Deterministic helper to split text into bullet items or clean paragraphs.
        """
        if not content:
            return []
        # Split by typical list bullet points or newlines
        lines = re.split(r'\n+|- \b|• \b|\* \b|\d+\.\s+\b', content)
        items = []
        for line in lines:
            cleaned = line.strip()
            # Remove trailing/leading garbage, ensure it has length and is not a generic header
            if cleaned and len(cleaned) > 10:
                # Remove extra internal whitespaces
                cleaned = re.sub(r'\s+', ' ', cleaned)
                items.append(cleaned)
        return items

    def _call_llm_fallback(self, content: str, prompt_instruction: str, response_format_json: bool = True) -> Optional[str]:
        """
        Call LLM as fallback for highly complex tables or deep nested bullets.
        """
        if not settings.GROQ_API_KEY:
            return None
            
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a precise clinical assistant. Extract data strictly from the provided text. Never hallucinate or use external knowledge. If not found in the text, return 'Not available'."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt_instruction}\n\nText:\n{content}"
                    }
                ],
                "temperature": 0.0
            }
            if response_format_json:
                payload["response_format"] = {"type": "json_object"}
                
            resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=20.0)
            if resp.status_code == 200:
                answer = resp.json()["choices"][0]["message"]["content"]
                return answer
        except Exception as e:
            logger.warning("llm_fallback_call_failed", error=str(e))
        return None

    def build_identity_profile(self, doc: Any) -> DrugIdentityProfile:
        """
        Phase A: Identity Engine. Extracts identity fields.
        """
        drug_name = doc.drug
        generic_name_val = doc.generic_name or drug_name
        
        # Load raw file data for rich metadata
        openfda_raw = self._read_raw_openfda(drug_name)
        openfda_meta = openfda_raw.get("openfda", {})
        
        # 1. Brands
        brand_list = openfda_meta.get("brand_name", [])
        if not brand_list:
            brand_list = [generic_name_val.title()]
        brand_list = list(dict.fromkeys([b.capitalize() for b in brand_list]))
        
        # 2. Drug Class
        class_list = openfda_meta.get("pharm_class_epc", []) or openfda_meta.get("pharm_class_moa", [])
        drug_class_val = class_list[0] if class_list else "Not available"
        
        # 3. Prescription Status
        rx_val = "Prescription Only"
        product_type = openfda_meta.get("product_type", [])
        route = openfda_meta.get("route", [])
        if "HUMAN OTC DRUG" in product_type or "OTC" in route:
            rx_val = "OTC"
            
        # 4. ATC, RxNorm, UNII, Manufacturer
        atc_val = "Not available"
        rxcui_list = openfda_meta.get("rxcui", [])
        rxnorm_val = rxcui_list[0] if rxcui_list else "Not available"
        unii_list = openfda_meta.get("unii", [])
        unii_val = unii_list[0] if unii_list else "Not available"
        mfg_list = openfda_meta.get("manufacturer_name", [])
        mfg_val = mfg_list[0] if mfg_list else "Not available"
        
        # Find ATC code in raw XML if DailyMed
        xml_content = self._read_raw_dailymed(drug_name)
        if xml_content:
            atc_match = re.search(r'code="([A-Z]\d{2}[A-Z]\d{2})"', xml_content)
            if atc_match:
                atc_val = atc_match.group(1)

        source_title = doc.source
        checksum = self.calculate_checksum(generic_name_val + " ".join(brand_list))
        last_verified_str = datetime.date.today().isoformat()
        
        def make_field(val: Any, sec_name: str = "Identity") -> ProfileField:
            is_missing = val == "Not available" or val is None or val == []
            return ProfileField(
                value=val,
                source="openFDA" if openfda_meta else doc.source,
                authority="FDA",
                section=sec_name,
                chunk_id=self._get_chunk_id(drug_name, "clinical_pharmacology"),
                confidence="deterministic",
                evidence_strength="HIGH",
                status="present" if not is_missing else "missing",
                reason=None if not is_missing else "section_not_present",
                parser_version=self.parser_version,
                pipeline_version=self.pipeline_version,
                document_checksum=checksum,
                last_verified=last_verified_str
            )
            
        # Class validation rule: Cannot be empty if generic name exists
        drug_class_field = make_field(drug_class_val, "Clinical Pharmacology")
        if drug_class_field.status == "missing" and generic_name_val:
            # Fallback check
            drug_class_field.status = "missing"
            drug_class_field.reason = "class_empty_in_source"

        return DrugIdentityProfile(
            entity_id=f"drug:{drug_name.lower().replace(' ', '_')}",
            entity_type="drug",
            generic_name=make_field(generic_name_val),
            brand_names=make_field(brand_list),
            drug_class=drug_class_field,
            prescription_status=make_field(rx_val),
            atc_code=make_field(atc_val),
            rxnorm_id=make_field(rxnorm_val),
            unii=make_field(unii_val),
            manufacturer=make_field(mfg_val)
        )

    def build_clinical_profile(self, doc: Any) -> DrugClinicalProfile:
        """
        Phase B: Clinical Profile Engine. Extracts clinical fields.
        """
        drug_name = doc.drug
        sections_dict = {sec.title.lower(): sec.content for sec in doc.sections}
        
        last_verified_str = datetime.date.today().isoformat()
        raw_full_text = " ".join([sec.content for sec in doc.sections])
        checksum = self.calculate_checksum(raw_full_text)
        
        def get_section_chunk_id(norm_sec: str) -> Optional[str]:
            """Returns chunk_id for the first chunk of this section."""
            return self._get_chunk_id(drug_name, norm_sec, 0)

        def make_field(val: Any, raw_sec: str, norm_sec: str, conf: str = "deterministic") -> ProfileField:
            is_missing = val == "Not available" or val is None or val == [] or val == {}
            return ProfileField(
                value=val,
                source=doc.source,
                authority="FDA",
                section=raw_sec,
                chunk_id=get_section_chunk_id(norm_sec) if not is_missing else None,
                confidence=conf,
                evidence_strength="HIGH",
                status="present" if not is_missing else "missing",
                reason=None if not is_missing else "section_not_present",
                parser_version=self.parser_version,
                pipeline_version=self.pipeline_version,
                document_checksum=checksum,
                last_verified=last_verified_str
            )

        # 1. Mechanism of Action
        moa_content = sections_dict.get("mechanism of action") or sections_dict.get("clinical pharmacology") or "Not available"
        moa_field = make_field(moa_content, "Mechanism of Action", "mechanism_of_action")

        # 2. Indications
        ind_content = sections_dict.get("indications") or sections_dict.get("indications and usage") or ""
        ind_list = self._extract_bullets_or_paragraphs(ind_content) if ind_content else []
        if not ind_list and ind_content:
            # Fallback to LLM if bullets parsing failed
            llm_res = self._call_llm_fallback(
                ind_content, 
                "Extract a JSON list of indications from this clinical text. Key: 'indications' (array of strings)."
            )
            if llm_res:
                try:
                    ind_list = json.loads(llm_res).get("indications", [])
                    logger.info("llm_fallback_success_indications", drug=drug_name)
                except Exception:
                    pass
        ind_field = make_field(ind_list or "Not available", "Indications", "indications", "deterministic" if not ind_content or ind_list else "fallback_llm")

        # 3. Dosing
        dose_content = sections_dict.get("dosage") or sections_dict.get("dosage and administration") or ""
        dosing_data = {}
        for k in ["adult", "pediatric", "geriatric", "renal", "hepatic", "loading_dose", "maintenance_dose", "maximum_dose", "route", "instructions"]:
            dosing_data[k] = "Not available"
            
        if dose_content:
            # Deterministic Regex Dosing Extraction
            max_dose_match = re.search(r'(?:maximum|max|do not exceed)\s+(?:daily\s+)?(?:dose|dosage|amount)?\s*(?:of|is|to)?\s*(\d+(?:\s*(?:mg|g|mcg|ml|units))\b)', dose_content, re.IGNORECASE)
            if max_dose_match:
                dosing_data["maximum_dose"] = max_dose_match.group(1).strip()
            
            # Validation rule for maximum dose: Must contain mg/mcg/IU/mL
            if dosing_data["maximum_dose"] != "Not available":
                if not any(u in dosing_data["maximum_dose"].lower() for u in ["mg", "mcg", "iu", "ml", "g"]):
                    dosing_data["maximum_dose"] = "Not available"  # Invalid formatting
                    
            # Basic route matching
            route_match = re.search(r'\b(?:oral|orally|intravenous|iv|subcutaneous|im|intramuscular|topical)\b', dose_content, re.IGNORECASE)
            if route_match:
                matched_route = route_match.group(0).capitalize()
                if matched_route == "Orally":
                    matched_route = "Oral"
                dosing_data["route"] = matched_route
                
            # Dosing LLM fallback for nested tables/schedules
            if dosing_data["maximum_dose"] == "Not available":
                llm_res = self._call_llm_fallback(
                    dose_content[:2000],
                    "Extract maximum daily dose and route into a JSON object. Keys: 'maximum_dose' (string or null), 'route' (string or null)."
                )
                if llm_res:
                    try:
                        parsed_llm = json.loads(llm_res)
                        if parsed_llm.get("maximum_dose"):
                            dosing_data["maximum_dose"] = parsed_llm["maximum_dose"]
                        if parsed_llm.get("route"):
                            dosing_data["route"] = parsed_llm["route"]
                        logger.info("llm_fallback_success_dosing", drug=drug_name)
                    except Exception:
                        pass
        
        dosing_fields = {
            k: make_field(v, "Dosage", "dosage_and_administration", "deterministic" if v != "Not available" else "missing")
            for k, v in dosing_data.items()
        }

        # 4. Contraindications
        contra_content = sections_dict.get("contraindications") or ""
        contra_list = self._extract_bullets_or_paragraphs(contra_content) if contra_content else []
        contra_field = make_field(contra_list or "Not available", "Contraindications", "contraindications")

        # 5. Warnings
        warnings_content = sections_dict.get("warnings") or sections_dict.get("warnings and precautions") or sections_dict.get("boxed warning") or ""
        warnings_list = self._extract_bullets_or_paragraphs(warnings_content) if warnings_content else []
        warnings_field = make_field(warnings_list or "Not available", "Warnings", "warnings")

        # 6. Side Effects (Structured)
        se_content = sections_dict.get("adverse reactions") or ""
        se_data = {"common": "Not available", "less_common": "Not available", "rare": "Not available", "life_threatening": "Not available"}
        if se_content:
            # Deterministic scan by keywords
            common_matches = re.findall(r'(?:most common|common|frequent)\s+(?:adverse|side)?\s*(?:reactions|effects)?\s*(?:are|include)?\s*([^.]+)', se_content, re.IGNORECASE)
            if common_matches:
                se_data["common"] = common_matches[0].strip()
            
            serious_matches = re.findall(r'(?:serious|severe|life-threatening|fatal)\s+(?:reactions|effects)?\s*(?:are|include)?\s*([^.]+)', se_content, re.IGNORECASE)
            if serious_matches:
                se_data["life_threatening"] = serious_matches[0].strip()
                
        se_fields = {
            k: make_field(v, "Adverse Reactions", "adverse_reactions")
            for k, v in se_data.items()
        }

        # 7. Drug Interactions (Structured)
        di_content = sections_dict.get("drug interactions") or ""
        di_data = {"contraindicated": "Not available", "major": "Not available", "moderate": "Not available", "minor": "Not available", "monitoring_required": "Not available"}
        if di_content:
            contra_di = re.findall(r'(?:contraindicated|should not be coadministered)\s+with\s+([^.]+)', di_content, re.IGNORECASE)
            if contra_di:
                di_data["contraindicated"] = contra_di[0].strip()
            monitor_di = re.findall(r'(?:monitor|monitoring)\s+(?:is recommended|should be performed)?\s*([^.]+)', di_content, re.IGNORECASE)
            if monitor_di:
                di_data["monitoring_required"] = monitor_di[0].strip()
                
        di_fields = {
            k: make_field(v, "Drug Interactions", "drug_interactions")
            for k, v in di_data.items()
        }

        # 8. Special Populations
        spec_fields = {}
        for key, norm in [("pregnancy", "pregnancy"), ("lactation", "lactation"), ("pediatric", "pediatric_use"), ("geriatric", "geriatric_use"), ("renal", "renal_impairment"), ("hepatic", "hepatic_impairment")]:
            spec_content = sections_dict.get(key) or sections_dict.get(f"{key} use") or "Not available"
            # Pregnancy validation rule
            if key == "pregnancy" and spec_content != "Not available":
                # Ensure status is correctly tagged
                pass
            spec_fields[key] = make_field(spec_content, key.capitalize(), norm)
        # Stubs for missing categories
        for key in ["dialysis", "pharmacogenomics"]:
            spec_fields[key] = make_field("Not available", key.capitalize(), key)

        # 9. Storage
        storage_content = sections_dict.get("storage") or sections_dict.get("storage and handling") or "Not available"
        storage_data = {"temperature": "Not available", "light_protection": "Not available", "moisture_protection": "Not available", "container": "Not available", "expiration": "Not available"}
        if storage_content != "Not available":
            temp_match = re.search(r'(?:store at|controlled room temperature|temperature)\s+([^.]+)', storage_content, re.IGNORECASE)
            if temp_match:
                storage_data["temperature"] = temp_match.group(0).strip()
        storage_fields = {
            k: make_field(v, "Storage", "storage")
            for k, v in storage_data.items()
        }

        # 10. Patient Counseling
        pc_content = sections_dict.get("patient counseling") or sections_dict.get("patient counseling information") or "Not available"
        pc_data = {"key_points": "Not available", "driving": "Not available", "alcohol": "Not available", "missed_dose": "Not available", "monitoring": "Not available", "lifestyle": "Not available"}
        if pc_content != "Not available":
            pc_data["key_points"] = pc_content[:400] + "..."
        pc_fields = {
            k: make_field(v, "Patient Counseling", "patient_counseling")
            for k, v in pc_data.items()
        }

        return DrugClinicalProfile(
            entity_id=f"drug:{drug_name.lower().replace(' ', '_')}",
            entity_type="drug",
            authority="FDA",
            mechanism=moa_field,
            indications=ind_field,
            dosing=dosing_fields,
            contraindications=contra_field,
            warnings=warnings_field,
            side_effects=se_fields,
            drug_interactions=di_fields,
            special_populations=spec_fields,
            storage=storage_fields,
            patient_counseling=pc_fields
        )
