"""
UrbanNexus Smart-City Use Case: Orchestration Graph (Refactored for UICII)
"""
import os
import uuid
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Generator

# Agents
from agents.site_viability import SiteViabilityAgent
from agents.sustainability import SustainabilitySpecialist
from agents.connectivity import ConnectivitySpecialist
from agents.public_safety import PublicSafetySpecialist
from agents.privacy import PrivacyCounsel
from agents.ot_security import OT_SecurityEngineer

# Protocol
from protocol.events import ProtocolEvent

# Schemas
from schemas.decision_brief import DecisionBrief
from schemas.common import Zone, Goal, Constraint, SolutionProposal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def _generate_summary_text(decision_brief: DecisionBrief, trace_id: str) -> str:
    """Generates a human-readable text summary of the decision brief."""
    summary = []
    summary.append("==================================================")
    summary.append("UrbanNexus Smart-City Decision Brief Summary")
    summary.append("==================================================")
    summary.append(f"Trace ID: {trace_id}")
    summary.append(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")

    summary.append("--------------------------------------------------")
    summary.append("1. Deployment Recommendation")
    summary.append("--------------------------------------------------")
    summary.append(f"Decision: {decision_brief.overall_decision}")
    summary.append(f"Context: {decision_brief.zone_context.name if decision_brief.zone_context else 'Unknown'}")
    
    if decision_brief.final_deployment_plan:
        summary.append("\nProposed Solutions:")
        for proposal in decision_brief.final_deployment_plan:
            summary.append(f"  * {proposal.hardware.sku} @ {proposal.location_description}")
            summary.append(f"    Value: {proposal.value_proposition}")
    else:
        summary.append("\nNo solutions proposed.")

    summary.append("\n--------------------------------------------------")
    summary.append("2. Risk Analysis")
    summary.append("--------------------------------------------------")
    if not decision_brief.combined_risks:
        summary.append("No significant risks identified.")
    else:
        for risk in decision_brief.combined_risks:
            summary.append(f"- [{risk.severity}] {risk.risk_id}: {risk.description}")
            summary.append(f"  Mitigation: {risk.mitigation}")

    return "\n".join(summary)


def run_workflow(input_context: dict) -> dict:
    """
    Runs the full multi-agent workflow: Assessment -> Value -> Risk -> Synthesis.
    
    Args:
        input_context: Dict containing 'zone_id', 'goals', 'constraints'.
    """
    # Simply consume the streaming generator to get the final result
    generator = run_workflow_streaming(input_context)
    final_result = None
    for event in generator:
        if isinstance(event, dict) and "trace_id" in event:
            final_result = event
    return final_result


def run_workflow_streaming(input_context: dict) -> Generator:
    """
    Runs the full multi-agent workflow, yielding events as they happen.
    """
    session_id = str(uuid.uuid4())
    events = []
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)

    def create_event(step: str, agent: str, inputs: dict, outputs: dict, decision: str = None) -> ProtocolEvent:
        event = ProtocolEvent(
            session_id=session_id,
            step=step,
            agent=agent,
            inputs_ref=inputs,
            outputs_ref=outputs,
            timestamp=datetime.utcnow().isoformat(),
            decision_state=decision
        )
        events.append(event)
        return event

    # Unpack Input
    zone_id = input_context.get("zone_id", "default_zone")
    goals_data = input_context.get("goals", [])
    goals = [Goal(**g) for g in goals_data]

    # ------------------------------------------------------------------
    # Stage 1: Site Assessment
    # ------------------------------------------------------------------
    site_agent = SiteViabilityAgent()
    zone_context = site_agent.run(zone_id)
    
    yield create_event("assessment", "SiteViabilityAgent", {"zone_id": zone_id}, zone_context.model_dump())

    # ------------------------------------------------------------------
    # Stage 2: Value Analysis (Advocates)
    # ------------------------------------------------------------------
    with ThreadPoolExecutor() as executor:
        sust_future = executor.submit(SustainabilitySpecialist().analyze, zone_context, goals)
        conn_future = executor.submit(ConnectivitySpecialist().analyze, zone_context, goals)
        
        sust_proposals = sust_future.result()
        conn_proposals = conn_future.result()

    yield create_event("value_analysis", "SustainabilitySpecialist", {"zone": zone_context.name}, {"proposals": [p.model_dump() for p in sust_proposals]})
    yield create_event("value_analysis", "ConnectivitySpecialist", {"zone": zone_context.name}, {"proposals": [p.model_dump() for p in conn_proposals]})

    all_proposals = sust_proposals + conn_proposals

    # ------------------------------------------------------------------
    # Stage 3: Risk Analysis (Critics)
    # ------------------------------------------------------------------
    # Adapter: Create a "Virtual Project Brief" for the legacy risk agents
    virtual_project_brief = {
        "zone_name": zone_context.name,
        "description": zone_context.description,
        "proposed_hardware": [p.hardware.sku for p in all_proposals],
        "locations": [p.location_description for p in all_proposals],
        "goals": [g.type for g in goals],
        "vendor_hints": ["Ubicquia"] # Legacy hint
    }

    with ThreadPoolExecutor() as executor:
        ps_future = executor.submit(PublicSafetySpecialist().analyze_brief, virtual_project_brief)
        pr_future = executor.submit(PrivacyCounsel().analyze_brief, virtual_project_brief)
        ot_future = executor.submit(OT_SecurityEngineer().analyze_brief, virtual_project_brief)

        public_safety_finding = ps_future.result()
        yield create_event("risk_analysis", "PublicSafetySpecialist", {"brief": "virtual_brief"}, public_safety_finding.model_dump())
        
        privacy_finding = pr_future.result()
        yield create_event("risk_analysis", "PrivacyCounsel", {"brief": "virtual_brief"}, privacy_finding.model_dump())

        ot_security_finding = ot_future.result()
        yield create_event("risk_analysis", "OT_SecurityEngineer", {"brief": "virtual_brief"}, ot_security_finding.model_dump())

    # ------------------------------------------------------------------
    # Stage 4: Synthesis
    # ------------------------------------------------------------------
    all_risks = public_safety_finding.risks + privacy_finding.risks + ot_security_finding.risks
    
    # Simple Decision Logic: If High Risk, MITIGATE
    overall_decision = "GO"
    if any(r.severity == "High" for r in all_risks):
        overall_decision = "MITIGATE"

    decision_brief = DecisionBrief(
        project_brief=virtual_project_brief,
        zone_context=zone_context,
        goals=goals,
        final_deployment_plan=all_proposals,
        public_safety=public_safety_finding,
        privacy=privacy_finding,
        ot_security=ot_security_finding,
        combined_risks=all_risks,
        combined_requirements=[], 
        overall_decision=overall_decision,
        overall_confidence=0.8, 
        needs_human_review=(overall_decision != "GO"),
        human_review_note="High risks detected." if overall_decision != "GO" else None
    )
    
    yield create_event("synthesis", "Synthesizer", {}, decision_brief.model_dump(), overall_decision)

    # Generate and save summary
    summary_text = _generate_summary_text(decision_brief, session_id)
    with open(os.path.join(output_dir, "final_recommendation_summary.txt"), "w") as f:
        f.write(summary_text)

    # Final Return
    final_response = decision_brief.model_dump()
    final_response["trace_id"] = session_id
    final_response["events"] = [event.model_dump() for event in events]
    yield final_response