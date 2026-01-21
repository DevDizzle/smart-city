# UrbanNexus Project Plan: "Go/No-Go for Smart-City Deployments"

This document outlines the development plan for UrbanNexus, a governed multi-agent reasoning system, using the Google Agent Development Kit (ADK).

## 1. Use Case: "Go/No-Go for Smart-City Deployments"

The Minimum Viable Product (MVP) will focus on answering the following prompt:

**Prompt:** *“Should City X deploy 500 streetlight AI nodes along corridors A/B to improve traffic safety and operations?”*

## 2. The UrbanNexus Protocol (Retrieve → Critique → Synthesize → Validate)

The system will follow a four-step protocol to arrive at a decision.

### Retrieve
Pull relevant vendor specifications, prior evaluations, and applicable policies into context. Key sources include:
*   **NIST AI RMF:** For AI risk framing and trustworthiness characteristics.
*   **Florida Sunshine Law:** For public records implications.
*   **CJIS (Criminal Justice Information Services):** For public-safety data considerations, mapped to Google Cloud’s CJIS 6.0 guidance.
*   **Smart City Sector Guides:** For privacy/cybersecurity best practices (e.g., NIST GCTC/SC3).
*   **Local Government AI Positions:** (e.g., Florida Association of Counties).
*   **Vendor/Partner Integrations:** (e.g., ALPR/safety with Genetec, UbiHub/UbiCell specs).

### Critique (QA)
Check for gaps in the retrieved information and the proposal, including:
*   Data classification, retention, encryption, and access policies.
*   Human rights and privacy risks.
*   Procurement and ADA compliance.
*   Public engagement plans.
*   Observability and monitoring.

### Synthesize
Produce a clear decision brief with one of three outcomes:
1.  **Proceed**
2.  **Proceed with Mitigations**
3.  **Do Not Proceed**

The brief will include evidence links, a risk table, and recommended mitigations (e.g., “use Assured Workloads, sign logs, redact PII, implement FOIA-ready retention policy”).

### Validate (Governance Gates)
Programmatically enforce policy thresholds. For example:
*   If ALPR is present → CJIS compliance path is required.
*   If microphones/cameras are present → A privacy impact assessment and community notice are required.
*   If data leaves the state → Data boundary controls must be implemented.

If any gate is not met, the process will loop back for revisions.

## 3. Development Plan (ADK Phases)

### Phase 1: Agents
Develop a team of specialized agents, including:
*   PublicSafetySpecialist
*   OT/SecurityEngineer
*   PrivacyCounsel
*   Procurement/Policy
*   CivicEngagement
*   Critic (for QA)
*   Validator (for governance)

Each agent will be an expert in the relevant frameworks (AI RMF, Sunshine Law, CJIS) and vendor patterns.

### Phase 2: Governance
*   **Schemas:** Use Pydantic to define the data structures for Findings, Critiques, and Decisions.
*   **Audit Trail:** Sign every `ProtocolEvent` and export the complete trace to Cloud Logging and BigQuery. The trace will be designed to be "FOIA-ready" (public record friendly).

### Phase 3: Orchestration (ADK)
Use the ADK's native orchestration features to manage the workflow:
*   Run specialist agents in parallel.
*   Implement automatic loop-backs if the Validator agent flags missing controls.

### Phase 4: RAG (Retrieval-Augmented Generation)
*   **Vertex AI Search:** Create a knowledge base from vendor docs, municipal policies, privacy notices, procurement rules, and city code.
*   **Vertex AI Vector Search:** Create a separate vector search index of prior city decisions and mitigations to allow the system to "remember" what has been approved in the past.

## 4. Pilot Project (The First Milestone)

### Scenario
*“Deploy UbiHub AP/AI on 50 lights around a campus/corridor for traffic & safety analytics.”*

### Deliverables
1.  **Decision Brief:** A "Go/Mitigate/Hold" recommendation with a confidence score.
2.  **Risk & Mitigation Table:** Covering privacy, storage, encryption, retention, and public engagement.
3.  **Audit Bundle:** A Sunshine-Law-ready package containing the trace JSON, policy mappings, and citations.

### Success Metrics
*   Time-to-decision.
*   Percentage of decisions with linked evidence.
*   Number of validator loop-backs prevented.
*   Completeness of the audit trail.
