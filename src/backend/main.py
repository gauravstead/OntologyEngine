from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid

# Engine Imports
from schema import NationNode, EventConflictNode
from database import neo4j_db, faiss_index
from embeddings import embedder

app = FastAPI(
    title="Global Ontology Engine API",
    description="Core orchestrator for semantic extraction, FAISS vector indexing, and Neo4j querying.",
    version="1.0.0",
)

# Allow Next.js frontend to interact with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
def shutdown_event():
    neo4j_db.close()


@app.get("/health")
async def health_check():
    # Simple check to see if dependencies loaded without crashing
    db_status = "connected" if neo4j_db is not None else "disconnected"
    faiss_status = "ready" if faiss_index.index is not None else "uninitialized"
    embedder_status = "ready" if embedder.model is not None else "uninitialized"

    return {
        "status": "ok", 
        "message": "Global Ontology Engine backend is running.",
        "neo4j": db_status,
        "faiss": faiss_status,
        "embedder": embedder_status
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Global Ontology Engine API."}

# Mock Endpoint for verification
@app.post("/mock_ingest/nation", response_model=NationNode)
async def mock_ingest_nation(name: str):
    """
    Simulates ingesting a new Nation node, generating an embedding, 
    and returning the strict Pydantic model for validation.
    """
    uid_val = str(uuid.uuid4())
    vector = embedder.embed_text(name)
    
    nation = NationNode(
        uid=uid_val,
        canonical_name=name,
        aliases=[name.lower()],
        embedding=vector
    )
    return nation

# Integration Pipeline Endpoint
from ingestion import IngestionPipeline
from critic import TheCritic
from resolution import resolver

@app.post("/ingest/trigger")
async def trigger_ingestion():
    """
    Triggers the mocked ingestion pipeline, routing payloads through the Critic 
    and resolving valid nodes via FAISS semantic cascade.
    """
    pipeline = IngestionPipeline()
    payloads = await pipeline.mock_poll_gdelt()
    
    results = []
    
    for payload in payloads:
        raw = payload.get("raw_extraction")
        is_valid, critic_msg = TheCritic.validate_triple(raw["subject"], raw["predicate"], raw["object"])
        
        if not is_valid:
            # Route to Critic for attempted salvation
            correction_res = TheCritic.correct_and_discard(critic_msg, raw)
            if not correction_res:
                results.append({"payload": raw["subject"]["canonical_name"], "status": "REJECTED_BY_CRITIC", "reason": critic_msg})
                continue
            
        # If valid or corrected, send to Entity Resolution (Phase 3)
        res_subject = resolver.resolve_entity(raw["subject"]["canonical_name"], raw["subject"]["type"])
        res_object = resolver.resolve_entity(raw["object"]["canonical_name"], raw["object"]["type"])
        
        results.append({
            "payload": f"{raw['subject']['canonical_name']} -> {raw['object']['canonical_name']}",
            "status": "RESOLVED_AND_QUEUED",
            "subject_action": res_subject,
            "object_action": res_object
        })
        
    return {"message": "Ingestion pipeline triggered.", "results": results}

# Phase 4: Storage & Graph Algorithms
from storage import write_queue
from graph_algorithms import gds

@app.post("/storage/flush")
async def flush_storage():
    """
    Manually flush the write queue, committing all pending nodes
    and edges to Neo4j in an ACID transaction.
    """
    result = write_queue.flush_all()
    return {
        "message": "Write queue flushed.",
        "nodes_flushed": result["nodes_flushed"],
        "edges_flushed": result["edges_flushed"],
        "pending_nodes": write_queue.pending_nodes,
        "pending_edges": write_queue.pending_edges,
    }

@app.get("/storage/status")
async def storage_status():
    """Check the current state of the write queue."""
    return {
        "pending_nodes": write_queue.pending_nodes,
        "pending_edges": write_queue.pending_edges,
    }

@app.post("/gds/nightly")
async def run_nightly_gds():
    """
    Trigger the full nightly GDS algorithm batch:
    Temporal Path Precalculation, PageRank, Impact Radius, FastRP.
    Designed to be called off-peak by an external scheduler.
    """
    results = gds.run_nightly_batch()
    return {"message": "Nightly GDS batch complete.", "results": results}

@app.post("/gds/temporal-paths")
async def run_temporal_paths():
    """Run only the temporal path precalculation algorithm."""
    return gds.precalculate_temporal_paths()

@app.post("/gds/pagerank")
async def run_pagerank():
    """Run only the temporal PageRank algorithm."""
    return gds.compute_temporal_pagerank()

@app.post("/gds/impact-radius")
async def run_impact_radius(max_hops: int = 4):
    """Run only the impact radius precomputation."""
    return gds.compute_impact_radius(max_hops=max_hops)

@app.post("/gds/fastrp")
async def run_fastrp(dimension: int = 128):
    """Run only the FastRP structural embedding recalculation."""
    return gds.compute_fastrp_embeddings(embedding_dimension=dimension)
