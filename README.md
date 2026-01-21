# UrbanNexus Smart City Platform

**UrbanNexus** is an intelligent infrastructure optimization engine designed to help city planners and administrators make data-driven decisions. It utilizes a multi-agent system to analyze urban zones, assess value propositions, identify risks, and synthesize strategic recommendations for smart city upgrades.

## Core Features

-   **Multi-Agent Architecture:** Specialized agents for Connectivity, Site Viability, Sustainability, Public Safety, OT Security, and Privacy.
-   **RAG-Powered Knowledge Base:** Retrieves and grounds decisions in real-world standards (NIST, CJIS, Sunshine Laws).
-   **Interactive Dashboard:** Select zones, define goals (Safety, Energy, Connectivity), and view live agent reasoning.
-   **Transparent Reasoning:** "Live Agent Trace" visualizes the step-by-step logic from assessment to final decision.

## Project Structure

-   `urbannexus/`: Core Python package containing the multi-agent protocol and state management.
-   `agents/`: Specialized agent implementations.
-   `api/`: FastAPI backend service (`api/main.py`).
-   `urbannexus-ui/`: Next.js frontend application.
-   `orchestration/`: LangGraph workflow definitions.
-   `rag/`: Vector search and document processing utilities.

## Getting Started

### Backend (Cloud Run / Local)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run Locally:**
    ```bash
    uvicorn api.main:app --reload
    ```

### Frontend (Next.js)

1.  **Navigate to UI:**
    ```bash
    cd urbannexus-ui
    ```
2.  **Install & Run:**
    ```bash
    npm install
    npm run dev
    ```

## Deployment

The system is designed for Google Cloud Run.
-   **Backend:** Deployed as a Python service.
-   **Frontend:** Deployed as a Next.js standalone container.

---
*Powered by Google Gemini 1.5 Pro & Vertex AI*