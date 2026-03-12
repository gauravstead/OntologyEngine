from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, conlist


class BaseNode(BaseModel):
    uid: str = Field(..., description="UUID of the node")
    canonical_name: str = Field(..., description="Canonical name of the entity")
    aliases: List[str] = Field(default_factory=list, description="Known aliases")
    embedding: Optional[List[float]] = Field(None, description="FAISS Vector embedding")

    class Config:
        populate_by_name = True


# Approved Node Types
class NationNode(BaseNode):
    type: Literal["Nation"] = "Nation"

class PersonPoliticianNode(BaseNode):
    type: Literal["Person_Politician"] = "Person_Politician"

class PersonMilitaryNode(BaseNode):
    type: Literal["Person_Military"] = "Person_Military"

class OrganizationGovtNode(BaseNode):
    type: Literal["Organization_Govt"] = "Organization_Govt"

class OrganizationCorporateNode(BaseNode):
    type: Literal["Organization_Corporate"] = "Organization_Corporate"

class MilitaryAssetNode(BaseNode):
    type: Literal["Military_Asset"] = "Military_Asset"

class EventConflictNode(BaseNode):
    type: Literal["Event_Conflict"] = "Event_Conflict"

class EconomicIndicatorNode(BaseNode):
    type: Literal["Economic_Indicator"] = "Economic_Indicator"

class TechnologySectorNode(BaseNode):
    type: Literal["Technology_Sector"] = "Technology_Sector"


class BaseEdge(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_url: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)


# Approved Edge Types
class AlliedWithEdge(BaseEdge):
    type: Literal["ALLIED_WITH"] = "ALLIED_WITH"

class SanctionedEdge(BaseEdge):
    type: Literal["SANCTIONED"] = "SANCTIONED"

class DeployedAtEdge(BaseEdge):
    type: Literal["DEPLOYED_AT"] = "DEPLOYED_AT"

class InvestedInEdge(BaseEdge):
    type: Literal["INVESTED_IN"] = "INVESTED_IN"

class CriticizedEdge(BaseEdge):
    type: Literal["CRITICIZED"] = "CRITICIZED"

class DependentOnEdge(BaseEdge):
    type: Literal["DEPENDENT_ON"] = "DEPENDENT_ON"
