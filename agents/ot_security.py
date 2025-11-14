"""
VeritAI Smart-City Use Case: OT Security Engineer Agent
"""
import json
from veritai.llm_client import GeminiClient
from ..rag.vertex_search import search_app, Doc
from ..schemas.common import Evidence, Risk, Requirement
from ..schemas.ot_security import OTSecurityFinding

RISK_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_id": {"type": "string", "description": "Unique identifier (e.g., RISK-OT-001)."},
        "description": {"type": "string", "description": "Summary of the OT security risk."},
        "severity": {"type": "string", "description": "Severity rating (High/Medium/Low)."},
        "mitigation": {"type": "string", "description": "Recommended mitigation."}
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
        "req_id": {"type": "string", "description": "Requirement identifier (e.g., REQ-OT-001)."},
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


class OT_SecurityEngineer:
    """
    A specialist agent that analyzes a project brief for OT security implications.
    """

    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze_brief(self, project_brief: dict) -> OTSecurityFinding:
        """
        Analyzes a project brief for OT security implications.
        """
        vendor_hints = " ".join(project_brief.get("vendor_hints", []))
        query = f"{vendor_hints} security encryption edge smart streetlight OT security best practices network segmentation"

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
        You are an OT Security Engineer reviewing a smart-city deployment. Identify the most
        critical OT/ICS security risks given the project brief and the retrieved evidence.

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
        Using the identified OT security risks, determine the concrete technical requirements
        (controls, safeguards, governance) the city must implement before deployment.

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

        confidence = 0.85 if risks and requirements else 0.4

        return OTSecurityFinding(
            evidence=evidence,
            risks=risks,
            requirements=requirements,
            notes="OT security analysis based on project brief and KB retrieval.",
            confidence=confidence,
        )
