"""
QueryPlanner Module for MedRef v5.0 Phase 2 Architecture.

Decomposes complex clinical prompts into targeted sub-queries and emits
selective retrieval constraints (target collections and required sections).
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RetrievalConstraints(BaseModel):
    target_collections: List[str]
    required_sections: List[str]

class SubQuery(BaseModel):
    query_text: str
    target_category: str
    priority: float = 1.0

class QueryPlan(BaseModel):
    original_query: str
    intent_mode: str
    sub_queries: List[SubQuery]
    constraints: RetrievalConstraints

class QueryPlanner:
    """
    Query Decomposition and Retrieval Constraint Generation Engine.
    """
    
    @classmethod
    def create_plan(cls, question: str, mode: str = "DRUG_CHAT") -> QueryPlan:
        q_lower = question.lower()
        sub_queries: List[SubQuery] = []
        
        # 1. Base Sub-Query (original prompt)
        sub_queries.append(SubQuery(query_text=question, target_category="general", priority=1.0))
        
        # 2. Conditional Intent-Based Decomposition (Only for complex prompts)
        complexity_triggers = [
            "adding", "switch", "patient with", "year-old", "yo ", "ckd", "egfr", 
            "creatinine", "uacr", "septic", "shock", "lvef", "afib", "atrial fibrillation",
            "taking", "receiving", "concurrent", "co-administration", "combination"
        ]
        is_complex = any(trigger in q_lower for trigger in complexity_triggers)
        
        if is_complex and mode in ["INTERACTION_CHECK", "PATIENT_SCENARIO"]:
            # Sub-Query for Drug-Drug Interactions & Risks
            sub_queries.append(SubQuery(
                query_text=f"{question} drug interactions adverse risks toxicity",
                target_category="drug_interactions",
                priority=1.2
            ))
            
            # Sub-Query for Guideline Recommendations (GDMT)
            if any(kw in q_lower for kw in ["guideline", "kdigo", "ada", "acc/aha", "esc", "surviving sepsis", "recommendation"]):
                sub_queries.append(SubQuery(
                    query_text=f"{question} clinical guideline recommendations GDMT first line",
                    target_category="disease_guidelines",
                    priority=1.3
                ))
                
            # Sub-Query for Safety, Monitoring & Lab Thresholds
            if any(kw in q_lower for kw in ["egfr", "creatinine", "potassium", "k+", "washout", "qtc", "monitoring", "lab"]):
                sub_queries.append(SubQuery(
                    query_text=f"{question} laboratory thresholds monitoring protocol discontinuation cut-off",
                    target_category="monitoring",
                    priority=1.1
                ))

        elif is_complex and mode == "CLINICAL_GUIDELINE":
            sub_queries.append(SubQuery(
                query_text=f"{question} clinical practice guidelines management consensus",
                target_category="disease_guidelines",
                priority=1.3
            ))

        # 3. Determine Selective Collection Constraints
        from app.usecases.intent_router import IntentRouter
        routed = IntentRouter.route_query(question, mode_override=mode)
        target_cols = routed.get("target_collections", ["openfda_labels", "drug_interactions", "disease_guidelines"])
        
        # Define required sections filter
        if mode == "INTERACTION_CHECK":
            req_sections = ["drug_interactions", "contraindications", "warnings", "boxed_warning"]
        elif mode == "CLINICAL_GUIDELINE":
            req_sections = ["indications", "clinical_guidelines", "disease_guidelines", "dosing"]
        elif mode == "PATIENT_SCENARIO":
            req_sections = ["drug_interactions", "disease_guidelines", "contraindications", "dosage_and_administration", "monitoring"]
        else:
            req_sections = ["indications", "dosage_and_administration", "contraindications", "warnings", "drug_interactions"]

        constraints = RetrievalConstraints(
            target_collections=target_cols,
            required_sections=req_sections
        )
        
        return QueryPlan(
            original_query=question,
            intent_mode=mode,
            sub_queries=sub_queries,
            constraints=constraints
        )
