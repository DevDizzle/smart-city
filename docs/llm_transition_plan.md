# Plan: Transitioning UrbanNexus to LLM-Powered Reasoning with `gemini-2.5-pro`

The objective is to replace or augment the current explicit, hardcoded `if`/`else` logic within the `Specialist`, `Critic`, and `Validator` agents with dynamic reasoning capabilities provided by the `gemini-2.5-pro` LLM. The existing `ProtocolRule` objects will serve as guiding principles or context for the LLM.

---

## Phase 1: Foundation & LLM Integration Strategy

1.  **Dependency Management:**
    *   Update the project's `requirements.txt` (or equivalent) to include `google-genai`.
    *   Ensure any legacy `google-generativeai` dependency is removed to prevent conflicts.
    *   Follow the [Gemini best practices](https://ai.google.dev/gemini-api/docs/get-started/python) by configuring a `genai.Client` with the `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) environment variable.
2.  **LLM Client Design (Conceptual):**
    *   Design a dedicated module (e.g., `src/urbannexus/llm_client.py`) to abstract interactions with the `google-genai` library.
    *   This client will provide a simplified interface for:
        *   Sending prompts to the `gemini-2.5-pro` model.
        *   Handling various response formats, including structured outputs (e.g., JSON).
        *   Configuring model parameters like `temperature` and `max_output_tokens`.
        *   Implementing robust error handling, rate limiting, and retry logic.
    *   Consider leveraging `google-genai`'s function calling feature to enforce strict JSON schema adherence for structured outputs from the LLM.
    *   Pass generation parameters via `google.genai.types.GenerateContentConfig` (including `response_mime_type="application/json"` when structured output is required) to ensure consistent behavior across SDK releases.

---

## Phase 2: Specialist Agent Enhancement (e.g., `PublicSafetySpecialist`)

1.  **Objective:** Transition from hardcoded risk/requirement identification to LLM-driven analysis based on project briefs and RAG results.
2.  **Conceptual Workflow:**
    *   The `Specialist` agent will continue to perform Retrieval-Augmented Generation (RAG) to gather relevant documents and context.
    *   Instead of using `_identify_risks` and `_identify_requirements` with explicit `if` conditions, the agent will construct a detailed prompt for `gemini-2.5-pro`.
    *   This prompt will include:
        *   The full `project_brief`.
        *   The content of the retrieved `evidence` from RAG.
        *   Clear instructions for the LLM to act as a domain expert (e.g., "Public Safety Specialist").
        *   A specific request to identify and list potential risks and necessary requirements related to the project, grounded in the provided brief and evidence.
        *   A precise JSON schema for the LLM to follow when outputting identified risks and requirements.
    *   The LLM's structured JSON response will then be parsed and converted into the existing `Risk` and `Requirement` data structures.

---

## Phase 3: Critic Agent Transformation

1.  **Objective:** Evolve the `Critic` agent from rule-based checks to intelligent, nuanced critique of specialist findings.
2.  **Conceptual Workflow:**
    *   The `Critic` agent will receive the `PublicSafetyFinding` (potentially already enhanced by LLM-driven Specialist agents) and the `project_brief`.
    *   It will formulate a comprehensive prompt for `gemini-2.5-pro` that includes:
        *   The complete `PublicSafetyFinding` details (evidence, risks, requirements, confidence).
        *   The `project_brief` context.
        *   Instructions for the LLM to act as an impartial "Critic" tasked with identifying:
            *   Any logical inconsistencies, contradictions, or gaps in the finding.
            *   Unfounded assumptions or biases.
            *   Insufficient evidence or detail.
            *   Potential non-compliance with general best practices or the spirit of the `ProtocolRule` objects (which can be provided as context in the prompt).
        *   A defined JSON schema for the LLM's output, specifying fields for identified issues, missing requirements, and a recommended status (e.g., "ok", "revise").
    *   The LLM's structured response will be parsed to update the critique status and provide detailed notes on identified issues.

---

## Phase 4: Validator Agent Transformation

1.  **Objective:** Enable the `Validator` agent to perform more intelligent and context-aware governance checks, interpreting and applying rules dynamically.
2.  **Conceptual Workflow:**
    *   The `Validator` agent will receive the `PublicSafetyFinding`, the `critic_output` (now LLM-generated), and the `project_brief`.
    *   Crucially, it will also be provided with the `ProtocolRule` objects from `rules.py` as explicit context within its prompt.
    *   A detailed prompt will be constructed for `gemini-2.5-pro` including:
        *   All relevant input data (`PublicSafetyFinding`, `critic_output`, `project_brief`).
        *   The full text or key attributes of the `ProtocolRule` objects, clearly indicating their purpose and conditions.
        *   Instructions for the LLM to act as a "Validator" and determine the final governance status ("GO", "HOLD", "MITIGATE").
        *   The LLM must be explicitly instructed to justify its decision by referencing the provided rules and findings.
        *   A precise JSON schema for the LLM's output, including the final status and a detailed reason.
    *   The LLM's structured response will be parsed to determine the final governance status and its accompanying rationale.

---

## Phase 5: Testing, Optimization, and Monitoring

1.  **Comprehensive Testing:** Develop new unit and integration tests specifically for the LLM-powered agents to verify:
    *   Correct parsing and interpretation of LLM outputs.
    *   Accurate decision-making across a wide range of scenarios.
    *   Robustness to unexpected LLM responses.
2.  **Prompt Engineering Iteration:** Continuously refine and optimize the prompts for each agent through experimentation. This includes exploring few-shot examples, system instructions, and different phrasing to improve LLM accuracy, consistency, and adherence to output formats.
3.  **Performance and Cost Monitoring:** Implement logging and monitoring to track LLM API calls, latency, token usage, and associated costs. This is crucial for managing operational expenses and identifying areas for optimization.
4.  **Human-in-the-Loop (HITL) Enhancement:** Ensure the system's UI/API layer is capable of effectively presenting the LLM-generated reasoning traces and justifications for human review, override, and auditing, reinforcing the "Complete Audit Trail by Design" principle.