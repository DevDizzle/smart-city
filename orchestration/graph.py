"""
VeritAI Smart-City Use Case: Orchestration Graph
"""
import os
import uuid
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from agents.public_safety import PublicSafetySpecialist
from agents.privacy import PrivacyCounsel
from agents.ot_security import OT_SecurityEngineer
from protocol.critic import Critic
from protocol.validator import Validator
from protocol.events import ProtocolEvent
from schemas.decision_brief import DecisionBrief

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def _generate_summary_text(decision_brief: DecisionBrief, trace_id: str) -> str:
    """Generates a human-readable text summary of the decision brief."""
    summary = []
    summary.append("==================================================")
    summary.append("VeritAI Smart-City Decision Brief Summary")
    summary.append("==================================================")
    summary.append(f"Trace ID: {trace_id}")
    summary.append(f"Timestamp: {datetime.utcnow().isoformat()}Z\n")

    summary.append("--------------------------------------------------")
    summary.append("1. Overall Recommendation")
    summary.append("--------------------------------------------------")
    summary.append(f"Decision: {decision_brief.overall_decision}")
    summary.append(f"Confidence: {decision_brief.overall_confidence:.2%}")
    if decision_brief.needs_human_review:
        summary.append(f"HUMAN REVIEW REQUIRED: {decision_brief.human_review_note}")
    summary.append("")

    summary.append("--------------------------------------------------")
    summary.append("2. Combined Risks")
    summary.append("--------------------------------------------------")
    if not decision_brief.combined_risks:
        summary.append("No risks identified.")
    else:
        # Sort risks by severity (High, Medium, Low)
        severity_order = {"High": 0, "Medium": 1, "Low": 2}
        sorted_risks = sorted(decision_brief.combined_risks, key=lambda r: severity_order.get(r.severity, 99))
        for risk in sorted_risks:
            summary.append(f"- ID: {risk.risk_id}")
            summary.append(f"  Severity: {risk.severity}")
            summary.append(f"  Description: {risk.description}")
            summary.append(f"  Mitigation: {risk.mitigation}\n")
    summary.append("")

    summary.append("--------------------------------------------------")
    summary.append("3. Combined Requirements")
    summary.append("--------------------------------------------------")
    if not decision_brief.combined_requirements:
        summary.append("No requirements identified.")
    else:
        for req in decision_brief.combined_requirements:
            summary.append(f"- ID: {req.req_id}")
            summary.append(f"  Description: {req.description}")
            summary.append(f"  Is Met: {'Yes' if req.is_met else 'No'}\n")

    return "\n".join(summary)


def run_workflow(project_brief: dict) -> dict:
    """
    Runs the full multi-agent workflow.
    """
    session_id = str(uuid.uuid4())
    events = []

    def log_event(step: str, agent: str, inputs: dict, outputs: dict, decision: str = None):
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
        logger.info(event.model_dump_json(), extra={"veritai_protocol_event": True})

    # 1. Parallel Specialist Agents
    with ThreadPoolExecutor() as executor:
        public_safety_future = executor.submit(PublicSafetySpecialist().analyze_brief, project_brief)
        privacy_future = executor.submit(PrivacyCounsel().analyze_brief, project_brief)
        ot_security_future = executor.submit(OT_SecurityEngineer().analyze_brief, project_brief)

        public_safety_finding = public_safety_future.result()
        privacy_finding = privacy_future.result()
        ot_security_finding = ot_security_future.result()

    log_event("public_safety", "PublicSafetySpecialist", {"project_brief": project_brief}, public_safety_finding.model_dump())
    log_event("privacy", "PrivacyCounsel", {"project_brief": project_brief}, privacy_finding.model_dump())
    log_event("ot_security", "OT_SecurityEngineer", {"project_brief": project_brief}, ot_security_finding.model_dump())

    # Save each agent's finding to a file
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "public_safety_finding.json"), "w") as f:
        json.dump(public_safety_finding.model_dump(), f, indent=2)
    with open(os.path.join(output_dir, "privacy_finding.json"), "w") as f:
        json.dump(privacy_finding.model_dump(), f, indent=2)
    with open(os.path.join(output_dir, "ot_security_finding.json"), "w") as f:
        json.dump(ot_security_finding.model_dump(), f, indent=2)

    findings = {
        "public_safety": public_safety_finding,
        "privacy": privacy_finding,
        "ot_security": ot_security_finding,
    }

    # 2. Critique and Validate each finding
    critic = Critic()
    validator = Validator()
    validation_results = {}

    for name, finding in findings.items():
        critique_output = critic.critique(finding, project_brief)
        log_event(f"critic_{name}", "Critic", {"finding": finding.model_dump(), "project_brief": project_brief}, critique_output)
        
        validator_output = validator.validate(finding, critique_output, project_brief)
        log_event(f"validator_{name}", "Validator", {"finding": finding.model_dump(), "critique_output": critique_output}, validator_output, validator_output["status"])
        validation_results[name] = validator_output

    # 3. Synthesize Decision
    all_risks = public_safety_finding.risks + privacy_finding.risks + ot_security_finding.risks
    all_reqs = public_safety_finding.requirements + privacy_finding.requirements + ot_security_finding.requirements
    
    overall_decision = "GO"
    if any(v["status"] == "HOLD" for v in validation_results.values()):
        overall_decision = "HOLD"
    elif any(v["status"] == "MITIGATE" for v in validation_results.values()):
        overall_decision = "MITIGATE"

    overall_confidence = min(f.confidence for f in findings.values())

    needs_human_review = False
    human_review_note = None
    if overall_decision == "HOLD":
        needs_human_review = True
        human_review_note = "Project is on hold due to unresolved high risk or missing required controls. Recommend review by legal and public safety stakeholders."
    elif overall_decision == "MITIGATE" and any(r.severity == "High" for r in all_risks):
        needs_human_review = True
        human_review_note = "High severity risks remain under a MITIGATE decision. Recommend review before approval."


    decision_brief = DecisionBrief(
        project_brief=project_brief,
        public_safety=public_safety_finding,
        privacy=privacy_finding,
        ot_security=ot_security_finding,
        combined_risks=all_risks,
        combined_requirements=all_reqs,
        overall_decision=overall_decision,
        overall_confidence=overall_confidence,
        needs_human_review=needs_human_review,
        human_review_note=human_review_note,
    )

    log_event("synthesis", "Synthesizer", {"findings": {k: v.model_dump() for k, v in findings.items()}}, decision_brief.model_dump(), overall_decision)

    # Generate and save human-readable summary
    summary_text = _generate_summary_text(decision_brief, session_id)
    with open(os.path.join(output_dir, "final_recommendation_summary.txt"), "w") as f:
        f.write(summary_text)

    response = decision_brief.model_dump()
    response["trace_id"] = session_id
    response["events"] = [event.model_dump() for event in events]
    return response


