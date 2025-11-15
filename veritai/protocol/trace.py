"""
Protocol Engineering: Audit Trail System

Every agent action creates an immutable event.
All events form a complete audit trail of the decision process.
Think "airport" -> pass certain requirements 'checkpoints' before proceeding:
check-in -> security -> boarding
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import hashlib


class ProtocolEvent(BaseModel):
    """
    Immutable record of a state transition
    
    Every agent action creates an event that cannot be altered.
    """
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    agent: str = Field(description="Agent that performed the action")
    action: str = Field(description="Action performed")
    input_snapshot: dict = Field(description="State before action")
    output_snapshot: dict = Field(description="State after action")
    rules_applied: List[str] = Field(default_factory=list, description="Rule IDs that fired")
    checkpoint_passed: Optional[str] = Field(None, description="Checkpoint ID if applicable")
    
    class Config:
        frozen = True  # Immutable


class ProtocolTrace(BaseModel):
    """
    Complete audit trail for a VeritAI decision session
    
    Exportable in standard VeritAI-PS format for interoperability.
    """
    trace_id: str = Field(description="Unique trace identifier")
    protocol_version: str = Field(default="VeritAI-PS-1.0")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    proposal: str = Field(description="Original proposal analyzed")
    events: List[ProtocolEvent] = Field(default_factory=list)
    final_recommendation: Optional[str] = None
    
    def add_event(self, event: ProtocolEvent):
        """Add event to trace"""
        self.events.append(event)
    
    def export_standard_format(self) -> dict:
        """
        Export in VeritAI Protocol Standard format
        
        This format is designed for:
        - Cross-system interoperability
        - Compliance reporting
        - External audit tools
        """
        return {
            "protocol": "VeritAI-PS",
            "version": self.protocol_version,
            "trace_id": self.trace_id,
            "created_at": self.created_at,
            "proposal": self.proposal,
            "events": [e.dict() for e in self.events],
            "final_recommendation": self.final_recommendation,
            "verification_hash": self.compute_verification_hash()
        }
    
    def compute_verification_hash(self) -> str:
        """
        Cryptographic hash proving trace integrity
        
        Any tampering with events will change the hash.
        """
        trace_json = json.dumps([e.dict() for e in self.events], sort_keys=True)
        return hashlib.sha256(trace_json.encode()).hexdigest()
    
    def to_json(self, indent: int = 2) -> str:
        """Export as JSON string"""
        return json.dumps(self.export_standard_format(), indent=indent)
    
    class Config:
        arbitrary_types_allowed = True