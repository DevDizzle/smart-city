"""
UrbanNexus Smart-City Use Case: Decision Brief Schema
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from .public_safety import PublicSafetyFinding
from .privacy import PrivacyFinding
from .ot_security import OTSecurityFinding
from .common import Risk, Requirement, Zone, Goal, Constraint, SolutionProposal

class DecisionBrief(BaseModel):
    """
    Represents the final decision brief, combining findings from all specialists.
    """
    project_brief: dict
    
    # Context (New)
    zone_context: Optional[Zone] = None
    goals: List[Goal] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=list)

    # Risk Analysis (Existing)
    public_safety: Optional[PublicSafetyFinding] = None 
    privacy: Optional[PrivacyFinding] = None
    ot_security: Optional[OTSecurityFinding] = None
    
    # Synthesis
    combined_risks: List[Risk]
    combined_requirements: List[Requirement]
    
    # Output
    final_deployment_plan: List[SolutionProposal] = Field(default_factory=list)
    
    overall_decision: Literal["GO", "MITIGATE", "HOLD"]
    overall_confidence: float
    needs_human_review: bool
    human_review_note: Optional[str]