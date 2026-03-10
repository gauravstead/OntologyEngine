# Global Ontology Engine: Implementation Pathway

This document outlines the strict technical pathway for implementing the Global Ontology Engine. This architecture optimizes for a hybrid deployment, leveraging local hardware (RTX 3050 6GB VRAM, 16GB RAM) alongside GCP resources. It pivots to a robust **Web Application** (Next.js Frontend + Python/FastAPI Backend) combined with cloud-based background processing, ensuring scalability, stability, and strict adherence to hardware and network limits.

## Phase 1: Core Schema & Environment Configuration

### 1.1 Strict Ontology Declaration
Enforce the following schema directly in Neo4j constraints and the Vertex AI input prompts.
*   **Approved Nodes**: `Nation`, `Person_Politician`, `Person_Military`, `Organization_Govt`, `Organization_Corporate`, `Military_Asset`, `Event_Conflict`, `Economic_Indicator`, `Technology_Sector`.
*   **Approved Edges**: `ALLIED_WITH`, `SANCTIONED`, `DEPLOYED_AT`, `INVESTED_IN`, `CRITICIZED`, `DEPENDENT_ON`.
*   **Node Properties**: `uid` (UUID), `canonical_name` (String), `aliases` (Array), `embedding` (Vector).
*   **Edge Properties**: `timestamp` (DateTime), `valid_from` (DateTime), `valid_until` (DateTime), `source_url` (String), `confidence_score` (Float). *(Constraint: Keep temporal logic to a minimum on deep traversals (3+ hops) to avoid exponential query slowdowns. Rely heavily on Graph Data Science cron jobs to pre-calculate these into static properties.)*

### 1.2 Local Constraints Environment (RTX 3050 / 16GB RAM)
*   **Web Application Architecture**: Initialize a Next.js frontend and a lightweight Python FastAPI backend to act as the core orchestrator. HTTP/WebSockets provide a stable IPC mechanism with minimal memory overhead compared to raw OS process spawning.
*   **Vector Indexing**: Implement FAISS or USearch memory-mapped indices (MMAP) to manage vector resolution off-RAM.
*   **Local PyTorch Execution (CPU-Bound)**: Execute BGE-m3 or all-MiniLM-L6-v2 embeddings explicitly on the CPU to leave the 6GB VRAM entirely free.
*   **Local LLM (Analytical/Query)**: Deploy `llama.cpp` to run a **Llama-3.2-3B-Instruct** GGUF model within a strict ~2.5GB VRAM footprint. This leaves enough VRAM free for Next.js UI rendering and OS overhead to prevent OOM crashes.

### 1.3 Cloud Infrastructure (GCP / Serverless)
*   **Graph Database**: Provision Neo4j AuraDB with the Neo4j Graph Data Science (GDS) plugin enabled.
*   **Extraction & Verification LLMs**: Configure Vertex AI API (Gemini Flash) with system prompts strictly restricted using JSON Schema. Deploy the "Critic" verification loop entirely server-side (using Gemini Flash or a high-throughput endpoint) to prevent overwhelming the local machine's processing queues.

---

## Phase 2: Ingestion & Agentic Verification

### 2.1 Cloud-Based Asynchronous Triage
1.  Initialize background Python `asyncio` workers on **GCP Cloud Run or Compute Engine** (running 24/7 independently of the local desktop) to poll the GDELT 2.0 JSON API, NDAP API, and strategic RSS feeds.
2.  Route payloads through deterministic keyword matching (e.g., names of bordering nations, essential minerals). Drop non-matching events instantly to save API calls.

### 2.2 LLM Structured Extraction (Vertex AI)
1.  Submit filtered text payloads to Vertex AI under "Structured Outputs" constraint.
2.  Extract JSON arrays of exact Triples containing `subject`, `subject_type`, `predicate`, `object`, `object_type`, and relative temporal context.

### 2.3 Cloud Agentic Verification Loop (The Critic)
1.  **Deterministic Validation**: Validate returned Triples against the Ontology Constraint Matrix. Reject invalid tuples (e.g., `Person_Politician` `[DEPLOYED_AT]` `Military_Asset`).
2.  **Server-Side Critic Routing**: For rejected Triples, instantly route the source text and failed JSON object to the cloud-based Critic agent. Do NOT route continuous ingestion validation data back to the local desktop.
3.  **Correction & Discard**: The Critic applies schema alignment. If it rectifies the error, proceed to resolution. If validation fails again, discard the extraction entirely.

