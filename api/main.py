"""
VeritAI Smart-City Use Case: FastAPI API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestration.graph import run_workflow
from rag.vertex_search import search_app
from protocol.events import ProtocolEvent
from fastapi.middleware.cors import CORSMiddleware # Added CORS import

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
origins = [
    "http://localhost:3000",  # For local development
    "https://3000-cs-832847987222-default.cs-us-east1-yeah.cloudshell.dev", # Your Cloud Shell frontend URL
    # Add other frontend origins if necessary
]

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

@app.post("/analyze", summary="Analyze a Project Brief")
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

@app.get("/trace/{trace_id}", summary="Get a trace by ID")
def get_trace(trace_id: str):
    """
    Retrieves the protocol events for a given trace ID.
    """
    if db is None:
        raise HTTPException(status_code=503, detail="Trace persistence not configured")

    trace_ref = db.collection("veritai_traces").document(trace_id)
    trace = trace_ref.get()
    if trace.exists:
        return trace.to_dict().get("events", [])
    else:
        raise HTTPException(status_code=404, detail="Trace not found")