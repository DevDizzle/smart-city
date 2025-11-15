"""
VeritAI Protocol Schemas

Data structures for agent communication in the simplified 3-agent architecture.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class CanonicalIntent(str, Enum):
    """Standard intents that agents can perform"""
    ASSESS_COMPREHENSIVE = "assess_comprehensive"
    DETECT_CONTRADICTIONS = "detect_contradictions"
    VALIDATE_COMPLIANCE = "validate_compliance"


class Severity(str, Enum):
    """Severity levels for risks and contradictions"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class Recommendation(str, Enum):
    """Final recommendation types"""
    APPROVE = "APPROVE"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    FURTHER_ANALYSIS = "FURTHER_ANALYSIS"


# ============================================================================
# AGENT 1: SPECIALIST AGENT SCHEMA
# ============================================================================

class SpecialistFinding(BaseModel):
    """
    Output from Specialist Agent
    
    The Specialist analyzes proposals across three dimensions:
    - Financial (ROI, budget, timeline)
    - Risk (security, operational, technical)
    - Ethics (bias, compliance, fairness)
    """
    agent: str = Field(default="Specialist", description="Agent identifier")
    canonical_intent: CanonicalIntent = Field(
        default=CanonicalIntent.ASSESS_COMPREHENSIVE,
        description="What analysis was performed"
    )
    
    # Financial Assessment
    financial_risk: float = Field(
        ge=0.0, le=1.0,
        description="Financial risk score (0=low risk, 1=high risk)"
    )
    financial_concerns: List[str] = Field(
        default_factory=list,
        description="List of financial concerns identified"
    )
    financial_analysis: str = Field(
        description="Detailed financial analysis narrative"
    )
    
    # Risk Assessment
    risk_score: float = Field(
        ge=0.0, le=1.0,
        description="Overall risk score (0=low risk, 1=high risk)"
    )
    risk_concerns: List[str] = Field(
        default_factory=list,
        description="List of operational/security/technical risks"
    )
    risk_analysis: str = Field(
        description="Detailed risk analysis narrative"
    )
    
    # Ethics Assessment
    ethics_risk: float = Field(
        ge=0.0, le=1.0,
        description="Ethics risk score (0=low risk, 1=high risk)"
    )
    ethics_concerns: List[str] = Field(
        default_factory=list,
        description="List of ethical concerns (bias, compliance, fairness)"
    )
    ethics_analysis: str = Field(
        description="Detailed ethics analysis narrative"
    )
    
    # Overall
    overall_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Overall confidence in the analysis (0=low, 1=high)"
    )
    supporting_evidence: List[str] = Field(
        default_factory=list,
        description="Evidence supporting the analysis from RAG context"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent": "Specialist",
                "canonical_intent": "assess_comprehensive",
                "financial_risk": 0.8,
                "financial_concerns": [
                    "Revenue projections assume unrealistic 100% adoption rate",
                    "Break-even timeline conflicts with integration schedule"
                ],
                "financial_analysis": "The proposal projects $12M revenue by Year 3...",
                "risk_score": 0.6,
                "risk_concerns": [
                    "No disaster recovery plan documented",
                    "Single point of failure in architecture"
                ],
                "risk_analysis": "The technical architecture presents moderate risks...",
                "ethics_risk": 0.9,
                "ethics_concerns": [
                    "Training data lacks demographic diversity",
                    "No bias testing protocol defined"
                ],
                "ethics_analysis": "Critical ethical concerns identified...",
                "overall_confidence": 0.75,
                "supporting_evidence": [
                    "Similar healthcare AI projects average 18-month adoption curve",
                    "FDA guidance requires bias monitoring for medical AI"
                ]
            }
        }


# ============================================================================
# AGENT 2: CRITIC AGENT SCHEMA
# ============================================================================

class Contradiction(BaseModel):
    """Individual contradiction detected by Critic"""
    severity: Severity = Field(description="Severity of this contradiction")
    description: str = Field(description="Description of the contradiction")
    evidence: Dict[str, str] = Field(
        description="Evidence from Specialist output showing the contradiction"
    )
    impact: str = Field(description="Impact of this contradiction on the decision")


