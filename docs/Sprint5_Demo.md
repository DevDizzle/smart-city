# Sprint 5 – Demo UX, Human Review Signal, and Runbook

**Goal:** Make the UrbanNexus smart-city MVP easy to demo, easy to understand, and easy for another engineer to deploy and test.

**Assumption:**
Sprints 1–4 are complete and `/analyze` returns a structured `DecisionBrief` with a `trace_id`.

---

## 1. Scope

1. Expose a clear decision + trace view.
2. Add an explicit human review signal.
3. Write a simple runbook and demo scenarios.

---

## 2. Work Items

### 2.1 Decision + Trace View

**API:**
- Confirm `POST /analyze` returns (at minimum):
  {
    "decision": "GO | MITIGATE | HOLD",
    "confidence": 0.0,
    "combined_risks": [...],
    "combined_requirements": [...],
    "evidence": [...],
    "trace_id": "..."
  }

Add GET /trace/{trace_id}:
- Input: trace_id from /analyze.
- Output: ordered list of protocol events for that run (either pulled from BigQuery or from whatever trace store we use).
- This does not need to be fancy; JSON is fine.

Minimal UI:
- Rely on FastAPI docs / Swagger for now.
- Make sure /analyze and /trace/{trace_id} are easy to call from there.

### 2.2 Human Review Signal

Extend the synthesis / final decision step and schema so we include:
- needs_human_review: bool
- human_review_note: Optional[str]

Policy:
- If overall_decision == "HOLD":
  - needs_human_review = true
  - human_review_note = "Project is on hold due to unresolved high risk or missing required controls. Recommend review by legal and public safety stakeholders."
- If overall_decision == "MITIGATE" and any combined risk has severity == "high" and likelihood != "low":
  - needs_human_review = true
  - human_review_note = "High severity risks remain under a MITIGATE decision. Recommend review before approval."
- Otherwise:
  - needs_human_review = false
  - human_review_note can be null or a short confirmation string.

Make sure these fields:
- Are part of the DecisionBrief model.
- Are included in the /analyze response.
- Are reflected in the final ProtocolEvent for the run.

### 2.3 Zones and Demo Scenarios

Project brief shape (canonical):

{
  "zone": "FAU",
  "corridors": ["Glades Rd corridor", "Campus core"],
  "sensors": {
    "alpr": true,
    "video": true,
    "audio": false
  },
  "storage": "edge",
  "vendor_hints": ["Ubicquia UbiHub AP/AI"]
}

Requirements:
- zone is a string (support at least "FAU" and "Mizner").
- Agents can use zone for prompt context, but gates are still driven by sensors + storage.

Create docs/Demo_Scenarios.md with three scenarios:

- Scenario A – Likely HOLD
  - ALPR + video, cloud storage, weak or missing controls.
  - Expected: decision = "HOLD", needs_human_review = true.

- Scenario B – MITIGATE
  - Video only, edge or hybrid storage.
  - Strong encryption but missing explicit public notice.
  - Expected: decision = "MITIGATE", needs_human_review = true.

- Scenario C – GO
  - Limited sensors, strong controls, clear retention and notice documentation.
  - Expected: decision = "GO", needs_human_review = false.

Each scenario should include:
- Full project_brief JSON.
- Expected decision, needs_human_review, and one or two key requirements that should appear.

### 2.4 Runbook

Create docs/Runbook_MVP.md with:

#### Overview
Short description of the MVP: “UrbanNexus evaluates smart-streetlight AI deployments and returns GO / MITIGATE / HOLD with an audit trace.”

#### Prerequisites
Google Cloud project with:
- Vertex AI Search enabled and configured.
- Cloud Run enabled.
- BigQuery dataset for protocol events.
- Service account permissions for:
  - Vertex AI Search.
  - BigQuery (if /trace/{trace_id} queries it).

#### Configuration
How to set:
- GOOGLE_CLOUD_PROJECT
- REGION
- Vertex AI Search engine / serving config id.
- Any .env values expected by the API.

#### Deployment
Single command (example):
- make deploy.api
What service name and URL to expect.

#### Smoke Tests
- make kb.health
Example curl commands:
- GET /kb/health
- POST /analyze with Scenario B project_brief.
- GET /trace/{trace_id} using returned trace_id.

#### Basic Troubleshooting
Where to look if:
- Retrieval returns empty results (Vertex AI Search).
- Permission errors occur (Cloud Run logs).
- Trace lookup fails (BigQuery or logging config).

---

## 3. Acceptance Criteria

Sprint 5 is complete when:
- /analyze returns decision, confidence, combined_risks, combined_requirements, evidence, trace_id, needs_human_review, and human_review_note.
- /trace/{trace_id} returns an ordered list of protocol events for that run (or an equivalent documented way to fetch them).
- docs/Demo_Scenarios.md contains the three scenarios above and they are reproducible by calling /analyze.
- A new engineer can follow docs/Runbook_MVP.md to:
  - Deploy the API to Cloud Run.
  - Run kb.health.
  - Execute at least one demo scenario end to end.