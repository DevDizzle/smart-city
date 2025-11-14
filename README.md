# VeritAI Smart-City Use Case

This project is a demonstration of the VeritAI multi-agent decision-making system, built for the "Go/No-Go for Smart-City Deployments" use case.

## 🚀 Overview

VeritAI is a governed multi-agent reasoning system that evaluates the deployment of AI-powered smart-city infrastructure. It uses a panel of specialized AI agents to analyze a project brief and provide a "Go / Mitigate / Hold" recommendation with a full audit trail.

This specific use case evaluates the deployment of smart streetlight nodes with sensors like ALPR, video, and audio, considering public safety, privacy, and security implications.

## ✨ Features

*   **Multi-Agent Analysis:** A panel of specialist agents (Public Safety, Privacy, and OT Security) analyze the project from different perspectives.
*   **Retrieval-Augmented Generation (RAG):** Agents are grounded in a knowledge base of real-world policy documents, including NIST AI RMF, Florida Sunshine Law, and CJIS Security Policy.
*   **Governance by Design:** A `Critic` and `Validator` agent review the specialists' findings to ensure quality and enforce governance gates.
*   **Auditable Decisions:** Every step of the decision-making process is logged, and a unique `trace_id` is generated for each analysis.
*   **FastAPI:** The application is exposed as a REST API using FastAPI.

## 🛠️ How to Run

1.  **Install Dependencies:**
    ```bash
    make install
    ```
2.  **Run the API:**
    ```bash
    make run.api
    ```
3.  **Test the API:**
    Open your browser to `http://127.0.0.1:8000/docs` to access the FastAPI Swagger UI and test the `/analyze` endpoint.