class CriticFinding(BaseModel):
    """
    Output from Critic Agent
    
    The Critic analyzes Specialist output for:
    - Internal contradictions
    - High-risk indicators
    - Logical inconsistencies
    """
    agent: str = Field(default="Critic", description="Agent identifier")
    canonical_intent: CanonicalIntent = Field(
        default=CanonicalIntent.DETECT_CONTRADICTIONS,
        description="What analysis was performed"
    )
    
    contradictions: List[Contradiction] = Field(
        default_factory=list,
        description="List of contradictions detected"
    )
    
    high_risk_flags: List[str] = Field(
        default_factory=list,
        description="High-risk indicators requiring attention"
    )
    
    overall_severity: Severity = Field(
        description="Overall severity assessment"
    )
    
    analysis: str = Field(
        description="Detailed analysis of contradictions and risks"
    )
    
    recommendation: str = Field(
        description="Critic's recommendation based on findings"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent": "Critic",
                "canonical_intent": "detect_contradictions",
                "contradictions": [
                    {
                        "severity": "HIGH",
                        "description": "Timeline contradiction between financial and risk assessments",
                        "evidence": {
                            "financial": "Revenue starts Month 1, break-even Month 6",
                            "risk": "Integration completes Month 12"
                        },
                        "impact": "Revenue cannot begin before system integration completes"
                    }
                ],
                "high_risk_flags": [
                    "Ethics risk score exceeds 0.8 threshold",
                    "Multiple concerns flagged across all dimensions"
                ],
                "overall_severity": "HIGH",
                "analysis": "Critical contradictions detected that undermine the proposal's viability...",
                "recommendation": "Recommend blocking due to HIGH severity contradictions"
            }
        }


# ============================================================================
# AGENT 3: VALIDATOR AGENT SCHEMA
# ============================================================================

class RuleEvaluation(BaseModel):
    """Evaluation of a single governance rule"""
    rule_id: str = Field(description="Rule identifier (R001-R004)")
    description: str = Field(description="Rule description")
    triggered: bool = Field(description="Whether this rule was triggered")
    triggered_by: Optional[str] = Field(
        None,
        description="What triggered this rule"
    )
    override_allowed: bool = Field(description="Can this rule be overridden?")
    action_required: str = Field(description="Action required by this rule")


class ValidatorDecision(BaseModel):
    """
    Output from Validator Agent (FINAL DECISION)
    
    The Validator:
    - Applies governance rules (R001-R004)
    - Makes final binding recommendation
    - Generates audit trail
    """
    agent: str = Field(default="Validator", description="Agent identifier")
    canonical_intent: CanonicalIntent = Field(
        default=CanonicalIntent.VALIDATE_COMPLIANCE,
        description="What analysis was performed"
    )
    
    final_recommendation: Recommendation = Field(
        description="Final binding recommendation"
    )
    
    rules_triggered: List[str] = Field(
        default_factory=list,
        description="List of rule IDs that were triggered"
    )
    
    rule_evaluations: List[RuleEvaluation] = Field(
        default_factory=list,
        description="Detailed evaluation of each governance rule"
    )
    
    rationale: str = Field(
        description="Detailed rationale for the final decision"
    )
    
    escalation_required: bool = Field(
        default=False,
        description="Whether human escalation is required"
    )
    
    required_actions: List[str] = Field(
        default_factory=list,
        description="Actions required before proposal can be reconsidered"
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in this decision"
    )
    
    estimated_savings: Optional[str] = Field(
        None,
        description="Estimated savings if blocking a bad investment"
    )
    
    audit_trail_hash: str = Field(
        description="Cryptographic hash of complete audit trail"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent": "Validator",
                "canonical_intent": "validate_compliance",
                "final_recommendation": "BLOCK",
                "rules_triggered": ["R001", "R002"],
                "rule_evaluations": [
                    {
                        "rule_id": "R001",
                        "description": "High severity contradictions require DO_NOT_PROCEED",
                        "triggered": True,
                        "triggered_by": "Critic identified HIGH severity timeline contradiction",
                        "override_allowed": False,
                        "action_required": "recommendation = BLOCK"
                    },
                    {
                        "rule_id": "R002",
                        "description": "Ethics HIGH RISK requires escalation",
                        "triggered": True,
                        "triggered_by": "Ethics risk score: 0.9",
                        "override_allowed": True,
                        "action_required": "escalation_required = True"
                    }
                ],
                "rationale": "Governance Rule R001 triggered: HIGH severity contradiction detected between financial projections and technical timeline. This rule cannot be overridden. Additionally, R002 triggered due to ethics risk exceeding 0.8 threshold. Recommend blocking this $15M investment.",
                "escalation_required": True,
                "required_actions": [
                    "Revise financial model with realistic 12-month integration timeline",
                    "Establish bias testing protocol per FDA guidelines",
                    "Conduct security architecture review"
                ],
                "confidence": 0.95,
                "estimated_savings": "$15M investment protected from failure",
                "audit_trail_hash": "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"
            }
        }


# ============================================================================
# WORKFLOW STATE SCHEMA
# ============================================================================

class WorkflowState(BaseModel):
    """
    Complete state that flows through the orchestrator
    
    This tracks the entire decision-making process.
    """
    proposal: str = Field(description="Original proposal text")
    rag_context: Optional[Dict] = Field(
        None,
        description="Context retrieved from RAG pipeline"
    )
    
    # Agent outputs
    specialist: Optional[SpecialistFinding] = None
    critic: Optional[CriticFinding] = None
    validator: Optional[ValidatorDecision] = None
    
    # Workflow metadata
    workflow_started_at: Optional[str] = None
    workflow_completed_at: Optional[str] = None
    total_processing_time_seconds: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True