# Sprint 3 – Governance, Gates, and Audit

**Goal:** Turn the working flow into a governed system with clear policy gates and an auditable trace for every decision.

**Assumption:**  
- Sprint 1 (KB + retrieval) and Sprint 2 (PublicSafetySpecialist + `/analyze` API) are complete and passing basic tests.

---

## 1. Scope

1. Strengthen Critic and Validator so they enforce concrete policy gates based on sensors in `project_brief`.
2. Emit a structured protocol trace for each run and ship it to Cloud Logging and BigQuery.
3. Make the decision payload reflect those governance checks in a stable, documented way.

---

## 2. Work Items

### 2.1 Critic logic (quality gate)

Location: `veritai-core/protocol/critic.py` (or equivalent)

Responsibilities:

- Inspect `PublicSafetyFinding` plus the input `project_brief`.
- Fail with a structured reason if:
  - `finding.evidence` has fewer than 3 items, or
  - Required controls are missing, given sensor configuration.

Rules:

- If `project_brief.sensors.alpr == true`:
  - Require at least one `Requirement` with:
    - `must_have == true`
    - `id` or `description` referencing CJIS or criminal justice data handling.
- If `project_brief.sensors.video == true` or `project_brief.sensors.audio == true`:
  - Require at least one `Requirement` with:
    - `must_have == true`
    - `description` that clearly mentions both public notice and retention schedule for recorded media.
- If `finding.confidence` < 0.4:
  - Critic flags low confidence and recommends revision.

Implementation details:

- Introduce a small helper like `check_required_controls(finding, project_brief)` that returns a list of missing controls.
- Critic returns:
  - `status: "ok" | "revise"`
  - `missing_requirements: list[str]`
  - `notes: Optional[str]`

Update tests:

- Unit tests that verify:
  - Missing CJIS requirement when ALPR = true causes Critic to fail.
  - Missing notice + retention requirement when video = true causes Critic to fail.
  - Enough evidence and proper requirements leads to status "ok".

---

### 2.2 Validator logic (hard governance gate)

Location: `veritai-core/protocol/validator.py` (or equivalent)

Responsibilities:

- Consume `PublicSafetyFinding` and Critic output.
- Decide final governance status for this step:
  - `GO`
  - `MITIGATE`
  - `HOLD`

Rules:

- If Critic status is "revise":
  - Validator returns `status: "HOLD"` and reason.
- Else:
  - If ALPR = true and no CJIS-related `Requirement` with `must_have == true`:
    - `status: "HOLD"`
    - `reason: "ALPR present but CJIS path is not defined"`
  - If video/audio = true and no public notice + retention `Requirement` with `must_have == true`:
    - `status: "MITIGATE"`
    - `reason: "Sensors require public notice and retention schedule"`
  - Otherwise:
    - `status: "GO"` or `status: "MITIGATE"` depending on risk levels:
      - For example: if any `Risk` has `severity == "high"` and `likelihood != "low"`, return `MITIGATE`.

Orchestration:

- Wire Validator status into the ADK graph so that:
  - A `HOLD` loops back to specialists for revision.
  - A `MITIGATE` continues, but the final decision is labeled `MITIGATE`.
  - A `GO` continues cleanly.

Tests:

- Unit tests for Validator:
  - ALPR without CJIS requirement -> HOLD.
  - Video without notice + retention -> MITIGATE.
  - All gates satisfied and only low/medium risks -> GO.

---

### 2.3 ProtocolEvent trace and logging

Location: `veritai-core/protocol/events.py`, integrated into graph

Create a `ProtocolEvent` model with fields:

- `session_id: str`
- `step: str` (examples: `retrieve`, `public_safety`, `critic`, `validator`, `synthesize`)
- `agent: str`
- `inputs_ref: dict`
- `outputs_ref: dict`
- `timestamp: str` (ISO 8601)
- `decision_state: Optional[str]` (GO/MITIGATE/HOLD if applicable)

For each graph node:

- Instantiate a `ProtocolEvent`.
- Log as JSON using Python `logging` with a consistent label, for example:
  - `logger.info(json.dumps(protocol_event), extra={"veritai_protocol_event": True})`

Add a `trace_id` that is shared across all events for a single `/analyze` call. Return this `trace_id` in the API response.

---

### 2.4 Cloud Logging and BigQuery integration

While this is mostly infra, we can document expected setup:

- Cloud Run service is already producing logs.
- Create:
  - A BigQuery dataset named, for example, `veritai_audit`.
  - A table for protocol events, or let the logging sink auto-create it.
- Create a logging sink that:
  - Filters for entries where `veritai_protocol_event` is true.
  - Writes them into the BigQuery dataset.

Add a short how-to in `docs/Runbook_MVP.md` on how to query by `trace_id`.

---

## 3. Acceptance Criteria

Sprint 3 is complete when:

1. Critic and Validator enforce the ALPR/CJIS and video/audio notice + retention requirements.
2. A `/analyze` call for an ALPR + video scenario:
   - Fails initially if requirements are missing.
   - Succeeds when the specialist adds those requirements.
3. Each `/analyze` call emits a sequence of `ProtocolEvent` logs with a shared `trace_id`.
4. ProtocolEvent logs are visible in BigQuery via the configured sink, and we can query all events for a given `trace_id`.
