from pydantic import BaseModel, ValidationError
from typing import Dict, Any
from schema import (
    NationNode, PersonPoliticianNode, PersonMilitaryNode,
    OrganizationGovtNode, OrganizationCorporateNode, MilitaryAssetNode,
    EventConflictNode, EconomicIndicatorNode, TechnologySectorNode,
    AlliedWithEdge, SanctionedEdge, DeployedAtEdge, InvestedInEdge,
    CriticizedEdge, DependentOnEdge
)

# A mapping to easily validate node types
NODE_SCHEMA_MAP = {
    "Nation": NationNode,
    "Person_Politician": PersonPoliticianNode,
    "Person_Military": PersonMilitaryNode,
    "Organization_Govt": OrganizationGovtNode,
    "Organization_Corporate": OrganizationCorporateNode,
    "Military_Asset": MilitaryAssetNode,
    "Event_Conflict": EventConflictNode,
    "Economic_Indicator": EconomicIndicatorNode,
    "Technology_Sector": TechnologySectorNode,
}

EDGE_SCHEMA_MAP = {
    "ALLIED_WITH": AlliedWithEdge,
    "SANCTIONED": SanctionedEdge,
    "DEPLOYED_AT": DeployedAtEdge,
    "INVESTED_IN": InvestedInEdge,
    "CRITICIZED": CriticizedEdge,
    "DEPENDENT_ON": DependentOnEdge,
}

class TheCritic:
    """
    The Cloud Agentic Verification Loop (Mocked for local execution).
    This deterministic validator enforces the strict ontology constraints.
    """
    
    @staticmethod
    def validate_triple(subject_data: dict, predicate_data: dict, object_data: dict) -> tuple[bool, str]:
        """
        Validates a single extracted triple (Subject, Predicate, Object)
        against the strict Pydantic definitions in schema.py.
        """
        
        # 1. Validate Subject
        subj_type = subject_data.get("type")
        if subj_type not in NODE_SCHEMA_MAP:
            return False, f"Invalid Subject Type: {subj_type}"
            
        try:
            # We mock the UID and Canonical Name for now if it's purely an extraction
            node_args = subject_data.copy()
            if "uid" not in node_args: node_args["uid"] = "temp-uid"
            NODE_SCHEMA_MAP[subj_type](**node_args)
        except ValidationError as e:
            return False, f"Subject Validation Failed: {e}"

        # 2. Validate Object
        obj_type = object_data.get("type")
        if obj_type not in NODE_SCHEMA_MAP:
            return False, f"Invalid Object Type: {obj_type}"
            
        try:
            node_args = object_data.copy()
            if "uid" not in node_args: node_args["uid"] = "temp-uid"
            NODE_SCHEMA_MAP[obj_type](**node_args)
        except ValidationError as e:
            return False, f"Object Validation Failed: {e}"
            
        # 3. Validate Predicate (Edge)
        pred_type = predicate_data.get("type")
        if pred_type not in EDGE_SCHEMA_MAP:
            return False, f"Invalid Predicate Type: {pred_type}"
            
        try:
            EDGE_SCHEMA_MAP[pred_type](**predicate_data)
        except ValidationError as e:
            return False, f"Predicate Validation Failed: {e}"
            
        # Optional: We could add specific semantic checks here, e.g., 
        # A Person_Politician cannot be DEPLOYED_AT a Military_Asset 
        # (Only Military_Asset or Person_Military can).
        if subj_type == "Person_Politician" and pred_type == "DEPLOYED_AT":
            return False, f"Semantic Constraint Violated: {subj_type} cannot be {pred_type}"
            
        return True, "Valid"

    @staticmethod
    def correct_and_discard(correction_prompt: str, original_payload: dict) -> dict | None:
        """
        Simulates routing a failed extraction to the 'Critic' LLM to try and save it.
        If it can't be saved deterministically, it discards it entirely.
        """
        # In a real scenario, this would call Vertex AI.
        print(f"[Critic] Attempting to correct payload due to error: {correction_prompt}")
        
        # Mock logic: if confidence score was missing, inject a default 0.5 to 'save' it.
        # Otherwise, discard.
        if "confidence_score" in correction_prompt:
             print("[Critic] Correction successful. Added default confidence.")
             return "SAVED_PAYLOAD"
        
        print("[Critic] Correction failed. Payload discarded.")
        return None
