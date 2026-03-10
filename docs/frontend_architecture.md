# Global Ontology Engine: Frontend Dashboard Architecture

This document defines the strict UI/UX architecture for the Global Ontology Engine, specifically designed for Government of India (GoI) decision-makers. 

**Core Philosophy:** The UI must maximize usability over cinematic aesthetics. Showing a spinning 3D globe with thousands of nodes looks impressive in a pitch but is useless for an analyst extracting tactical intelligence. The UI exists to distill a massive, unified intelligence graph (spanning geopolitics, economics, defense, tech, and climate) into **clear insights for strategy, transparency, and national advantage.**

## 1. Usability & Progressive Disclosure

The frontend operates on the principle of Progressive Disclosure. We never show the user the raw "hairball" graph or purely aesthetic 3D globes.

### 1.1 Level 1: The Executive Summary (Actionable Anomalies)
*   **The View:** A minimalist dashboard of prioritized alerts and metric cards.
*   **Purpose:** Tell the decision-maker *what changed today* that matters to India's strategic interests.
*   **Components:**
    *   **Anomaly Feed:** e.g., "73% spike in negative sentiment from Nation X regarding Indian tech sector."
    *   **Risk Indices:** Cascading supply chain risk scores (0-100) pre-computed by the Neo4j backend.
    *   **Geopolitical Activity Heatmaps:** Simple, flat 2D choropleth maps highlighting regional tension zones or data density, actively minimizing browser resource consumption.

### 1.2 Level 2: Domain-Specific Exploration (Deep Dives)
*   **The View:** Standardized, dense data tables and temporal charts (time-series).
*   **Purpose:** Allow analysts to easily parse high volumes of structured feeds (NDAP) and extracted unstructured intelligence (GDELT) filtered by their domain.
*   **Components:**
    *   **Cross-Linked Tables:** Clean, traditional data grids that list entities, recent relationship updates, and confidence scores. No visual noise.
    *   **Event Timelines:** Horizontal or vertical chronologies tracking the history of specific relationships (e.g., plotting the historical escalation timeline of a specific military deployment).

### 1.3 Level 3: The Full Graph Explorer (Global View)
*   **The View:** A dedicated, full-screen canvas displaying the entire structural graph (or large sub-graphs).
*   **Purpose:** For advanced analysts who explicitly need to see the "big picture" macro-structure of the parsed intelligence, identifying large-cluster formations, disjointed networks, or isolated entities.
*   **Components:**
    *   **2D Physics-Based Rendering:** We utilize optimized 2D physics engines (like d3-force or Sigma.js) instead of 3D WebGL. This provides a readable, interactable global topology that won't overwhelm a 16GB RAM system.
    *   **Semantic Filtering:** The full graph is unusable without strict filtering. The UI includes a robust sidebar to instantly filter nodes by explicit ontology labels (e.g., show only `Event_Conflict` and `Military_Asset` edges) or temporal bounds.

### 1.4 Level 4: The 2-Hop Graph Inspector (On-Demand Topology)
*   **The View:** A lightweight contextual sidebar or focused modal.
*   **Purpose:** Provide full systemic visibility into the direct relationships of a *single* entity, only when explicitly requested.
*   **Components:**
    *   **Ego-Graph Validation:** When an analyst clicks "Inspect Network" on a specific port, corporate entity, or politician, the UI queries the unified graph for a strict 2-hop radius.
    *   **Deterministic 2D SVG Rendering:** We render this sub-graph using mathematically positioned 2D SVGs (e.g., radial tree layouts). We explicitly ban heavy WebGL/Three.js libraries to ensure the interface never crashes on limited 16GB RAM machines and remains hyper-readable.

## 2. Ministry-Tailored Experiences

The underlying graph is a constantly updating, massive unified engine. However, the frontend interface is strictly partitioned by domain to eliminate cross-domain noise.

*   **Ministry of Defence (MoD): The Tactical View**
    *   **Focus:** Force deployments, strategic assets, and conflict thresholds.
    *   **UI Priority:** 2D tactical maps overlaid with asset groupings, calculated threat radii (impact radius), and alliance shift indicators. 
*   **Ministry of External Affairs (MEA): The Diplomatic View**
    *   **Focus:** Bilateral relations, international sentiment shifts, treaties, and sanctions.
    *   **UI Priority:** Entity relationship timelines, sentiment variation charts, and interaction histories.
*   **Ministry of Finance (MoF): The Economic View**
    *   **Focus:** Supply chain dependencies, foreign direct investment anomalies, and critical resource chokepoints.
    *   **UI Priority:** Dependency tree visualizations (showing upstream bottlenecks for domestic manufacturing), trade deficit highlights, and investment origin tracking.

## 3. Technical Constraints & Implementation Stack
*   **Framework (Web App):** Next.js (React). A standard web application built to consume data from a local Python FastAPI backend, optimized to ensure the browser strictly accesses paginated data rather than holding the entire graph in RAM.
*   **Backend Inter-Process Communication (IPC):** The FastAPI backend orchestrates local Python AI scripts and lightweight `llama.cpp` analytical endpoints (e.g. Llama-3.2-3B) using stable HTTP/WebSocket connections, avoiding the brittleness of raw OS process spawning. Embeddings run on the CPU, and heavy ingestion verification is strictly offloaded to the cloud to preserve system stability.
*   **Styling:** Tailwind CSS for a rigid, utilitarian, and high-contrast design system tailored for long sessions.
*   **State Management:** Zustand to provide lightweight, boilerplate-free state synchronization across complex dashboard widgets without React Context re-render lag.
*   **Visualization Modules:** 
    *   **Charts:** Recharts or similarly lightweight standard 2D charting libraries.
    *   **Maps:** React-Leaflet with flat vector bounds (avoiding heavy 3D vector tile processors).
    *   **Interactive Topology:** Custom React SVG implementations tailored specifically for low-node-count (under 50 nodes) ego-graphs, prioritizing layout stability over animation.
