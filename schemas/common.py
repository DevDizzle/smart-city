"""
VeritAI Smart-City Use Case: Common Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class Evidence(BaseModel):
    """Represents a piece of evidence retrieved from the knowledge base."""
    title: str = Field(..., description="The title of the document.")
    uri: str = Field(..., description="The URI of the document.")
    snippet: str = Field(..., description="A relevant snippet from the document.")
    source: str = Field(..., description="The source of the document (e.g., GCS path).")

class Risk(BaseModel):
    """Represents a potential risk identified by a specialist agent."""
    risk_id: str = Field(..., description="A unique identifier for the risk (e.g., 'RISK-001').")
    description: str = Field(..., description="A description of the risk.")
    severity: str = Field(..., description="The severity of the risk (e.g., 'High', 'Medium', 'Low').")
    mitigation: str = Field(..., description="A suggested mitigation for the risk.")

class Requirement(BaseModel):
    """Represents a requirement that must be met for a project to proceed."""
    req_id: str = Field(..., description="A unique identifier for the requirement (e.g., 'REQ-001').")
    description: str = Field(..., description="A description of the requirement.")
    is_met: bool = Field(False, description="Whether the requirement has been met.")
