"""
Phase 4.1: Predictable Graph Storage
Handles batch queuing of resolved nodes and edges, then performs
ACID transactional commits to Neo4j AuraDB.
"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import neo4j_db


class WriteQueue:
    """
    Accumulates resolved nodes and edges into batches before
    flushing them in a single ACID transaction to Neo4j.
    """

    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size
        self._node_queue: List[Dict[str, Any]] = []
        self._edge_queue: List[Dict[str, Any]] = []

    @property
    def pending_nodes(self) -> int:
        return len(self._node_queue)

    @property
    def pending_edges(self) -> int:
        return len(self._edge_queue)

    def enqueue_node(self, node_type: str, canonical_name: str,
                     aliases: List[str], embedding: Optional[List[float]] = None):
        """Queue a resolved node for batch writing."""
        self._node_queue.append({
            "uid": str(uuid.uuid4()),
            "type": node_type,
            "canonical_name": canonical_name,
            "aliases": aliases,
            "embedding": embedding,
            "created_at": datetime.utcnow().isoformat(),
        })

        if len(self._node_queue) >= self.batch_size:
            self.flush_nodes()

    def enqueue_edge(self, source_uid: str, target_uid: str, edge_type: str,
                     confidence_score: float, source_url: Optional[str] = None,
                     valid_from: Optional[str] = None, valid_until: Optional[str] = None):
        """Queue a structured edge for batch writing."""
        self._edge_queue.append({
            "source_uid": source_uid,
            "target_uid": target_uid,
            "type": edge_type,
            "confidence_score": confidence_score,
            "source_url": source_url,
            "timestamp": datetime.utcnow().isoformat(),
            "valid_from": valid_from,
            "valid_until": valid_until,
        })

        if len(self._edge_queue) >= self.batch_size:
            self.flush_edges()

    def flush_nodes(self) -> int:
        """
        Perform an ACID transactional commit of all queued nodes to Neo4j.
        Uses UNWIND for efficient batch insertion.
        """
        if not self._node_queue:
            return 0

        count = len(self._node_queue)

        # Cypher UNWIND batch — each node gets its own label via APOC or
        # we use a generic merge and set label post-hoc.
        # For strict typing, we write per-type batches.
        nodes_by_type: Dict[str, List[Dict]] = {}
        for node in self._node_queue:
            t = node["type"]
            nodes_by_type.setdefault(t, []).append(node)

        for node_type, batch in nodes_by_type.items():
            cypher = f"""
            UNWIND $batch AS row
            MERGE (n:{node_type} {{uid: row.uid}})
            SET n.canonical_name = row.canonical_name,
                n.aliases = row.aliases,
                n.created_at = datetime(row.created_at)
            """
            neo4j_db.query(cypher, parameters={"batch": batch})

        self._node_queue.clear()
        print(f"[Storage] Flushed {count} nodes to Neo4j.")
        return count

    def flush_edges(self) -> int:
        """
        Perform an ACID transactional commit of all queued edges to Neo4j.
        Uses UNWIND for efficient batch insertion.
        """
        if not self._edge_queue:
            return 0

        count = len(self._edge_queue)

        edges_by_type: Dict[str, List[Dict]] = {}
        for edge in self._edge_queue:
            t = edge["type"]
            edges_by_type.setdefault(t, []).append(edge)

        for edge_type, batch in edges_by_type.items():
            cypher = f"""
            UNWIND $batch AS row
            MATCH (src {{uid: row.source_uid}})
            MATCH (tgt {{uid: row.target_uid}})
            MERGE (src)-[r:{edge_type}]->(tgt)
            SET r.confidence_score = row.confidence_score,
                r.source_url = row.source_url,
                r.timestamp = datetime(row.timestamp),
                r.valid_from = CASE WHEN row.valid_from IS NOT NULL THEN datetime(row.valid_from) ELSE null END,
                r.valid_until = CASE WHEN row.valid_until IS NOT NULL THEN datetime(row.valid_until) ELSE null END
            """
            neo4j_db.query(cypher, parameters={"batch": batch})

        self._edge_queue.clear()
        print(f"[Storage] Flushed {count} edges to Neo4j.")
        return count

    def flush_all(self) -> Dict[str, int]:
        """Flush both node and edge queues."""
        nodes_flushed = self.flush_nodes()
        edges_flushed = self.flush_edges()
        return {"nodes_flushed": nodes_flushed, "edges_flushed": edges_flushed}


# Singleton
write_queue = WriteQueue()
