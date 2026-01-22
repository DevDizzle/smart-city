"""
UrbanNexus Smart-City Use Case: FastAPI API (V2 Updated)
"""
import json
import os
import uuid
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
        
        # Call the orchestrator (ADK)
        for item in run_workflow_streaming(input_context):
            
            # Treat everything as a dict (ADK events or final result)
            data_payload = item
            if not isinstance(data_payload, dict) and hasattr(data_payload, 'model_dump'):
                 data_payload = data_payload.model_dump()
            
            # Try to extract trace_id/session_id for persistence
            if not trace_id:
                trace_id = data_payload.get("session_id") or data_payload.get("trace_id")
            
            # Firestore persistence (optional, best effort)
            if db is not None and trace_id:
                try:
                    # Create a unique ID for the event or use step if available
                    step_id = data_payload.get("step") or str(uuid.uuid4())
                    event_ref = db.collection("urbannexus_traces").document(trace_id).collection("events").document(step_id)
                    safe_payload = sanitize_for_firestore(json.loads(json.dumps(data_payload, default=str)))
                    event_ref.set(safe_payload)
                except Exception as e:
                    print(f"Firestore save error: {e}")

            # Stream to client
            yield f"data: {json.dumps(data_payload, default=str)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
