# Sprint 4 – Multi-Agent Panel and Decision Synthesis

**Goal:** Move from a single specialist to a small, realistic multi-agent panel and produce a richer, well structured decision brief.

**Assumption:**  
- PublicSafetySpecialist, Critic, Validator, and tracing are working from Sprints 2 and 3.
- Vertex AI Search retrieval is stable.

---

## 1. Scope

1. Add at least two more specialist agents:
   - PrivacyCounsel
   - OT_SecurityEngineer
2. Extend schemas so we can combine findings into a structured DecisionBrief.
3. Update the ADK graph to run the specialists in parallel and then synthesize a unified decision.

---

## 2. Work Items

### 2.1 Schemas for multi-agent findings and decision brief

Location: `veritai-core/schemas/`

Add or extend:

- `PrivacyFinding`:
  - `topic: Literal["privacy"]`
  - `evidence: list[Evidence]`
  - `risks: list[Risk]`
  - `requirements: list[Requirement]`
  - `notes: Optional[str]`
  - `confidence: condecimal(ge=0, le=1)`

- `OTSecurityFinding`:
  - `topic: Literal["ot_security"]`
  - same structure as above.

- `DecisionBrief`:
  - `project_brief: dict`
  - `public_safety: PublicSafetyFinding`
  - `privacy: Optional[PrivacyFinding]`
  - `ot_security: Optional[OTSecurityFinding]`
  - `combined_risks: list[Risk]`
  - `combined_requirements: list[Requirement]`
  - `overall_decision: Literal["GO", "MITIGATE", "HOLD"]`
  - `overall_confidence: condecimal(ge=0, le=1)`

Update any JSON schema export logic so these types are included.

---

### 2.2 PrivacyCounsel agent

Location: `smart-city/agents/privacy.py`

Inputs:

- `project_brief`
- Access to `search_app()` for privacy and transparency related queries.

Behavior:

1. Build focused queries such as:
   - "Florida Sunshine Law video surveillance retention"
   - "public records obligations for camera footage Florida"
   - "privacy impact assessment public surveillance"
2. Use `search_app` for each query, dedupe by URI.
3. Construct `PrivacyFinding`:
   - Evidence:
     - At least 3 policy or guidance documents.
   - Risks:
     - Examples:
       - Over-collection of personally identifying data.
       - Insufficient notice to the public.
       - Retention periods that are too long relative to best practice.
   - Requirements:
     - Publicly posted notice where sensors are deployed.
     - Published retention schedule for video/ALPR/audio data.
     - Clear rules on secondary use and data sharing.
   - Confidence:
     - Similar heuristic to PublicSafetySpecialist based on coverage and evidence.

Tests:

- Unit tests for a `project_brief` with video/audio = true:
  - `PrivacyFinding` must include at least:
    - A notice requirement.
    - A retention schedule requirement.
    - Evidence length >= 3.

---

### 2.3 OT_SecurityEngineer agent

Location: `smart-city/agents/ot_security.py`

Inputs:

- `project_brief` including:
  - `storage: "edge" | "cloud" | "hybrid"`
  - `vendor_hints` such as "Ubicquia UbiHub AP/AI".

Behavior:

1. Build focused queries such as:
   - "Ubicquia UbiHub AP/AI security encryption edge"
   - "smart streetlight OT security best practices"
   - "network segmentation smart city OT"
2. Use `search_app`, dedupe by URI.
3. Construct `OTSecurityFinding`:
   - Evidence:
     - At least 3 technical or vendor sources.
   - Risks:
     - Weak or missing encryption at rest or in transit.
     - Insufficient network segmentation from other city systems.
     - Lack of security monitoring and log collection from devices.
   - Requirements:
     - Encryption at rest and in transit.
     - Network segmentation and access control for devices.
     - Centralized security logging and monitoring.
   - Confidence:
     - Based on how much relevant data is found.

Tests:

- Unit tests for a `project_brief` with `storage = "cloud"` and vendor hints including Ubicquia:
  - `OTSecurityFinding` must include an encryption requirement and at least one network segmentation requirement.

---

### 2.4 Updated ADK graph and synthesis step

Location: `veritai-core/orchestration/graph.py` and `veritai-core/orchestration/synthesis.py`

Changes:

- Parallel specialists:
  - `PublicSafetySpecialist`
  - `PrivacyCounsel`
  - `OT_SecurityEngineer`
- After all three specialists complete and pass Critic:
  - Call a `Synthesis` node that:
    - Merges evidence, risks, and requirements from all findings.
    - Computes `overall_decision` and `overall_confidence` using:
      - Validator status for each specialist.
      - High severity risks across findings.
      - Lowest confidence among findings or a weighted combination.
    - Returns a `DecisionBrief`.

Graph routing:

- Critic and Validator can run per specialist.
- Synthesis looks at:
  - If any specialist yields `HOLD` → `overall_decision = "HOLD"`.
  - Else if any specialist yields `MITIGATE` → `overall_decision = "MITIGATE"`.
  - Else → `overall_decision = "GO"`.

Update `/analyze` API:

- Return `DecisionBrief` fields plus `trace_id`.

---

## 3. Acceptance Criteria

Sprint 4 is complete when:

1. PrivacyCounsel and OT_SecurityEngineer agents are implemented, tested, and integrated into the graph.
2. For an ALPR + video scenario:
   - All three specialists produce findings with at least 3 evidence items.
   - The combined `DecisionBrief` contains merged risks and requirements.
3. `/analyze` returns a `DecisionBrief` including:
   - project_brief
   - each specialist finding
   - combined_risks
   - combined_requirements
   - overall_decision
   - overall_confidence
4. Critic/Validator logic is applied per specialist and informs the overall decision in Synthesis.
