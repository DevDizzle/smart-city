"""
UrbanNexus Smart-City Use Case: Public Safety Specialist Agent
"""
import json
from urbannexus.llm_client import GeminiClient
from rag.vertex_search import search_app, Doc
from schemas.common import Evidence, Risk, Requirement
from schemas.public_safety import PublicSafetyFinding

# Define JSON schemas for LLM output
RISK_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_id": {"type": "string", "description": "A unique identifier for the risk (e.g., 'RISK-001')."},
        "description": {"type": "string", "description": "A description of the risk."},
        "severity": {"type": "string", "description": "The severity of the risk (e.g., 'High', 'Medium', 'Low')."},
        "mitigation": {"type": "string", "description": "A suggested mitigation for the risk."}
    },
    "required": ["risk_id", "description", "severity", "mitigation"]
}

RISK_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "risks": {
            "type": "array",
            "items": RISK_SCHEMA
        }
    },
    "required": ["risks"]
}

REQUIREMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "req_id": {"type": "string", "description": "A unique identifier for the requirement (e.g., 'REQ-001')."},
        "description": {"type": "string", "description": "A description of the requirement."},
        "is_met": {"type": "boolean", "description": "Whether the requirement has been met."}
    },
    "required": ["req_id", "description", "is_met"]
}

REQUIREMENT_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "requirements": {
            "type": "array",
            "items": REQUIREMENT_SCHEMA
        }
    },
    "required": ["requirements"]
}


class PublicSafetySpecialist:
    """
    A specialist agent that analyzes a project brief for public safety implications.
    """

    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze_brief(self, project_brief: dict) -> PublicSafetyFinding:
        """
        Analyzes a project brief, queries the knowledge base, and returns a
        PublicSafetyFinding.

        Args:
            project_brief: A dictionary containing the project brief.
                Expected keys: "corridors", "sensors", "storage", "vendor_hints".

        Returns:
            A PublicSafetyFinding object.
        """
        # Construct a detailed query for the knowledge base search
        query = f"""
        Public safety implications of a project with the following characteristics:
        Corridors: {", ".join(project_brief.get("corridors", []))}
        Sensors: {", ".join([sensor for sensor, enabled in project_brief.get("sensors", {}).items() if enabled])}
        Storage: {project_brief.get("storage", "Not specified")}
        Vendor Hints: {", ".join(project_brief.get("vendor_hints", []))}
        """
        
        # Search the knowledge base
        retrieved_docs: list[Doc] = search_app(query=query, top_k=5)

        # Convert Docs to Evidence
        evidence = [
            Evidence(
                title=doc.title,
                uri=doc.uri,
                snippet=doc.snippet,
                source=doc.source
            ) for doc in retrieved_docs
        ]

        # Use LLM to identify risks
        risks_prompt = f"""
        You are a public safety specialist. Your task is to identify potential public safety risks based on a project brief and a set of evidence documents.

        **Project Brief:**
        {json.dumps(project_brief, indent=2)}

        **Evidence Documents:**
        {json.dumps([e.model_dump() for e in evidence], indent=2)}

        **Instructions:**
        1.  Carefully review the project brief and each piece of evidence.
        2.  For each piece of evidence, consider its implications for the project described in the brief.
        3.  Identify potential public safety risks that arise from the project, based on the evidence. A risk is a potential for harm or loss.
        4.  For each risk, provide a clear description, a severity level (High, Medium, or Low), and a suggested mitigation.
        5.  If you do not identify any risks, return an empty list.

        Please output a list of risks in JSON format.
        """
        llm_risks_output = self.gemini_client.generate_structured_content(risks_prompt, RISK_LIST_SCHEMA)
        risks = [Risk(**r) for r in llm_risks_output.get("risks", [])] if llm_risks_output else []


        # Use LLM to identify requirements
        requirements_prompt = f"""
        You are a public safety specialist. Your task is to identify necessary public safety requirements based on a project brief, a set of evidence documents, and a list of identified risks.

        **Project Brief:**
        {json.dumps(project_brief, indent=2)}

        **Evidence Documents:**
        {json.dumps([e.model_dump() for e in evidence], indent=2)}

        **Identified Risks:**
        {json.dumps([r.model_dump() for r in risks], indent=2)}

        **Instructions:**
        1.  Carefully review the project brief, the evidence, and the identified risks.
        2.  Based on all of this information, identify any necessary public safety requirements. A requirement is a specific action or control that must be implemented to ensure public safety and compliance.
        3.  For each requirement, provide a clear description and indicate if it is already met by the project as described in the brief.
        4.  If you do not identify any requirements, return an empty list.

        Please output a list of requirements in JSON format.
        """
        llm_requirements_output = self.gemini_client.generate_structured_content(requirements_prompt, REQUIREMENT_LIST_SCHEMA)
        requirements = [Requirement(**r) for r in llm_requirements_output.get("requirements", [])] if llm_requirements_output else []

        # Calculate confidence (dummy logic for now, can be LLM-driven later)
        confidence = 0.85 if risks and requirements else 0.5

        return PublicSafetyFinding(
            evidence=evidence,
            risks=risks,
            requirements=requirements,
            notes="Initial analysis based on project brief, KB retrieval, and LLM reasoning.",
            confidence=confidence,
        )

if __name__ == '__main__':
    # Example Usage
    specialist = PublicSafetySpecialist()
    sample_brief = {
        "corridors": ["A", "B"],
        "sensors": {"alpr": True, "video": True, "audio": False},
        "storage": "cloud",
        "vendor_hints": ["Ubicquia"]
    }
    finding = specialist.analyze_brief(sample_brief)
    print(finding.model_dump_json(indent=2))

# --- ADK Integration ---
try:
    from google.adk.tools import FunctionTool
    
    _ps_specialist = PublicSafetySpecialist()

    def assess_public_safety_risks(project_brief: dict) -> dict:
        """
        Analyzes the project brief for public safety risks and requirements.
        
        Args:
            project_brief: Dict with 'corridors', 'sensors', 'storage', 'vendor_hints'.
        """
        result = _ps_specialist.analyze_brief(project_brief)
        return result.model_dump()

    assess_public_safety_tool = FunctionTool(assess_public_safety_risks)

except ImportError:
    pass


