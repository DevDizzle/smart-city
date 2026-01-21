"""
UrbanNexus Smart-City Use Case: Connectivity Specialist
"""
import uuid
from typing import List
from urbannexus.llm_client import GeminiClient
from rag.vertex_search import search_app, Doc
from schemas.common import Evidence, Zone, Goal, SolutionProposal, HardwareSpec

PROPOSAL_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string"},
                    "category": {"type": "string", "enum": ["Control", "Hub", "Grid"]},
                    "features": {"type": "array", "items": {"type": "string"}},
                    "location_description": {"type": "string"},
                    "value_proposition": {"type": "string"},
                    "justification": {"type": "string"}
                },
                "required": ["sku", "category", "features", "location_description", "value_proposition", "justification"]
            }
        }
    },
    "required": ["proposals"]
}

class ConnectivitySpecialist:
    """
    Advocate agent for Digital Equity and Connectivity goals.
    Uses RAG to find UbiHub capabilities.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze(self, zone_context: Zone, goals: List[Goal]) -> List[SolutionProposal]:
        # 1. Retrieval
        query = "Ubicquia UbiHub WiFi 6 capabilities and digital divide"
        retrieved_docs: list[Doc] = search_app(query=query, top_k=3)
        
        evidence_text = "\n".join([f"- {d.title}: {d.snippet}" for d in retrieved_docs])

        # 2. LLM Reasoning
        prompt = f"""
        You are a Connectivity Specialist for a smart city project.
        Your goal is to propose hardware solutions that improve digital equity and public wifi coverage.
        
        **Zone Context:**
        Name: {zone_context.name}
        Description: {zone_context.description}
        Attributes: {zone_context.attributes}
        
        **Strategic Goals:**
        {', '.join([f'{g.type}: {g.description}' for g in goals])}
        
        **Available Product Intelligence (RAG):**
        {evidence_text}
        
        **Task:**
        Propose deployment of 'UbiHub' (AP6 or AI+) if the zone needs connectivity (e.g. walkways, parking lots).
        Highlight the WiFi 6 features and "Digital Divide" impact.
        
        Return a list of proposals in JSON format.
        """
        
        response = self.gemini_client.generate_structured_content(prompt, PROPOSAL_LIST_SCHEMA)
        
        proposals = []
        if response and "proposals" in response:
            for p in response["proposals"]:
                # Map plain dict to Pydantic models
                hw = HardwareSpec(
                    sku=p["sku"],
                    category=p["category"],
                    features=p["features"]
                )
                proposal = SolutionProposal(
                    proposal_id=str(uuid.uuid4())[:8],
                    hardware=hw,
                    location_description=p["location_description"],
                    value_proposition=p["value_proposition"],
                    justification=p["justification"]
                )
                proposals.append(proposal)
                
        return proposals