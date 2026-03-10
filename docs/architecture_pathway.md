# Global Ontology Engine: Implementation Pathway

This document outlines the strict technical pathway for implementing the Global Ontology Engine. This architecture optimizes for a local RTX 3050 (6GB VRAM) and 16GB RAM alongside GCP resources. It explicitly pivots from a standard web application to a **Tauri-based Native Desktop Application** (Rust + React) to bypass browser memory limits, eliminate middleware overhead, and provide a secure, high-performance command center.

## Phase 1: Core Schema & Environment Configuration

### 1.1 Strict Ontology Declaration
Enforce the following schema directly in Neo4j constraints and the Vertex AI input prompts.
*   **Approved Nodes**: `Nation`, `Person_Politician`, `Person_Military`, `Organization_Govt`, `Organization_Corporate`, `Military_Asset`, `Event_Conflict`, `Economic_Indicator`, `Technology_Sector`.
*   **Approved Edges**: `ALLIED_WITH`, `SANCTIONED`, `DEPLOYED_AT`, `INVESTED_IN`, `CRITICIZED`, `DEPENDENT_ON`.
*   **Node Properties**: `uid` (UUID), `canonical_name` (String), `aliases` (Array), `embedding` (Vector).
*   **Edge Properties**: `timestamp` (DateTime), `valid_from` (DateTime), `valid_until` (DateTime), `source_url` (String), `confidence_score` (Float).

### 1.2 Local Constraints Environment (RTX 3050 / 16GB RAM)
*   **Tauri Desktop Environment**: Initialize a Tauri application (`Rust` backend + `React` frontend) to act as the core orchestrator, replacing local web servers.
*   **Vector Indexing**: Implement FAISS or USearch memory-mapped indices (MMAP) to manage vector resolution off-RAM.
*   **Local PyTorch Execution**: Deploy BGE-m3 or all-MiniLM-L6-v2 quantized to 8-bit or 4-bit. The Rust backend will execute these Python scripts directly via OS-level Inter-Process Communication (IPC) (`std::process::Command`), saving ~1-2GB RAM by explicitly avoiding FastAPI/Uvicorn middleware.
*   **Local Critic LLM**: Deploy `llama.cpp` to run a Llama-3-8B-Instruct GGUF model within VRAM limits, spawned directly by Rust.

### 1.3 GCP Infrastructure
*   **Graph Database**: Provision Neo4j AuraDB with the Neo4j Graph Data Science (GDS) plugin enabled.
*   **Extraction LLM**: Configure Vertex AI API (Gemini Flash) with system prompts strictly restricted using JSON Schema.

---

## Phase 2: Ingestion & Agentic Verification

### 2.1 Asynchronous Triage
1.  Initialize background Python `asyncio` workers to pole the GDELT 2.0 JSON API, NDAP API, and strategic RSS feeds.
2.  Route payloads through deterministic keyword matching (e.g., names of bordering nations, essential minerals). Drop non-matching events instantly to save API calls.

### 2.2 LLM Structured Extraction (Vertex AI)
1.  Submit filtered text payloads to Vertex AI under "Structured Outputs" constraint.
2.  Extract JSON arrays of exact Triples containing `subject`, `subject_type`, `predicate`, `object`, `object_type`, and relative temporal context.

### 2.3 Local Agentic Verification Loop (The Critic)
1.  Validate returned Triples against the local Ontology Constraint Matrix. Reject invalid tuples (e.g., `Person_Politician` `[DEPLOYED_AT]` `Military_Asset`).
2.  For rejected Triples: route the source text and failed JSON object to the local local Llama-3-8B Critic agent.
3.  The Critic applies schema alignment. If it rectifies the error, proceed to resolution. If validation fails again, discard the extraction entirely.

---

## Phase 3: Topological & Semantic Entity Resolution

### 3.1 Identity Vector Generation
1.  **Semantic Vector ($v_{text}$)**: Generate the dense embedding representation for the canonical name and aliases of the new entity using the local BGE-m3 index.
2.  **Structural Vector ($v_{struct}$)**: Run a lookup query against Neo4j to retrieve the local Fast Random Projection (FastRP) composite embedding of the entity's 1-hop neighborhood.
3.  **Composite Calculation**: Calculate the combined Identity Vector:
    $V_{id} = \alpha v_{text} + (1-\alpha) v_{struct}$ (Initialize $\alpha = 0.6$).

### 3.2 Threshold Resolution
1.  Query the local memory-mapped FAISS index with $V_{id}$.
2.  **Cosine Similarity Branching**:
    *   If Similarity $> 0.92$: Execute a Cypher query to append the incoming string as a new element in the `aliases` property of the existing matched node. Do not create a new graph entity.
    *   If Similarity $\leq 0.92$: Execute a Cypher query to instantiate a fully distinct node using the mapped ontology.

---

## Phase 4: Predictable Graph Storage & Nightly Compute

### 4.1 Storage Commit 
1.  Queue resolved nodes and structured edges to write batches.
2.  Perform an ACID transactional commit to Neo4j AuraDB over HTTP.

### 4.2 Algorithm Cron Jobs (Neo4j GDS)
1.  Execute server-side graph algorithms off-peak.
2.  **Temporal Relevance**: Calculate PageRank using active temporal windows (`valid_from` & `valid_until`) to surface entities currently exerting structural importance.
3.  **Impact Radius Precomputation**: Traverse `DEPENDENT_ON` chains using graph traversals. Generate 2 to 4-hop cascading risk scores to expose supply chain or strategic bottleneck vulnerabilities. Write these pre-calculated integer scores back to the source node metrics.

---

## Phase 5: Tauri Native Command Center (Frontend)

### 5.1 Framework & Core Engine
1.  **Tauri Integration**: Wrap the React/Tailwind UI in a Tauri container. This surfaces the application as a secure, standalone `.exe`/`.deb` native desktop app, bypassing browser tab V8 memory limits.
2.  **Rust Backend Sync**: Use Tauri's Rust backend to maintain the persistent Neo4j connection, paginating large graph payloads centrally before dispatching them to the React frontend to prevent UI thread freezing.
3.  **State Management**: Deploy centralized state management (Zustand) to sync insights injected by the Rust IPC to dashboard widgets.

### 5.2 Insight-Driven Usability Architecture
1.  **Actionable Intelligence Layer**: Default to structured data tables, ranked anomalies, and timeline heatmaps. Abstract the global graph away until explicitly requested.
2.  **Strategic Watchlists**: Implement real-time ticker feeds of critical entities (e.g., specific ports, bordering military assets) with calculated threat/opportunity scores.
3.  **On-Demand Topology (Graph Inspector)**: Hook entity click events to open a contextual side-panel or modal. Pull the localized pre-calculated impact radius and precisely render an isolated 2-hop ego-graph for the selected entity using crisp, interactive 2D SVGs, explicitly avoiding 3D hairball visualizations.

### 5.3 Ministry Compartmentalization
1.  Enforce Role-Based Access Views (`/mod`, `/mof`, `/mea`). 
2.  Bind isolated endpoint queries exclusively fetching targeted intelligence (e.g. `MATCH (m:Military_Asset)-[r:DEPLOYED_AT]->(l:Location)`) preventing UI pollution and optimizing query response.
