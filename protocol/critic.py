"""
VeritAI Core Protocol: Critic Agent
"""
import json
from veritai.llm_client import GeminiClient
from ..schemas.public_safety import PublicSafetyFinding

# Define JSON schema for Critic's output
CRITIC_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ok", "revise"], "description": "The overall status of the critique."},
        "missing_requirements": {
            "type": "array",
            "items": {"type": "string", "description": "Description of a missing requirement."}
        },
        "notes": {"type": "string", "description": "Detailed notes or issues identified by the critic."}
    },
    "required": ["status", "missing_requirements", "notes"]
}

class Critic:
    """
    The Critic agent checks the findings of specialist agents for completeness and logical soundness.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()

    def critique(self, finding: PublicSafetyFinding, project_brief: dict) -> dict:
        """
        Critiques a finding using an LLM and returns a dictionary with status and issues.
        """
        critique_prompt = f"""
        You are an AI Critic. Your task is to review a specialist agent's finding for a smart-city project.
        Identify any issues, contradictions, logical errors, missing information, or biases.
        Also, check if all necessary requirements are present based on the project brief and finding.

        Project Brief: {json.dumps(project_brief, indent=2)}
        Specialist Finding: {finding.model_dump_json(indent=2)}

        Consider the following aspects:
        - Is there sufficient evidence (at least 3 pieces)?
        - Are risks clearly identified?
        - Is the confidence score reasonable (e.g., above 0.4)?
        - Are there specific requirements for sensors (e.g., CJIS for ALPR, public notice/retention for video/audio)?

        Output your critique in JSON format, adhering to the following schema:
        {json.dumps(CRITIC_OUTPUT_SCHEMA, indent=2)}
        """

        llm_critique_output = self.gemini_client.generate_structured_content(critique_prompt, CRITIC_OUTPUT_SCHEMA)

        if llm_critique_output:
            return llm_critique_output
        else:
            # Fallback in case LLM fails
            return {
                "status": "revise",
                "missing_requirements": ["LLM critique failed."],
                "notes": "Could not generate critique using LLM."
            }

