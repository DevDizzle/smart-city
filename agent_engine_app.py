"""
UrbanNexus Agent Entry Point for ADK Deployment
"""
import os
import logging
from google.adk.agents import LlmAgent
from google.genai import types

# Import Tools
# Note: These must be importable by the ADK packager. 
# We might need to ensure __init__.py files are present (which they are).
from agents.site_viability import assess_site_tool
from agents.sustainability import analyze_sustainability_tool
from agents.connectivity import analyze_connectivity_tool
from agents.public_safety import assess_public_safety_tool
from agents.privacy import assess_privacy_tool
from agents.ot_security import assess_ot_security_tool

# System Instruction
CITY_PLANNER_INSTRUCTION = """
You are the UrbanNexus City Planner. Your goal is to orchestrate a smart city deployment assessment.

Follow this workflow:
1.  **Assessment:** Assess the site viability using the given Zone ID.
2.  **Value Analysis:** Analyze sustainability and connectivity value using the zone data.
3.  **Risk Analysis:** Analyze Public Safety, Privacy, and OT Security risks. You must construct a 'project brief' based on the assessment and value proposals to pass to these tools.
4.  **Synthesis:** Synthesize all findings into a final decision (GO / MITIGATE / HOLD) and a summary.

Output the final result as a structured JSON summary containing the decision and key findings.
"""

# Define the Root Agent
# This variable name 'root_agent' is standard for ADK but can be anything if specified in CLI.
root_agent = LlmAgent(
    name="city_planner",
    model="gemini-3-flash-preview",
    tools=[
        assess_site_tool,
        analyze_sustainability_tool,
        analyze_connectivity_tool,
        assess_public_safety_tool,
        assess_privacy_tool,
        assess_ot_security_tool
    ],
    instruction=CITY_PLANNER_INSTRUCTION
)
