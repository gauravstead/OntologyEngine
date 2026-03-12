"""
Phase 4.2: Algorithm Cron Jobs (Neo4j GDS)
Server-side graph algorithms executed off-peak as scheduled jobs.
Each algorithm writes pre-calculated scores back to node properties
so operational queries stay O(1).
"""
from datetime import datetime
from typing import Dict, Any, List
from database import neo4j_db


class GraphAlgorithms:
    """
    Encapsulates all Neo4j Graph Data Science (GDS) cron job operations.
    Each method corresponds to a specific algorithm from the architecture doc.
    """

    # ──────────────────────────────────────────────
    # 4.2.2 — Temporal Path Precalculation
    # ──────────────────────────────────────────────
    @staticmethod
    def precalculate_temporal_paths() -> Dict[str, Any]:
        """
        Flatten complex temporal logic into static spatial metrics.
        Marks edges as 'active' or 'expired' based on valid_from/valid_until
        windows so traversals (-[:DEPENDENT_ON]->) remain O(1).
        """
        now = datetime.utcnow().isoformat()

        # Step 1: Mark all edges with a computed `is_active` boolean property.
        cypher_mark_active = """
        MATCH ()-[r]->()
        WHERE r.valid_from IS NOT NULL AND r.valid_until IS NOT NULL
        SET r.is_active = (r.valid_from <= datetime($now) AND r.valid_until >= datetime($now))
        RETURN count(r) AS edges_processed
        """

        # Step 2: For edges with no temporal bounds, assume always active.
        cypher_mark_unbounded = """
        MATCH ()-[r]->()
        WHERE r.valid_from IS NULL OR r.valid_until IS NULL
        SET r.is_active = true
        RETURN count(r) AS edges_processed
        """

        result_bounded = neo4j_db.query(cypher_mark_active, parameters={"now": now})
        result_unbounded = neo4j_db.query(cypher_mark_unbounded)

        bounded_count = result_bounded[0]["edges_processed"] if result_bounded else 0
        unbounded_count = result_unbounded[0]["edges_processed"] if result_unbounded else 0

        print(f"[GDS] Temporal paths precalculated: {bounded_count} bounded, {unbounded_count} unbounded.")
        return {"bounded": bounded_count, "unbounded": unbounded_count}

    # ──────────────────────────────────────────────
    # 4.2.3 — Temporal Relevance PageRank
    # ──────────────────────────────────────────────
    @staticmethod
    def compute_temporal_pagerank() -> Dict[str, Any]:
        """
        Calculate PageRank using only active temporal windows to surface
        entities currently exerting structural importance.
        Uses Neo4j GDS projected graph filtered by is_active edges.
        """
        # Step 1: Create a projected in-memory graph of only active edges.
        cypher_project = """
        CALL gds.graph.project.cypher(
            'temporal_active_graph',
            'MATCH (n) RETURN id(n) AS id',
            'MATCH (s)-[r]->(t) WHERE r.is_active = true RETURN id(s) AS source, id(t) AS target'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        # Step 2: Run PageRank on the projected graph.
        cypher_pagerank = """
        CALL gds.pageRank.write('temporal_active_graph', {
            writeProperty: 'temporal_pagerank',
            maxIterations: 20,
            dampingFactor: 0.85
        })
        YIELD nodePropertiesWritten, ranIterations
        RETURN nodePropertiesWritten, ranIterations
        """

        # Step 3: Drop the in-memory graph to free resources.
        cypher_drop = """
        CALL gds.graph.drop('temporal_active_graph', false)
        """

        project_result = neo4j_db.query(cypher_project)
        pagerank_result = neo4j_db.query(cypher_pagerank)
        neo4j_db.query(cypher_drop)

        node_count = project_result[0]["nodeCount"] if project_result else 0
        props_written = pagerank_result[0]["nodePropertiesWritten"] if pagerank_result else 0

        print(f"[GDS] Temporal PageRank: {props_written} scores written across {node_count} nodes.")
        return {"nodes_projected": node_count, "scores_written": props_written}

    # ──────────────────────────────────────────────
    # 4.2.4 — Impact Radius Precomputation
    # ──────────────────────────────────────────────
    @staticmethod
    def compute_impact_radius(max_hops: int = 4) -> Dict[str, Any]:
        """
        Traverse DEPENDENT_ON chains (2-4 hops). Generate cascading risk
        scores and write them back onto source node properties.
        The risk score = count of downstream dependencies within the hop radius.
        """
        cypher_impact = """
        MATCH (n)
        WHERE EXISTS { (n)-[:DEPENDENT_ON]->() }
        CALL {
            WITH n
            MATCH path = (n)-[:DEPENDENT_ON*1..$max_hops]->(downstream)
            WHERE ALL(r IN relationships(path) WHERE r.is_active = true OR r.is_active IS NULL)
            RETURN count(DISTINCT downstream) AS downstream_count
        }
        SET n.impact_radius_score = downstream_count
        RETURN count(n) AS nodes_updated
        """

        result = neo4j_db.query(cypher_impact, parameters={"max_hops": max_hops})
        updated = result[0]["nodes_updated"] if result else 0

        print(f"[GDS] Impact radius (max {max_hops} hops): {updated} nodes scored.")
        return {"nodes_scored": updated, "max_hops": max_hops}

    # ──────────────────────────────────────────────
    # 4.2.5 — Structural Embeddings (FastRP)
    # ──────────────────────────────────────────────
    @staticmethod
    def compute_fastrp_embeddings(embedding_dimension: int = 128) -> Dict[str, Any]:
        """
        Recalculate FastRP structural vectors for the entire graph.
        Captures the topological transition matrix of the network.
        """
        # Step 1: Project full graph.
        cypher_project = """
        CALL gds.graph.project(
            'fastrp_graph',
            '*',
            '*'
        )
        YIELD graphName, nodeCount, relationshipCount
        RETURN graphName, nodeCount, relationshipCount
        """

        # Step 2: Run FastRP and write embeddings back.
        cypher_fastrp = f"""
        CALL gds.fastRP.write('fastrp_graph', {{
            embeddingDimension: {embedding_dimension},
            writeProperty: 'structural_embedding',
            iterationWeights: [0.0, 1.0, 1.0, 0.8]
        }})
        YIELD nodePropertiesWritten
        RETURN nodePropertiesWritten
        """

        # Step 3: Drop the in-memory graph.
        cypher_drop = """
        CALL gds.graph.drop('fastrp_graph', false)
        """

        project_result = neo4j_db.query(cypher_project)
        fastrp_result = neo4j_db.query(cypher_fastrp)
        neo4j_db.query(cypher_drop)

        node_count = project_result[0]["nodeCount"] if project_result else 0
        props_written = fastrp_result[0]["nodePropertiesWritten"] if fastrp_result else 0

        print(f"[GDS] FastRP: {props_written} structural embeddings written (dim={embedding_dimension}).")
        return {"nodes_projected": node_count, "embeddings_written": props_written}

    # ──────────────────────────────────────────────
    # Master Cron Runner
    # ──────────────────────────────────────────────
    @staticmethod
    def run_nightly_batch() -> Dict[str, Any]:
        """
        Execute all nightly GDS algorithms in sequence.
        Designed to be triggered off-peak by an external scheduler (cron/Cloud Scheduler).
        """
        print(f"[GDS] === Nightly Batch Started at {datetime.utcnow().isoformat()} ===")

        results = {}
        results["temporal_paths"] = GraphAlgorithms.precalculate_temporal_paths()
        results["temporal_pagerank"] = GraphAlgorithms.compute_temporal_pagerank()
        results["impact_radius"] = GraphAlgorithms.compute_impact_radius(max_hops=4)
        results["fastrp"] = GraphAlgorithms.compute_fastrp_embeddings(embedding_dimension=128)

        print(f"[GDS] === Nightly Batch Complete ===")
        return results


# Singleton
gds = GraphAlgorithms()
