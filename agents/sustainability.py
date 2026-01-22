"""
UrbanNexus Smart-City Use Case: Sustainability Specialist
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

class SustainabilitySpecialist:
    """
    Advocate agent for Energy and Environmental goals.
    Uses RAG to find Ubicquia products that save energy or reduce clutter.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze(self, zone_context: Zone, goals: List[Goal]) -> List[SolutionProposal]:
        # 1. Retrieval
        query = "Ubicquia UbiCell energy savings and environmental benefits"
        retrieved_docs: list[Doc] = search_app(query=query, top_k=3)
        
        evidence_text = "\n".join([f"- {d.title}: {d.snippet}" for d in retrieved_docs])

        # 2. LLM Reasoning
        prompt = f"""
        You are a Sustainability Specialist for a smart city project.
        Your goal is to propose hardware solutions that maximize energy savings and environmental benefits.
        
        **Zone Context:**
        Name: {zone_context.name}
        Description: {zone_context.description}
        Attributes: {zone_context.attributes}
        
        **Strategic Goals:**
        {', '.join([f'{g.type}: {g.description}' for g in goals])}
        
        **Available Product Intelligence (RAG):**
        {evidence_text}
        
        **Task:**
        Propose deployment of Ubicquia 'UbiCell' controllers if appropriate for this zone (e.g. if it has streetlights).
        Highlight the 40% energy savings.
        Also consider 'UbiHub' if it consolidates devices (reducing clutter), but focus on UbiCell for energy.
        
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

# --- ADK Integration ---
try:
    from google.adk.tools import FunctionTool
    
    _sust_specialist = SustainabilitySpecialist()

    def analyze_sustainability_value(zone_context: dict, goals: List[dict]) -> List[dict]:
        """
        Analyzes the zone and goals to propose sustainability-focused hardware solutions.
        
        Args:
            zone_context: The zone data object/dict.
            goals: List of goal objects/dicts.
        """
        # Convert dicts back to Pydantic if necessary, or let the agent handle it.
        # The agent expects Zone and List[Goal].
        # But for robustness with tool calling, we might receive dicts.
        z = Zone(**zone_context) if isinstance(zone_context, dict) else zone_context
        g = [Goal(**goal) if isinstance(goal, dict) else goal for goal in goals]
        
        results = _sust_specialist.analyze(z, g)
        return [r.model_dump() for r in results]

    analyze_sustainability_tool = FunctionTool(analyze_sustainability_value)

except ImportError:
    pass