def run_workflow_streaming(project_brief: dict):
    """
    Runs the full multi-agent workflow, yielding events as they happen.
    """
    session_id = str(uuid.uuid4())
    output_dir = "agent_outputs"
    os.makedirs(output_dir, exist_ok=True)

    def create_event(step: str, agent: str, inputs: dict, outputs: dict, decision: str = None) -> ProtocolEvent:
        return ProtocolEvent(
            session_id=session_id,
            step=step,
            agent=agent,
            inputs_ref=inputs,
            outputs_ref=outputs,
            timestamp=datetime.utcnow().isoformat(),
            decision_state=decision
        )

    # 1. Parallel Specialist Agents
    with ThreadPoolExecutor() as executor:
        public_safety_future = executor.submit(PublicSafetySpecialist().analyze_brief, project_brief)
        privacy_future = executor.submit(PrivacyCounsel().analyze_brief, project_brief)
        ot_security_future = executor.submit(OT_SecurityEngineer().analyze_brief, project_brief)

        public_safety_finding = public_safety_future.result()
        yield create_event("public_safety", "PublicSafetySpecialist", {"project_brief": project_brief}, public_safety_finding.model_dump())
        with open(os.path.join(output_dir, "public_safety_finding.json"), "w") as f:
            json.dump(public_safety_finding.model_dump(), f, indent=2)

        privacy_finding = privacy_future.result()
        yield create_event("privacy", "PrivacyCounsel", {"project_brief": project_brief}, privacy_finding.model_dump())
        with open(os.path.join(output_dir, "privacy_finding.json"), "w") as f:
            json.dump(privacy_finding.model_dump(), f, indent=2)

        ot_security_finding = ot_security_future.result()
        yield create_event("ot_security", "OT_SecurityEngineer", {"project_brief": project_brief}, ot_security_finding.model_dump())
        with open(os.path.join(output_dir, "ot_security_finding.json"), "w") as f:
            json.dump(ot_security_finding.model_dump(), f, indent=2)

    findings = {
        "public_safety": public_safety_finding,
        "privacy": privacy_finding,
        "ot_security": ot_security_finding,
    }

    # 2. Critique and Validate each finding
    critic = Critic()
    validator = Validator()
    validation_results = {}

    for name, finding in findings.items():
        critique_output = critic.critique(finding, project_brief)
        yield create_event(f"critic_{name}", "Critic", {"finding": finding.model_dump(), "project_brief": project_brief}, critique_output)
        
        validator_output = validator.validate(finding, critique_output, project_brief)
        yield create_event(f"validator_{name}", "Validator", {"finding": finding.model_dump(), "critique_output": critique_output}, validator_output, validator_output["status"])
        validation_results[name] = validator_output

    # 3. Synthesize Decision
    all_risks = public_safety_finding.risks + privacy_finding.risks + ot_security_finding.risks
    all_reqs = public_safety_finding.requirements + privacy_finding.requirements + ot_security_finding.requirements
    
    overall_decision = "GO"
    if any(v["status"] == "HOLD" for v in validation_results.values()):
        overall_decision = "HOLD"
    elif any(v["status"] == "MITIGATE" for v in validation_results.values()):
        overall_decision = "MITIGATE"

    overall_confidence = min(f.confidence for f in findings.values())

    needs_human_review = False
    human_review_note = None
    if overall_decision == "HOLD":
        needs_human_review = True
        human_review_note = "Project is on hold due to unresolved high risk or missing required controls. Recommend review by legal and public safety stakeholders."
    elif overall_decision == "MITIGATE" and any(r.severity == "High" for r in all_risks):
        needs_human_review = True
        human_review_note = "High severity risks remain under a MITIGATE decision. Recommend review before approval."

    decision_brief = DecisionBrief(
        project_brief=project_brief,
        public_safety=public_safety_finding,
        privacy=privacy_finding,
        ot_security=ot_security_finding,
        combined_risks=all_risks,
        combined_requirements=all_reqs,
        overall_decision=overall_decision,
        overall_confidence=overall_confidence,
        needs_human_review=needs_human_review,
        human_review_note=human_review_note,
    )

    yield create_event("synthesis", "Synthesizer", {"findings": {k: v.model_dump() for k, v in findings.items()}}, decision_brief.model_dump(), overall_decision)

    # Generate and save human-readable summary
    summary_text = _generate_summary_text(decision_brief, session_id)
    with open(os.path.join(output_dir, "final_recommendation_summary.txt"), "w") as f:
        f.write(summary_text)
    
    # Yield the final decision brief object itself, including the trace_id
    final_response = decision_brief.model_dump()
    final_response["trace_id"] = session_id
    yield final_response