---

## Phase 3: Topological & Semantic Entity Resolution

### 3.1 Vector Generation & Cascading Retrieval
1.  **Semantic Vector ($v_{text}$)**: Generate the dense embedding representation for the canonical name and aliases of the new entity using the local text embedding model (e.g., all-MiniLM-L6-v2 or BGE-m3).
2.  **Primary Semantic Search**: Query the local memory-mapped FAISS index with $v_{text}$ to retrieve the Top-K (e.g., K=10) candidate nodes based on standard Cosine Similarity.
3.  **Exact Property Matching**: Cross-reference the incoming entity against exact property matches (e.g., `canonical_name` and explicit `aliases`) of the Top-K candidate nodes.

### 3.2 Threshold Resolution & Merging
1.  **Semantic & Textual Resolution**: Execute resolution based on explicit textual matches and semantic similarity rather than structural transition matrices (which require the node to already exist in the graph).
2.  **Resolution Branching**:
    *   If Exact Property Match OR (Semantic Similarity $> 0.88$ AND consistent ontology labels): Execute a Cypher query to append the incoming string as a new element in the `aliases` property of the existing matched node. Do not create a new graph entity.
    *   Otherwise: Execute a Cypher query to instantiate a fully distinct node using the mapped ontology.

---

## Phase 4: Predictable Graph Storage & Nightly Compute

### 4.1 Storage Commit 
1.  Queue resolved nodes and structured edges to write batches.
2.  Perform an ACID transactional commit to Neo4j AuraDB over HTTP.

### 4.2 Algorithm Cron Jobs (Neo4j GDS)
1.  Execute server-side graph algorithms off-peak.
2.  **Temporal Path Precalculation**: Calculate active temporal paths using `valid_from` & `valid_until` windows, flattening complex temporal logic into static spatial metrics to ensure standard traversals (`-[:DEPENDENT_ON]->`) remain $O(1)$ fast during operational hours.
3.  **Temporal Relevance**: Calculate PageRank using active temporal windows to surface entities currently exerting structural importance.
4.  **Impact Radius Precomputation**: Traverse `DEPENDENT_ON` chains using graph traversals. Generate 2 to 4-hop cascading risk scores to expose supply chain or strategic bottleneck vulnerabilities. Write these pre-calculated integer scores back to the source node metrics.
5.  **Structural Embeddings (FastRP)**: Recalculate FastRP (Fast Random Projection) structural vectors for the entire graph. This captures the topological transition matrix of the network, enabling complex structural queries that are updated dynamically as the graph grows.

---

## Phase 5: Web Application Command Center (Frontend)

### 5.1 Framework & Core Engine
1.  **Web Architecture**: Build the frontend using React/Next.js and Tailwind UI. This provides a highly accessible, cross-platform command center that connects to the local FastAPI backend.
2.  **Backend Sync**: Use the Python FastAPI backend to maintain the persistent Neo4j connection, paginating large graph payloads centrally before dispatching them to the React frontend to prevent browser UI thread freezing and memory exhaustion.
3.  **State Management**: Deploy centralized state management (Zustand) to sync insights injected by the FastAPI backend to dashboard widgets.

### 5.2 Insight-Driven Usability Architecture
1.  **Actionable Intelligence Layer**: Default to structured data tables, ranked anomalies, and timeline heatmaps. Abstract the global graph away until explicitly requested.
2.  **Strategic Watchlists**: Implement real-time ticker feeds of critical entities (e.g., specific ports, bordering military assets) with calculated threat/opportunity scores.
3.  **On-Demand Topology (Graph Inspector)**: Hook entity click events to open a contextual side-panel or modal. Pull the localized pre-calculated impact radius and precisely render an isolated 2-hop ego-graph for the selected entity using crisp, interactive 2D SVGs, explicitly avoiding 3D hairball visualizations.

### 5.3 Ministry Compartmentalization
1.  Enforce Role-Based Access Views (`/mod`, `/mof`, `/mea`). 
2.  Bind isolated endpoint queries exclusively fetching targeted intelligence (e.g. `MATCH (m:Military_Asset)-[r:DEPLOYED_AT]->(l:Location)`) preventing UI pollution and optimizing query response.
