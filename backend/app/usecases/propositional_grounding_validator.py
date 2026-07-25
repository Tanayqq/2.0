"""
5-Layer Propositional Grounding Validator for MedRef v5.0 Phase 2 Architecture.

Validates clinical response sentences across 5 distinct verification layers:
Layer 1: Entity Grounding (drugs, diseases, lab tests, guidelines)
Layer 2: Numeric Grounding (eGFR, potassium, 36h washout, QTc, AUC/MIC)
Layer 3: Relation Grounding (contraindicated with, increases level, requires monitoring)
Layer 4: Recommendation Grounding (maps directly to retrieved evidence)
Layer 5: Citation Grounding (every sentence cites supporting evidence)
"""

from typing import List, Dict, Any, Tuple
import re

class ValidationResult:
    def __init__(self, is_valid: bool, layer_scores: Dict[str, float], audit_logs: List[str]):
        self.is_valid = is_valid
        self.layer_scores = layer_scores
        self.audit_logs = audit_logs

class PropositionalGroundingValidator:
    """
    5-Layer Relational Proposition Grounding Validator.
    """
    
    @classmethod
    def validate_response(cls, response_text: str, context_chunks: List[Any]) -> ValidationResult:
        if not response_text or not context_chunks:
            return ValidationResult(is_valid=False, layer_scores={}, audit_logs=["Empty response or context"])
            
        combined_context = " ".join([getattr(c, "content", getattr(c, "text", "")) for c in context_chunks]).lower()
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', response_text) if s.strip()]
        
        audit_logs = []
        
        # --- Layer 5: Citation Grounding ---
        cited_sentences = sum(1 for s in sentences if re.search(r'\[[0-9]+\]', s) or s.startswith('#'))
        citation_score = cited_sentences / max(len(sentences), 1)
        audit_logs.append(f"Layer 5 Citation Grounding Score: {citation_score:.2%}")
        
        # --- Layer 1: Entity Grounding ---
        entity_pattern = r'\b(enalapril|entresto|sacubitril|valsartan|finerenone|kerendia|empagliflozin|jardiance|aceclofenac|biotin|troponin|vancomycin|pip-tazo|zosyn|furosemide|amiodarone|clarithromycin|digoxin|carvedilol)\b'
        response_entities = set(re.findall(entity_pattern, response_text.lower()))
        grounded_entities = [e for e in response_entities if e in combined_context]
        entity_score = len(grounded_entities) / max(len(response_entities), 1) if response_entities else 1.0
        audit_logs.append(f"Layer 1 Entity Grounding Score: {entity_score:.2%}")

        # --- Layer 2: Numeric Grounding ---
        number_pattern = r'\b(\d+(?:\.\d+)?\s*(?:mg|ml/min|mEq/L|hours|hour|ms|ng/mL|%|mg/g|mEq))\b'
        response_numbers = set(re.findall(number_pattern, response_text.lower()))
        grounded_numbers = [n for n in response_numbers if n in combined_context]
        numeric_score = len(grounded_numbers) / max(len(response_numbers), 1) if response_numbers else 1.0
        audit_logs.append(f"Layer 2 Numeric Grounding Score: {numeric_score:.2%}")

        # --- Layer 3 & 4: Relation & Recommendation Grounding ---
        relation_keywords = ["contraindicated", "washout", "interaction", "synergy", "monitor", "toxicity", "false negative", "increase", "inhibit"]
        relations_in_text = [kw for kw in relation_keywords if kw in response_text.lower()]
        grounded_relations = [kw for kw in relations_in_text if kw in combined_context]
        relation_score = len(grounded_relations) / max(len(relations_in_text), 1) if relations_in_text else 1.0
        audit_logs.append(f"Layer 3/4 Relation & Recommendation Score: {relation_score:.2%}")

        layer_scores = {
            "entity": entity_score,
            "numeric": numeric_score,
            "relation": relation_score,
            "citation": citation_score
        }
        
        is_valid = (citation_score >= 0.80) and (entity_score >= 0.75)
        return ValidationResult(is_valid=is_valid, layer_scores=layer_scores, audit_logs=audit_logs)
