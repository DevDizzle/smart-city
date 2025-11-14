"""
VeritAI Smart-City Use Case: Orchestration Graph
"""
import uuid
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from ..agents.public_safety import PublicSafetySpecialist
from ..agents.privacy import PrivacyCounsel
from ..agents.ot_security import OT_SecurityEngineer
from ..protocol.critic import Critic
from ..protocol.validator import Validator
from ..protocol.events import ProtocolEvent
from ..schemas.decision_brief import DecisionBrief

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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

    response = decision_brief.model_dump()
    response["trace_id"] = session_id
    response["events"] = [event.model_dump() for event in events]
    return response
