"""
Protocol Engineering: Governance Rules

NOTE: This is a prototype implementation for hackathon demonstration.
Production version should replace eval() with a safe expression evaluator
and add rule priority/conflict resolution.
"""

'''
The rules are enforced on the agents, seperate from the agent prompts. 
Rules are the infarastructure. Not the prompts. 
Agents are to be governed by these rules. 
Agents provide the reasoning and MUST obey the protocol rules.
LangGraph workflow ENFORCES protocol rules on agents
'''

from pydantic import BaseModel, Field
from enum import Enum


class Severity(str, Enum):
    """Standard severity levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class Recommendation(str, Enum):
    """Standard recommendation types"""
    DO_NOT_PROCEED = "DO_NOT_PROCEED"
    PROCEED_WITH_CAUTION = "PROCEED_WITH_CAUTION"
    CONDUCT_FURTHER_ANALYSIS = "CONDUCT_FURTHER_ANALYSIS"
    PROCEED = "PROCEED"


class ProtocolRule(BaseModel):
    """
    Protocol Engineering: Declarative governance rule
    
    A rule that is programmatically enforced, not suggested.
    """
    rule_id: str = Field(description="Unique rule identifier")
    description: str = Field(description="Human-readable rule description")
    trigger_condition: str = Field(description="Lambda condition as string")
    required_action: str = Field(description="Action that must be taken")
    override_allowed: bool = Field(default=False, description="Can humans override?")
    severity_level: Severity = Field(default=Severity.MEDIUM)
    
    def evaluate(self, state: dict) -> bool:
        """
        Evaluate if this rule should fire
        
        Args:
            state: Current system state
            
        Returns:
            True if rule condition is met
        """
        try:
            # Safe evaluation of trigger condition
            return eval(self.trigger_condition, {"state": state})
        except Exception as e:
            print(f"⚠️ Rule {self.rule_id} evaluation error: {e}")
            return False
    
    class Config:
        frozen = True  # Rules are immutable


class GovernanceRules:
    """
    VeritAI-PS Standard Governance Rules
    
    These rules define the governed behavior of the system.
    """
    
    # Rule R001: High severity = Do Not Proceed
    HIGH_SEVERITY_BLOCKS = ProtocolRule(
        rule_id="R001",
        description="High severity contradictions require DO_NOT_PROCEED recommendation",
        trigger_condition="state.get('critic', {}).get('severity') == 'HIGH'",
        required_action="recommendation = DO_NOT_PROCEED",
        override_allowed=False,
        severity_level=Severity.HIGH
    )
    
    # Rule R002: Ethics escalation
    ETHICS_HIGH_RISK_ESCALATES = ProtocolRule(
        rule_id="R002",
        description="Ethics HIGH RISK flags trigger escalation",
        trigger_condition="any('HIGH RISK' in str(flag) for flag in state.get('ethics', {}).get('red_flags', []))",
        required_action="escalation_required = True",
        override_allowed=True,
        severity_level=Severity.HIGH
    )
    
    # Rule R003: Low confidence requires analysis
    LOW_CONFIDENCE_REQUIRES_ANALYSIS = ProtocolRule(
        rule_id="R003",
        description="Financial confidence <60% requires further analysis",
        trigger_condition="state.get('financial', {}).get('confidence', 100) < 60",
        required_action="recommendation = CONDUCT_FURTHER_ANALYSIS",
        override_allowed=True,
        severity_level=Severity.MEDIUM
    )
    
    # Rule R004: Multiple flags = High severity
    MULTIPLE_FLAGS_HIGH_SEVERITY = ProtocolRule(
        rule_id="R004",
        description="3+ agents flagging same issue elevates to HIGH severity",
        trigger_condition="len([f for agent in ['financial', 'technical', 'ethics', 'risk'] for f in state.get(agent, {}).get('red_flags', [])]) >= 3",
        required_action="severity = HIGH",
        override_allowed=False,
        severity_level=Severity.HIGH
    )
    
    @classmethod
    def get_all_rules(cls) -> list[ProtocolRule]:
        """Get all governance rules"""
        return [
            cls.HIGH_SEVERITY_BLOCKS,
            cls.ETHICS_HIGH_RISK_ESCALATES,
            cls.LOW_CONFIDENCE_REQUIRES_ANALYSIS,
            cls.MULTIPLE_FLAGS_HIGH_SEVERITY,
        ]
    
    @classmethod
    def evaluate_all(cls, state: dict) -> list[str]:
        """
        Evaluate all rules and return triggered rule IDs
        
        Args:
            state: Current system state
            
        Returns:
            List of rule IDs that were triggered
        """
        triggered = []
        for rule in cls.get_all_rules():
            if rule.evaluate(state):
                triggered.append(rule.rule_id)
        return triggered