# VeritAI Smart-City Operationalization Plan

This document outlines the plan for operationalizing the VeritAI Smart-City demo, including the deployment of the analysis service and the development of a web-based UI.

## 1. Service Deployment

The core analysis service is implemented as a FastAPI application and deployed as a containerized service on Google Cloud Run.

- **Endpoint:** `/analyze`
- **URL:** `https://veritai-smart-city-r5uzf6jgla-uc.a.run.app`
- **Deployment:** The service is deployed from a Docker container, managed by Google Cloud Run.

## 2. Frontend Development (Firebase Studio)

A modern, sharp, and intuitive web application will be developed using Firebase Studio to demonstrate the VeritAI framework.

### Firebase Studio Prompt

**Objective:**

Create a modern, sharp, and intuitive web application to demonstrate the VeritAI framework applied to a smart-city scenario. The application will allow users to input a project brief, submit it to a VeritAI service for analysis, and visualize the results and the decision-making process.

**Application Name:** VeritAI Smart-City Decision Hub

**Key Features:**

1.  **Project Brief Input Form:**
    *   A clean and user-friendly form to input the project brief.
    *   The form should have the following fields:
        *   `corridors`: A multi-select dropdown or a list of checkboxes with options like "Corridor 1", "Corridor 2", "Corridor 3".
        *   `sensors`: A dictionary-like input with key-value pairs for sensor types and quantities (e.g., `{"camera": 10, "lidar": 5}`).
        *   `storage`: A text input for storage solutions (e.g., "Cloud-based, 1 year retention").
        *   `vendor_hints`: A multi-select dropdown or a list of checkboxes with options for vendors (e.g., "Vendor A", "Vendor B", "Vendor C").
    *   A "Submit for Analysis" button.

2.  **Analysis Results Display:**
    *   After submitting the brief, the UI should display the analysis results returned from the VeritAI service.
    *   The results will include:
        *   `decision`: The final decision (e.g., "Approved", "Rejected").
        *   `summary`: A summary of the decision.
        *   `trace_id`: An ID for the decision trace.
    *   The UI should present this information in a clear and visually appealing way. Use cards, icons, and different colors to represent the decision.

3.  **Trace Visualization:**
    *   A dedicated section or a modal to visualize the decision-making trace.
    *   The trace is a list of protocol events, where each event has a `type`, `agent`, `message`, and `timestamp`.
    *   Display the trace as a timeline or a sequence of steps. Each step should show the agent involved, the action taken, and the timestamp.
    *   Use icons to represent different agent types (e.g., a brain for the reasoning agent, a shield for the security agent).

**Backend and API Integration:**

*   **Backend:** Use Firestore to store the analysis results and traces.
*   **API Integration:**
    *   When the user submits the project brief, the backend should make a POST request to the following endpoint: `https://veritai-smart-city-r5uzf6jgla-uc.a.run.app/analyze`
    *   The request body should be a JSON object with the project brief.
    *   The backend should store the response from the VeritAI service in Firestore.
    *   The backend should also fetch the trace data from the VeritAI service using the `trace_id` and the `/trace/{trace_id}` endpoint, and store it in Firestore.

**Styling and UI/UX:**

*   **Theme:** Modern, sharp, and professional. Use a dark theme with accents of blue and green.
*   **Framework:** Use React with Material-UI or a similar modern component library.
*   **Layout:** A single-page application (SPA) with a clean and intuitive layout.
*   **Visualizations:** Use charts or graphs to visualize sensor data if possible.