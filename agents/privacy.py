"""
UrbanNexus Smart-City Use Case: Privacy Counsel Agent
"""
import json
from urbannexus.llm_client import GeminiClient
from rag.vertex_search import search_app, Doc
from schemas.common import Evidence, Risk, Requirement
from schemas.privacy import PrivacyFinding

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
        # Construct a detailed query for the knowledge base search
        query = f"""
        Privacy implications of a project with the following characteristics:
        Corridors: {", ".join(project_brief.get("corridors", []))}
        Sensors: {", ".join([sensor for sensor, enabled in project_brief.get("sensors", {}).items() if enabled])}
        Storage: {project_brief.get("storage", "Not specified")}
        Vendor Hints: {", ".join(project_brief.get("vendor_hints", []))}
        """
        
        retrieved_docs: list[Doc] = search_app(query=query, top_k=5)

        evidence = [
            Evidence(
                title=doc.title,
                uri=doc.uri,
                snippet=doc.snippet,
                source=doc.source
            ) for doc in retrieved_docs
        ]

        risks_prompt = f"""
        You are a Privacy Counsel. Your task is to identify potential privacy risks based on a project brief and a set of evidence documents.

        **Project Brief:**
        {json.dumps(project_brief, indent=2)}

        **Evidence Documents:**
        {json.dumps([e.model_dump() for e in evidence], indent=2)}

        **Instructions:**
        1.  Carefully review the project brief and each piece of evidence.
        2.  For each piece of evidence, consider its implications for the project described in the brief, specifically from a privacy perspective.
        3.  Identify potential privacy risks that arise from the project, based on the evidence. A risk is a potential for harm or loss to individuals' privacy.
        4.  For each risk, provide a clear description, a severity level (High, Medium, or Low), and a suggested mitigation.
        5.  If you do not identify any risks, return an empty list.

        Please output a list of risks in JSON format.
        """

        llm_risks_output = self.gemini_client.generate_structured_content(
            risks_prompt, RISK_LIST_SCHEMA
        )
        risks = [Risk(**risk) for risk in llm_risks_output.get("risks", [])] if llm_risks_output else []

        requirements_prompt = f"""
        You are a Privacy Counsel. Your task is to identify necessary privacy requirements based on a project brief, a set of evidence documents, and a list of identified risks.

        **Project Brief:**
        {json.dumps(project_brief, indent=2)}

        **Evidence Documents:**
        {json.dumps([e.model_dump() for e in evidence], indent=2)}

        **Identified Risks:**
        {json.dumps([r.model_dump() for r in risks], indent=2)}

        **Instructions:**
        1.  Carefully review the project brief, the evidence, and the identified risks.
        2.  Based on all of this information, identify any necessary privacy requirements. A requirement is a specific action or control that must be implemented to protect individuals' privacy and ensure compliance with privacy laws and regulations.
        3.  For each requirement, provide a clear description and indicate if it is already met by the project as described in the brief.
        4.  If you do not identify any requirements, return an empty list.

        Please output a list of requirements in JSON format.
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
