# UrbanNexus: ADK (Agent Development Kit) Feasibility Analysis

**Date:** January 21, 2026
**Target:** Architecture Team
**Goal:** Evaluate replacing the current custom orchestration engine with Google's **Agent Development Kit (ADK)** to enhance reliability, scalability, and integration.

---

## 1. Executive Summary

UrbanNexus currently utilizes a **custom-built Python orchestration engine** (`orchestration/graph.py`) that manages state and agent execution using `ThreadPoolExecutor` and Python generators. While functional for the MVP, it lacks the robustness of a dedicated agent framework.

This analysis explores adopting Google's **Agent Development Kit (ADK)**, an open-source framework designed to streamline the creation of Gen AI agents, particularly those leveraging the Gemini ecosystem and Vertex AI.

**Verdict:** **High Potential for "Phase 2".** Adopting ADK would significantly reduce boilerplate code for agent communication and state management, but requires a moderate refactor of the existing agent classes.

---

## 2. What is ADK?

The **Agent Development Kit (ADK)** is Google's framework for building agentic workflows. Unlike generic libraries (like LangChain), ADK is optimized for:
*   **Gemini Native:** Built-in support for Gemini's function calling and reasoning capabilities.
*   **Vertex AI Integration:** Seamless deployment to **Vertex AI Agent Engine**, offering managed infrastructure for running agents.
*   **Hierarchical Delegation:** First-class support for "Supervisor -> Worker" patterns, which UrbanNexus mimics manually today.

---

## 3. Architecture Comparison

| Feature | Current Architecture (Custom Graph) | Proposed ADK Architecture |
| :--- | :--- | :--- |
| **Orchestration** | Manual DAG in `graph.py` (State Machine). | **Declarative Workflows:** Agents define their capabilities, and ADK/Gemini handles the routing. |
| **Parallelism** | Manual `ThreadPoolExecutor` implementation. | **Native Async/Parallel:** ADK handles concurrent agent execution out-of-the-box. |
| **State Management** | Custom `ProtocolEvent` objects streamed manually. | **Managed State:** ADK tracks conversation history and agent scratchpads automatically. |
| **Observability** | Custom logging to Firestore (`utils/firestore_sanitizer.py`). | **Vertex Tracing:** Built-in integration with Google Cloud Trace and logging. |
| **Deployment** | Cloud Run (Stateless HTTP container). | Cloud Run or **Vertex AI Agent Runtime** (Managed stateful service). |

---

## 4. Benefits of Migration

### 1. Reduced "Glue" Code
Currently, `orchestration/graph.py` contains complex logic to manage the "Advocate vs. Critic" debate flow. ADK's **Delegation** patterns would allow us to simply define a `Synthesizer` agent that has access to `Privacy` and `Safety` tools, and the framework would handle the "ask and wait" loop naturally.

### 2. Robust Error Handling
Our current system has basic try/catch blocks. ADK provides structured error handling, retries (crucial for LLM flakiness), and fallback mechanisms standardizing how agents recover from failures.

### 3. Native Function Calling
Instead of manually parsing JSON outputs from prompts (which is error-prone), ADK leverages Gemini's native tool-use API. This would make our agents (`agents/*.py`) much cleaner, as they would just expose Python functions as "Tools".

---

## 5. Migration Roadmap

To adopt ADK, we would execute the following plan:

1.  **Wrap Agents as Tools:** Convert existing classes (e.g., `SiteViabilityAgent`) into ADK-compatible Tools.
    *   *Current:* `agent.run(zone_id)`
    *   *ADK:* `@tool def assess_site(zone_id: str) -> Zone:`
2.  **Define the "Supervisor":** Replace `graph.py` with an ADK Agent definition that acts as the "City Planner". Give it the instructions to "Assess value, then check risks, then synthesize."
3.  **Refactor API:** Update `api/main.py` to invoke the ADK runtime instead of `run_workflow_streaming`.
4.  **Vertex Integration:** Update `Makefile` to deploy the agent configuration to Vertex AI.

## 6. Conclusion

Moving to ADK is recommended for the **Operationalization Phase** (Sprint 3+).
*   **Pros:** Less code to maintain, better Gemini integration, "enterprise-grade" stability.
*   **Cons:** Vendor lock-in to Google/Vertex ecosystem (which matches our current direction), learning curve for new framework.

**Recommendation:** Continue with the custom graph for the immediate demo to ensure stability, but provision a "Spike" task to prototype the `PublicSafetySpecialist` using ADK to measure code reduction.
