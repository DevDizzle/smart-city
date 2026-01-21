"""
UrbanNexus Smart-City Use Case: FastAPI API (V2 Updated)
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any

from orchestration.graph import run_workflow, run_workflow_streaming
from rag.vertex_search import search_app
from protocol.events import ProtocolEvent
from fastapi.middleware.cors import CORSMiddleware
from schemas.decision_brief import DecisionBrief
from schemas.common import Zone, Goal, Constraint
from utils.firestore_sanitizer import sanitize_for_firestore

app = FastAPI(
    title="UrbanNexus Smart-City API",
    description="API for the UrbanNexus Smart-City use case (V2 capable).",
    version="0.2.0",
)

# Initialize Firestore client
from google.cloud import firestore
from google.auth.exceptions import DefaultCredentialsError

try:
    db = firestore.Client()
except DefaultCredentialsError:
    db = None
    print("Firestore credentials not configured; trace persistence is disabled.")

# CORS Middleware
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- V2 Models ---

class AnalysisRequest(BaseModel):
    """V2 Input Context Request."""
    zone_id: str
    goals: List[Goal]
    constraints: List[Constraint] = []

# --- Helper: Load Mock Data ---

def load_mock_zones():
    path = "data/mock_zones.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"zones": []}

MOCK_ZONES_DB = load_mock_zones()


# --- Endpoints ---

@app.get("/zones", summary="Get Available Demo Zones")
def get_zones():
    """Returns the list of mock zones for the frontend map."""
    return MOCK_ZONES_DB

@app.get("/kb/health", summary="Knowledge Base Health Check")
def kb_health():
    """
    Performs a health check on the Knowledge Base by running a sample query.
    """
    try:
        results = search_app(query="Sunshine Law video retention", top_k=3)
        if results:
            return {"status": "ok", "results": results}
        else:
            return {"status": "error", "message": "No results returned from KB."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/analyze/v2", summary="Analyze Zone (V2 Streaming)")
async def analyze_v2(request: AnalysisRequest):
    """
    V2 Analysis: Takes Zone ID + Goals, runs the 4-stage pipeline, and streams events.
    """
    # Convert Pydantic model to dict for the orchestrator
    input_context = request.model_dump()
    
    async def event_generator():
        trace_id = None
        final_response = None
        
        # Call the orchestrator
        # Note: The orchestrator's streaming generator yields both ProtocolEvent objects and the final dict
        for item in run_workflow_streaming(input_context):
            
            if isinstance(item, ProtocolEvent):
                # Step Event
                event = item
                trace_id = event.session_id
                
                # Firestore persistence (optional)
                if db is not None:
                    event_ref = db.collection("urbannexus_traces").document(trace_id).collection("events").document(event.step)
                    # Use sanitizer to handle nested lists (coordinates) that Firestore rejects
                    safe_payload = sanitize_for_firestore(json.loads(event.model_dump_json()))
                    event_ref.set(safe_payload)
                
                # Stream to client
                yield f"data: {event.model_dump_json()}\n\n"
            
            elif isinstance(item, dict):
                # Final Result
                final_response = item
                trace_id = final_response.get("trace_id")
        
        # Save final result to Firestore
        if final_response and trace_id and db is not None:
            trace_ref = db.collection("urbannexus_traces").document(trace_id)
            final_response_copy = final_response.copy()
            final_response_copy.pop("events", None)
            trace_ref.set(final_response_copy, merge=True)
            
        # Yield final result
        if final_response:
             yield f"data: {json.dumps(final_response)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Legacy Endpoints (Optional, kept for reference) ---

class ProjectBrief(BaseModel):
    corridors: list[str]
    sensors: dict
    storage: str
    vendor_hints: list[str]

@app.post("/analyze", summary="Legacy Analysis")
def analyze(brief: ProjectBrief):
    return run_workflow(brief.model_dump())
