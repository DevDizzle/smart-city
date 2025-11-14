"""
VeritAI Smart-City Use Case: Privacy Counsel Agent
"""
import json
from veritai.llm_client import GeminiClient
from ..rag.vertex_search import search_app, Doc
from ..schemas.common import Evidence, Risk, Requirement
from ..schemas.privacy import PrivacyFinding

RISK_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_id": {"type": "string", "description": "Unique identifier (e.g., RISK-PRIV-001)."},
        "description": {"type": "string", "description": "Summary of the privacy risk."},
        "severity": {"type": "string", "description": "Severity rating (High/Medium/Low)."},
        "mitigation": {"type": "string", "description": "Action to mitigate the risk."}
    },
    "required": ["risk_id", "description", "severity", "mitigation"]
}

RISK_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "risks": {"type": "array", "items": RISK_SCHEMA}
    },
    "required": ["risks"]
}

REQUIREMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "req_id": {"type": "string", "description": "Requirement identifier (e.g., REQ-PRIV-001)."},
        "description": {"type": "string", "description": "Requirement description."},
        "is_met": {"type": "boolean", "description": "Whether requirement currently met."}
    },
    "required": ["req_id", "description", "is_met"]
}

REQUIREMENT_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {"type": "array", "items": REQUIREMENT_SCHEMA}
    },
    "required": ["requirements"]
}

class PrivacyCounsel:
    """
    A specialist agent that analyzes a project brief for privacy implications.
    """

    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze_brief(self, project_brief: dict) -> PrivacyFinding:
        """
        Analyzes a project brief for privacy implications.
        """
        query = "Florida Sunshine Law video surveillance retention public records obligations for camera footage Florida privacy impact assessment public surveillance"
        
        retrieved_docs: list[Doc] = search_app(query=query, top_k=3)

        evidence = [
            Evidence(
                title=doc.title,
                uri=doc.uri,
                snippet=doc.snippet,
                source=doc.source
            ) for doc in retrieved_docs
        ]

        risks_prompt = f"""
        You are acting as the Privacy Counsel for a smart-city deployment. Use the project
        brief and evidence to identify the top privacy compliance risks that city leaders
        must address.

        Project Brief:
        {json.dumps(project_brief, indent=2)}

        Evidence:
        {json.dumps([e.model_dump() for e in evidence], indent=2)}

        Return JSON that follows this schema exactly: {json.dumps(RISK_LIST_SCHEMA)}
        """

        llm_risks_output = self.gemini_client.generate_structured_content(
            risks_prompt, RISK_LIST_SCHEMA
        )
        risks = [Risk(**risk) for risk in llm_risks_output.get("risks", [])] if llm_risks_output else []

        requirements_prompt = f"""
        Based on the project brief and identified privacy risks, enumerate enforceable privacy
        requirements (e.g., policy, legal, governance controls) that the deployment must meet.

        Project Brief:
        {json.dumps(project_brief, indent=2)}

        Risks:
        {json.dumps([r.model_dump() for r in risks], indent=2)}

        Return JSON that follows this schema exactly: {json.dumps(REQUIREMENT_LIST_SCHEMA)}
        """

        llm_requirements_output = self.gemini_client.generate_structured_content(
            requirements_prompt, REQUIREMENT_LIST_SCHEMA
        )
        requirements = [
            Requirement(**req) for req in llm_requirements_output.get("requirements", [])
        ] if llm_requirements_output else []

        confidence = 0.9 if risks and requirements else 0.5

        return PrivacyFinding(
            evidence=evidence,
            risks=risks,
            requirements=requirements,
            notes="Privacy analysis based on project brief and KB retrieval.",
            confidence=confidence,
        )
