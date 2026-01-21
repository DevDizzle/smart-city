# UrbanNexus for Ubicquia Innovation Center (UICII) - Roadmap & Implementation Plan

**Date:** January 17, 2026
**Target Audience:** Development Team
**Goal:** Adapt the UrbanNexus platform to align with the Ubicquia Innovation Center for Intelligent Infrastructure (UICII) mission and prepare a demo for Dr. Jason Hallstrom.

---

## 1. Executive Summary

* **Current State:** UrbanNexus is currently a defensive tool focused on risk governance, providing Go/No-Go decisions based on privacy, safety, and security constraints.
* **Future State (UICII Edition):** UrbanNexus will evolve into a **Strategic Infrastructure Optimization Engine**. It will not only assess risk but actively recommend the optimal mix of Ubicquia solutions (UbiCell, UbiHub, UbiGrid) to maximize community value—specifically Safety, Energy Savings, and Connectivity—within a specific geographic context.
* **The Demo Goal:** A live "Site Assessment" of an FAU campus zone (e.g., "Engineering Lab Parking") where agents debate and conclude with a recommendation like: *"Deploy UbiHub AI+ at the crosswalks for student safety, but use UbiCell on the perimeter lights to maximize energy savings."*

---

## 2. Phase 1: Knowledge Base Expansion (The "Brain")

**Objective:** Equip agents with deep knowledge of Ubicquia's specific product capabilities to enable intelligent recommendations.
**Action Item:** Ingest the following specific content into the `urbannexus-smart-city-kb` bucket:

### UbiCell (Intelligent Streetlight Control)
* **Key Concepts to Ingest:** Energy savings capabilities (up to 40%), utility-grade metering features, and tilt/vibration monitoring for storm resilience.
* **Agent Mapping:** This data will primarily power the `SustainabilitySpecialist` for calculating ROI and CO2 reduction.

### UbiHub (AP/AI & AI+)
* **Key Concepts to Ingest:** Edge AI processing capabilities (privacy-preserving), license plate recognition (LPR), public WiFi features for digital divide initiatives, and dual 4K camera specs.
* **Agent Mapping:** This data will power the `PublicSafetySpecialist` and `ConnectivitySpecialist`.

### UbiGrid (DTM+)
* **Key Concepts to Ingest:** Transformer monitoring, power quality analytics, and grid resilience features.
* **Agent Mapping:** This data will power the `GridResilienceSpecialist`.

---

## 3. Phase 2: Core Architecture & Schema (The "Foundation")

**Objective:** Refactor the system core to support the new "Value vs. Risk" debate logic before implementing specific agents.

### 2.1 Update Decision Schemas
The system must be updated to understand goals, constraints, and geographic context.
* **Action:** Modify `schemas/decision_brief.py` and `common.py` to include:
    * **`goals`**: (e.g., public safety, energy savings, digital equity).
    * **`constraints`**: (e.g., budget, privacy sensitivity).
    * **`Zone` Definition**: A structured object representing the physical site (e.g., dimensions, existing poles, backhaul status).

### 2.2 Orchestration Refactor
The current linear risk-check workflow must be replaced with a multi-stage pipeline.
* **Action:** Rewrite `orchestration/graph.py` to implement a 4-stage state machine:
    1.  **Site Assessment:** Fetch zone data.
    2.  **Value Analysis:** "Advocate" agents propose solutions.
    3.  **Risk Analysis:** "Critic" agents review proposals.
    4.  **Synthesis:** Final trade-off analysis and recommendation.

### 2.3 Mock GIS Data
Since no live GIS database exists, we need a simulation layer.
* **Action:** Create `data/mock_zones.json` to store hardcoded attributes for demo zones (e.g., "Engineering Lab Parking" has Fiber Backhaul and High Pedestrian Traffic).

---

## 4. Phase 3: Agent Implementation (The "Team")

**Objective:** Deploy the specialized agents, shifting from a pure "Critic" model to an "Advocate vs. Critic" model.

### 3.1 New Paradigm: Advocates vs. Critics
*   **Advocates (Value Specialists):** New agents that scan for *opportunity*. They proactively suggest hardware to meet goals.
*   **Critics (Risk Specialists):** Existing agents (Privacy, OT Security) that scan for *liability*. They veto or condition the proposals.

### 3.2 New Agent: SiteViabilityAgent (The "Geographer")
*   **Role:** The interface to the GIS layer.
*   **Implementation Logic:** Reads `mock_zones.json` and populates the `Zone` object in the orchestration state.

### 3.3 New Agent: SustainabilitySpecialist (Advocate)
*   **Role:** Environmental and Economic impact calculator.
*   **Implementation Logic:**
    * Analyze proposed UbiCell deployments to estimate kilowatt-hour (kWh) savings.
    * Highlight aesthetic/maintenance value of device consolidation.

### 3.4 New Agent: ConnectivitySpecialist (Advocate)
*   **Role:** Digital Equity and Connectivity evaluator.
*   **Implementation Logic:**
    * Analyze UbiHub AP proposals for WiFi coverage radius.
    * Cross-reference with zone demographics to score "digital equity value".

---

## 5. Phase 4: Web App Demo (The "Wow" Factor)

**Technology Stack Recommendation:** Modern frontend framework (e.g., React/Next.js) with mapping libraries (Leaflet/Mapbox) and a real-time backend (Firebase).

**Target User Experience:**
* **Map Interface:** Interactive map centered on the FAU Campus.
* **Zone Selection:** Users click defined polygons.
* **Context Panel:** Displays simulated live data for the selected zone.
* **"Run Analysis" Action:** Triggers the UrbanNexus multi-agent workflow.
* **Live Thinking Trace:** dedicated panel streaming agent "thoughts".
* **Recommendation Overlay:** Map updates with icons indicating optimal unit locations.

---

## 6. Immediate Next Steps

1.  **Schema & State:** Update `schemas/` to define the `Zone` and `Goal` structures.
2.  **Orchestration:** Refactor `orchestration/graph.py` to support the 4-stage pipeline.
3.  **Mock Data:** Create `data/mock_zones.json` with valid "Engineering Lab" data.
4.  **Data Ingestion:** Execute import scripts for Ubicquia docs.
5.  **Agent Logic:** Implement `SiteViabilityAgent` and `SustainabilitySpecialist`.
6.  **UI Scaffold:** Initialize the web application framework.
