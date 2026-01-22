# UrbanNexus: AI-Powered Smart City Orchestrator

**UrbanNexus** is an enterprise-grade AI agent system designed to automate the complex decision-making process for smart city infrastructure deployment. It demonstrates advanced **AI Engineering** patterns by using a governed multi-agent architecture to balance innovation (value generation) with responsibility (risk mitigation).

> **AI Engineering Showcase:** This project highlights the implementation of **Google's Agent Development Kit (ADK)**, **Vertex AI Agent Engine**, **RAG (Retrieval-Augmented Generation)**, and **Constitutional AI** governance patterns.

---

## 🏗️ System Architecture

UrbanNexus moves beyond simple chatbots by implementing a **Supervisor-Worker** agentic workflow.

### 1. The Core Engine: Google ADK
We utilize the **Google Agent Development Kit (ADK)** to manage agent state, tool execution, and reasoning loops.
-   **Old Architecture:** Manual state machine / LangGraph (Deprecated).
-   **New Architecture:** `LlmAgent` (Supervisor) orchestrating a suite of `FunctionTools`.

### 2. The "City Planner" (Supervisor)
The central brain is the **City Planner Agent**, powered by **Gemini 3.0 Flash**. It does not guess; it follows a strict plan:
1.  **Assess:** Calls the `SiteViability` tool to fetch GIS/physical data.
2.  **Propose:** Delegates to "Advocate" agents (`Sustainability`, `Connectivity`) to generate solution proposals.
3.  **Critique:** Delegates to "Critic" agents (`Privacy`, `PublicSafety`, `OTSecurity`) to attack the proposals with risk analysis.
4.  **Synthesize:** Makes a final `GO / MITIGATE / HOLD` decision based on the combined evidence.

---

## ⚖️ Governance Model: "Advocate vs. Critic"

A key feature of UrbanNexus is its adversarial governance protocol, designed to prevent hallucinated benefits and ignored risks.

| Role | Agents | Responsibility |
| :--- | :--- | :--- |
| **Advocates** | **Sustainability Specialist**<br>**Connectivity Specialist** | Their goal is to **maximize value**. They use RAG to find product features (e.g., "WiFi 6 capability", "40% energy savings") that align with the city's strategic goals. |
| **Critics** | **Privacy Counsel**<br>**Public Safety Specialist**<br>**OT Security Engineer** | Their goal is to **minimize risk**. They use RAG to find compliance documents (e.g., "CJIS Security Policy", "Surveillance Ordinances") and flag violations. |
| **Judge** | **City Planner (Supervisor)** | The supervisor must weigh the *Value Proposals* against the *Risk Findings* to render a final verdict. |

---

## 🛠️ AI Engineering Implementation Details

### 1. Retrieval-Augmented Generation (RAG)
Agents do not rely on internal knowledge for facts. They utilize **Vertex AI Search** to query a curated corpus of:
-   Vendor Specifications (Ubicquia hardware specs)
-   Regulatory Standards (NIST, GDPR, Local Sunshine Laws)

### 2. Tooling & Function Calling
We wrap deterministic Python logic into **ADK Tools**.
-   *Example:* The `assess_site_tool` connects to a mock GIS database. The LLM cannot "hallucinate" the zone's dimensions; it must call the tool to get the ground truth.

### 3. Protocol Adapter (The "Glue")
To bridge the gap between the sophisticated ADK event stream (reasoning steps, tool calls) and the user interface, we implemented a **Protocol Adapter** in the orchestration layer.
-   **Raw Event:** `ToolOutput(tool_name='assess_site', output={...})`
-   **Adapted Event:** `{"step": "assessment", "agent": "SiteViability", "data": {...}}`
-   This ensures the Frontend (Next.js) receives a clean, predictable stream of JSON events via **Server-Sent Events (SSE)**.

---

## 🚀 Getting Started

### Prerequisites
-   Python 3.12+
-   Google Cloud SDK (`gcloud`)
-   `google-adk`

### Backend Setup
1.  **Install Dependencies:**
    ```bash
    make install
    ```
2.  **Configure Environment:**
    Ensure you have `GOOGLE_API_KEY` or `GOOGLE_CLOUD_PROJECT` set.
3.  **Run API Locally:**
    ```bash
    make run.api
    ```
    The API will start at `http://localhost:8000`.

### Frontend Setup
1.  **Navigate:** `cd urbannexus-ui`
2.  **Install & Run:**
    ```bash
    npm install
    npm run dev
    ```
    Open `http://localhost:3000` to interact with the map and agent panel.

---

## ☁️ Deployment

### Agent Deployment (Vertex AI)
We deploy the core agent logic to **Vertex AI Agent Engine** for managed scalability and tracing.
```bash
make deploy.agent
```

### API Deployment (Cloud Run)
The FastAPI wrapper (which serves the frontend stream) is deployed to **Cloud Run**.
```bash
make deploy.api
```

---
*Built with ❤️ by the UrbanNexus Engineering Team*
