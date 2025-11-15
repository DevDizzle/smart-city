"""
VeritAI Smart-City Use Case: FastAPI API
"""
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError
from orchestration.graph import run_workflow, run_workflow_streaming
from rag.vertex_search import search_app
from protocol.events import ProtocolEvent
from fastapi.middleware.cors import CORSMiddleware
from schemas.decision_brief import DecisionBrief

app = FastAPI(
    title="VeritAI Smart-City API",
    description="API for the VeritAI Smart-City use case.",
    version="0.1.0",
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

class ProjectBrief(BaseModel):
    """Pydantic model for the project brief."""
    corridors: list[str]
    sensors: dict
    storage: str
    vendor_hints: list[str]

@app.get("/kb/health", summary="Knowledge Base Health Check")
def kb_health():
    """
    Performs a health check on the Knowledge Base by running a sample query.
    """
    results = search_app(query="Sunshine Law video retention", top_k=3)
    if results:
        return {"status": "ok", "results": results}
    else:
        return {"status": "error", "message": "No results returned from KB."}

@app.post("/analyze", summary="Analyze a Project Brief (Non-Streaming)")
def analyze(brief: ProjectBrief):
    """
    Analyzes a project brief and returns a decision.
    """
    result = run_workflow(brief.model_dump())
    trace_id = result.get("trace_id")
    if trace_id and db is not None:
        # Store the trace in Firestore
        trace_ref = db.collection("veritai_traces").document(trace_id)
        trace_ref.set({"events": result.get("events", [])})
    # We don't want to return the events in the main response, just the trace_id
    result.pop("events", None)
    return result

@app.get("/analyze-stream", summary="Analyze a Project Brief (Streaming)")
async def analyze_stream(brief_json: str):
    """
    Analyzes a project brief and streams the events in real-time.
    """
    try:
        brief_data = json.loads(brief_json)
        brief = ProjectBrief(**brief_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid Project Brief JSON")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Project Brief data: {e}")
    async def event_generator():
        trace_id = None
        final_response = None
        
        for item in run_workflow_streaming(brief.model_dump()):
            if isinstance(item, ProtocolEvent):
                # This is a step in the process
                event = item
                trace_id = event.session_id
                if db is not None:
                    # Save event to subcollection
                    event_ref = db.collection("veritai_traces").document(trace_id).collection("events").document(event.step)
                    event_ref.set(event.model_dump())
                
                # Yield event to client
                yield f"data: {event.model_dump_json()}\n\n"
            
            elif isinstance(item, dict):
                # This is the final decision brief
                final_response = item
                trace_id = final_response.get("trace_id")

        if final_response and trace_id and db is not None:
            # Save the final decision brief to the main trace document
            trace_ref = db.collection("veritai_traces").document(trace_id)
            # Exclude events list from the main doc, as they are in the subcollection
            final_response_copy = final_response.copy()
            final_response_copy.pop("events", None)
            trace_ref.set(final_response_copy, merge=True)
        
        # Yield final response to client
        if final_response:
            yield f"data: {json.dumps(final_response)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/trace/{trace_id}", summary="Get a trace by ID")
def get_trace(trace_id: str):
    """
    Retrieves the protocol events for a given trace ID from the subcollection.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Trace persistence not configured")

    events_ref = db.collection("veritai_traces").document(trace_id).collection("events")
    docs = events_ref.stream()
    events = [doc.to_dict() for doc in docs]
    
    if events:
        # Sort events by timestamp
        events.sort(key=lambda e: e.get('timestamp', ''))
        return events
    else:
        # Fallback to check the main document for old-style traces
        trace_ref = db.collection("veritai_traces").document(trace_id)
        trace = trace_ref.get()
        if trace.exists and trace.to_dict().get("events"):
            return trace.to_dict().get("events", [])
        raise HTTPException(status_code=404, detail="Trace not found or contains no events.")