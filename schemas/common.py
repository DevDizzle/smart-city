"""
UrbanNexus Smart-City Use Case: Common Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

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

# --- UICII Enhancement Extensions ---

class Zone(BaseModel):
    """Represents the physical deployment zone."""
    zone_id: str = Field(..., description="Unique ID for the zone (e.g., 'campus-core').")
    name: str = Field(..., description="Human-readable name (e.g., 'Engineering Lab Parking').")
    description: str = Field(..., description="Description of the environment.")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs for infrastructure (e.g., {'pole_density': 'high', 'backhaul': 'fiber'}).")
    coordinates: Optional[List[List[float]]] = Field(None, description="Polygon coordinates [[lat, lon], ...].")

class Goal(BaseModel):
    """Represents a strategic objective for the deployment."""
    type: Literal["Safety", "Energy", "Connectivity", "Resilience"]
    description: str = Field(..., description="Specific goal description.")
    priority: Literal["High", "Medium", "Low"]

class Constraint(BaseModel):
    """Represents a limitation or requirement."""
    type: Literal["Budget", "Policy", "Technical", "Privacy"]
    description: str = Field(..., description="Description of the constraint.")
    is_hard_constraint: bool = Field(True, description="If True, cannot be violated.")

class HardwareSpec(BaseModel):
    """Represents a Ubicquia hardware unit."""
    sku: str = Field(..., description="Product SKU or Model (e.g., 'UbiHub AI+').")
    category: Literal["Control", "Hub", "Grid"]
    features: List[str] = Field(..., description="Key features enabled (e.g., ['LPR', 'Public WiFi']).")

class SolutionProposal(BaseModel):
    """Represents a specific deployment recommendation."""
    proposal_id: str = Field(..., description="Unique ID for this proposal.")
    hardware: HardwareSpec
    location_description: str = Field(..., description="Where to deploy (e.g., 'Perimeter poles').")
    value_proposition: str = Field(..., description="Why this adds value (e.g., 'Maximizes energy savings').")
    justification: str = Field(..., description="Reasoning behind the choice.")