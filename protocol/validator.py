"""
UrbanNexus Core Protocol: Validator Agent
"""
import json
from urbannexus.llm_client import GeminiClient
from schemas.public_safety import PublicSafetyFinding
from rules.rules import SmartCityRules, ProtocolRule # Assuming this import path for ProtocolRule

# Define JSON schema for Validator's output
VALIDATOR_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["GO", "HOLD", "MITIGATE"], "description": "The final governance status."},
        "reason": {"type": "string", "description": "The detailed reason for the governance status."}
    },
    "required": ["status", "reason"]
}

class Validator:
    """
    The Validator agent checks the findings against governance gates using an LLM.
    """
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.protocol_rules = SmartCityRules.get_all_rules()

    def validate(self, finding: PublicSafetyFinding, critic_output: dict, project_brief: dict) -> dict:
        """
        Validates a finding using an LLM and returns a dictionary with the governance status.
        """
        # Prepare protocol rules for the LLM prompt
        rules_context = "\n".join([
            f"- Rule ID: {rule.rule_id}\n  Description: {rule.description}\n  Required Action: {rule.required_action}\n  Severity: {rule.severity_level.name}"
            for rule in self.protocol_rules
        ])

        validation_prompt = f"""
        You are an AI Validator. Your task is to determine the final governance status (GO, HOLD, MITIGATE)
        for a smart-city project based on the specialist's finding, the critic's output, the project brief,
        and a set of defined protocol rules.

        Project Brief: {json.dumps(project_brief, indent=2)}
        Specialist Finding: {finding.model_dump_json(indent=2)}
        Critic Output: {json.dumps(critic_output, indent=2)}

        Protocol Rules to consider:
        {rules_context}

        Based on all the provided information, especially the protocol rules, determine the governance status.
        If the critic requested a revision, the status must be HOLD.
        If any High severity risks are identified and not mitigated, the status should be MITIGATE.
        If any rule's trigger condition is met and its required action is not addressed, the status should be HOLD or MITIGATE depending on severity.

        Output your validation in JSON format, adhering to the following schema:
        {json.dumps(VALIDATOR_OUTPUT_SCHEMA, indent=2)}
        """

        llm_validation_output = self.gemini_client.generate_structured_content(validation_prompt, VALIDATOR_OUTPUT_SCHEMA)

        if llm_validation_output:
            return llm_validation_output
        else:
            # Fallback in case LLM fails
            return {"status": "HOLD", "reason": "Could not perform validation using LLM."}
