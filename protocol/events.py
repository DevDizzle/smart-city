"""
VeritAI Core Protocol: Event Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ProtocolEvent(BaseModel):
    """
    Represents a single event in the VeritAI protocol.
    """
    session_id: str = Field(..., description="The unique identifier for the entire session.")
    step: str = Field(..., description="The step in the protocol (e.g., 'retrieve', 'public_safety', 'critic').")
    agent: str = Field(..., description="The agent performing the step.")
    inputs_ref: Dict[str, Any] = Field(..., description="A reference to the inputs of the step.")
    outputs_ref: Dict[str, Any] = Field(..., description="A reference to the outputs of the step.")
    timestamp: str = Field(..., description="The ISO 8601 timestamp of the event.")
    decision_state: Optional[str] = Field(None, description="The decision state after the step (GO/MITIGATE/HOLD).")
