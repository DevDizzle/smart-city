# Sprint 2 – PublicSafetySpecialist Agent & API Integration  
**Duration:** 2 weeks  
**Sprint Goal:** Implement the first real specialist agent, integrate into the workflow graph, and expose an API endpoint for the “Go / Mitigate / Hold” decision flow.

### Work Items  
- Define Pydantic schemas in `schemas/`:  
  - `Evidence`, `Risk`, `Requirement` (common)  
  - `PublicSafetyFinding` (topic “public_safety”, evidence[], risks[], requirements[], notes?, confidence)  
- Implement specialist agent: `smart-city/agents/public_safety.py`  
  - Input: `project_brief` (corridors, sensors: ALPR/video/audio, storage, vendor_hints)  
  - Behavior: use `search_app()` to query the knowledge base for focused queries (Sunshine Law video retention, CJIS ALPR handling, vendor encryption/retention)  
  - Output: `PublicSafetyFinding` with ≥3 evidence links, risk list, requirement list (must-haves if ALPR/video/audio present), confidence value  
- Plug agent into workflow graph (ADK):  
  - In `orchestration/graph.py`, run: Parallel(Specialists) → Critic → Validator → Synthesize  
  - Critic: fail if <3 evidence or missing must_have requirement  
  - Validator: fail if ALPR present & no CJIS requirement OR video/audio present & no notice/retention requirement  
- API surface in `smart-city/api/main.py`:  
  - `GET /kb/health` → runs retrieval tool sample query  
  - `POST /analyze` → accepts `project_brief`, runs workflow graph, returns `{decision, confidence, risks, evidence, trace_id}`  
- Deploy to Cloud Run via Makefile (`make deploy.api`) with source deploy of `smart-city/api`  
- **Definition of Done:**  
  - Specialist returns a valid `PublicSafetyFinding` for a brief with ALPR=true & video=true  
  - API endpoint `/analyze` returns properly structured payload  
  - Workflow graph invoked, retrieval → specialist → Critic → Validator flows end-to-end  
  - Basic tracing/logging present for workflow steps  

### Risks & Considerations  
- Retrieval tool latency may affect specialist responsiveness  
- Specialist prompt output must be stable and parseable  
- Permissions for Search App must allow Cloud Run service account  
- Plan fallback if retrieval returns weak results (e.g., manual citations)

