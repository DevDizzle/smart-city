"""
UrbanNexus Smart-City Use Case: Orchestration Graph (ADK Refactor)
"""
import os
import uuid
import json
import logging
from datetime import datetime
from typing import Generator, Dict, Any, List
from google.genai import types

# ADK
try:
    from google.adk.agents import LlmAgent
    from google.adk.runners import InMemoryRunner
    from google.adk import types
except ImportError:
    logging.error("Google ADK not found. Please install 'google-adk'.")

# Tools
from agents.site_viability import assess_site_tool
from agents.sustainability import analyze_sustainability_tool
from agents.connectivity import analyze_connectivity_tool
from agents.public_safety import assess_public_safety_tool
from agents.privacy import assess_privacy_tool
from agents.ot_security import assess_ot_security_tool

# Protocol
from protocol.events import ProtocolEvent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

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

def run_workflow_streaming(input_context: dict) -> Generator:
    """
    Runs the full multi-agent workflow using ADK.
    """
    session_id = str(uuid.uuid4())
    zone_id = input_context.get("zone_id", "default_zone")
    goals = input_context.get("goals", [])
    
    # 1. Define Agent
    # We use the 'City Planner' supervisor pattern
    planner_agent = LlmAgent(
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
    
    # 2. Setup Runner
    runner = InMemoryRunner(agent=planner_agent)
    
    # Create session (required for InMemoryRunner)
    import asyncio
    asyncio.run(runner.session_service.create_session(session_id=session_id, user_id="user", app_name="InMemoryRunner"))
    
    # 3. Create User Message
    user_msg_text = f"""
    Assess the viability of zone '{zone_id}'.
    
    Strategic Goals:
    {json.dumps(goals, indent=2)}
    """
    user_msg = types.Content(role="user", parts=[types.Part(text=user_msg_text)])
    
    # 4. Run & Adapt Events
    logger.info(f"Starting ADK Workflow for session {session_id}")
    
    try:
        # Adapter Logic
        for event in runner.run(user_id="user", session_id=session_id, new_message=user_msg):
            
            # Map ADK Event to ProtocolEvent for Frontend Compatibility
            # The frontend expects: step, agent, outputs_ref
            
            # Use 'step' to map tool calls to frontend steps
            mapped_event = None
            
            # Debug: Print raw event type
            # logger.info(f"Raw ADK Event: {type(event)}")

            # We need to inspect the event type from google.adk.events
            # But since we are streaming dicts to the API, we can just construct a dict.
            
            event_type = type(event).__name__
            
            if event_type == "ToolCall":
                # A tool is being called. We can map this to "Starting Analysis..." or ignore.
                pass
                
            elif event_type == "ToolOutput":
                # A tool has returned data. THIS is what the frontend wants to see.
                # event.tool_name gives us the tool.
                # event.output gives us the result.
                
                tool_name = getattr(event, "tool_name", "")
                tool_output = getattr(event, "output", {})
                
                # Map Tool Name -> Frontend Step & Agent
                if "assess_site" in tool_name:
                    mapped_event = {
                        "step": "assessment",
                        "agent": "SiteViabilityAgent", 
                        "outputs_ref": tool_output
                    }
                elif "sustainability" in tool_name:
                    mapped_event = {
                        "step": "value_analysis",
                        "agent": "SustainabilitySpecialist",
                        "outputs_ref": {"proposals": tool_output} # Frontend expects 'proposals' list
                    }
                elif "connectivity" in tool_name:
                    mapped_event = {
                        "step": "value_analysis",
                        "agent": "ConnectivitySpecialist",
                        "outputs_ref": {"proposals": tool_output}
                    }
                elif "public_safety" in tool_name:
                    mapped_event = {
                        "step": "risk_analysis",
                        "agent": "PublicSafetySpecialist",
                        "outputs_ref": tool_output # Expects 'risks' list inside
                    }
                elif "privacy" in tool_name:
                    mapped_event = {
                        "step": "risk_analysis",
                        "agent": "PrivacyCounsel",
                        "outputs_ref": tool_output
                    }
                elif "ot_security" in tool_name:
                    mapped_event = {
                        "step": "risk_analysis",
                        "agent": "OT_SecurityEngineer",
                        "outputs_ref": tool_output
                    }

            elif event_type == "ModelResponse":
                # The final text from the model. 
                # We can try to parse the "Decision" from the text or just send it as synthesis.
                text = getattr(event, "text", "")
                
                # Simple heuristic to extract decision from text
                decision = "GO"
                if "MITIGATE" in text.upper():
                    decision = "MITIGATE"
                elif "HOLD" in text.upper():
                    decision = "HOLD"
                
                mapped_event = {
                    "step": "synthesis",
                    "agent": "Synthesizer",
                    "outputs_ref": {"summary": text},
                    "decision_state": decision
                }

            # If we successfully mapped it, yield it wrapped in the standard format
            if mapped_event:
                mapped_event["session_id"] = session_id
                mapped_event["timestamp"] = datetime.utcnow().isoformat()
                mapped_event["inputs_ref"] = {} # Placeholder
                yield mapped_event
            
            # Always yield the raw event for the final result collector (in run_workflow)
            yield event

    except Exception as e:
        logger.error(f"Error during ADK execution: {e}")
        yield {"error": str(e)}

def run_workflow(input_context: dict) -> dict:
    """
    Runs the workflow and returns the final result.
    """
    generator = run_workflow_streaming(input_context)
    final_result = None
    all_events = []
    
    for event in generator:
        all_events.append(event)
        # Identify the final model response
        # In ADK, this is typically the last event or an event with 'text' from the model
        final_result = event
        
    return {"events": all_events, "final_result": final_result}
