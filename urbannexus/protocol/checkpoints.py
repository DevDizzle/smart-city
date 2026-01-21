"""
Protocol Engineering: Verification Checkpoints

Checkpoints are gates that agents must pass through.
They enforce quality standards before allowing the workflow to proceed.
"""

from pydantic import BaseModel, Field
from typing import List, Tuple
from .rules import ProtocolRule


class ProtocolCheckpoint(BaseModel):
    """
    Protocol Engineering: Verification Gate
    
    Agents cannot proceed past a checkpoint unless conditions are met.
    """
    checkpoint_id: str = Field(description="Unique checkpoint identifier")
    description: str = Field(description="What this checkpoint verifies")
    required_state_keys: List[str] = Field(description="State keys that must exist")
    validation_rules: List[ProtocolRule] = Field(default_factory=list)
    
    def can_pass(self, state: dict) -> Tuple[bool, List[str]]:
        """
        Check if state can pass through this checkpoint
        
        Args:
            state: Current system state
            
        Returns:
            Tuple of (can_pass, list_of_failure_reasons)
        """
        failures = []
        
        # Check required state exists
        for key in self.required_state_keys:
            if key not in state or state[key] is None:
                failures.append(f"Missing required state: {key}")
        
        # Check validation rules
        for rule in self.validation_rules:
            if not rule.evaluate(state):
                failures.append(f"Failed validation: {rule.description}")
        
        return len(failures) == 0, failures
    
    class Config:
        arbitrary_types_allowed = True


class Checkpoints:
    """UrbanNexus-PS Standard Checkpoints"""
    
    CRITIC_GATE = ProtocolCheckpoint(
        checkpoint_id="CRITIC_GATE",
        description="Ensures all specialist agents have completed before Critic runs",
        required_state_keys=["financial", "technical", "ethics", "risk"],
        validation_rules=[
            ProtocolRule(
                rule_id="CG001",
                description="All specialist findings must have confidence scores",
                trigger_condition="all(state.get(k, {}).get('confidence') is not None for k in ['financial', 'technical', 'ethics', 'risk'])",
                required_action="allow_critic",
                override_allowed=False
            )
        ]
    )
    
    VALIDATOR_GATE = ProtocolCheckpoint(
        checkpoint_id="VALIDATOR_GATE",
        description="Ensures Critic has completed before Validator runs",
        required_state_keys=["financial", "technical", "ethics", "risk", "critic"],
        validation_rules=[
            ProtocolRule(
                rule_id="VG001",
                description="Critic must have assigned severity level",
                trigger_condition="state.get('critic', {}).get('severity') is not None",
                required_action="allow_validation",
                override_allowed=False
            )
        ]
    )
    
    @classmethod
    def get_all_checkpoints(cls) -> list[ProtocolCheckpoint]:
        """Get all defined checkpoints"""
        return [cls.CRITIC_GATE, cls.VALIDATOR_GATE]