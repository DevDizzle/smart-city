"""
VeritAI Smart-City Use Case: Decision Brief Schema
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from .public_safety import PublicSafetyFinding
from .privacy import PrivacyFinding
from .ot_security import OTSecurityFinding
from .common import Risk, Requirement

class DecisionBrief(BaseModel):
    """
    Represents the final decision brief, combining findings from all specialists.
    """
    project_brief: dict
    public_safety: PublicSafetyFinding
    privacy: Optional[PrivacyFinding]
    ot_security: Optional[OTSecurityFinding]
    combined_risks: List[Risk]
    combined_requirements: List[Requirement]
    overall_decision: Literal["GO", "MITIGATE", "HOLD"]
    overall_confidence: float
    needs_human_review: bool
    human_review_note: Optional[str]
