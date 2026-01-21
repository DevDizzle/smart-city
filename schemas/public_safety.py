"""
UrbanNexus Smart-City Use Case: Public Safety Specialist Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .common import Evidence, Risk, Requirement

class PublicSafetyFinding(BaseModel):
    """
    Represents the findings of the Public Safety Specialist agent.
    """
    topic: str = Field("public_safety", description="The topic of the finding.")
    evidence: List[Evidence] = Field(..., description="A list of evidence supporting the finding.")
    risks: List[Risk] = Field(..., description="A list of risks identified.")
    requirements: List[Requirement] = Field(..., description="A list of requirements that must be met.")
    notes: Optional[str] = Field(None, description="Additional notes from the specialist.")
    confidence: float = Field(..., description="The confidence score of the finding (0.0 to 1.0).")
