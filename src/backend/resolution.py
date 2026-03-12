import numpy as np
from database import faiss_index, neo4j_db
from embeddings import embedder

class ResolutionEngine:
    """
    Handles Topological and Semantic Entity Resolution (Phase 3).
    """

    def __init__(self):
        # We need a way to map FAISS indices back to Neo4j nodes.
        # In a real system, you'd store this in Redis or memory.
        # We mock a simple array where index == FAISS index ID
        self.mock_index_to_canonical = []
        self.mock_index_to_aliases = []

    def resolve_entity(self, incoming_name: str, incoming_type: str) -> dict:
        """
        Executes the resolution cascade:
        1. Generate v_text
        2. Semantic Search (mock map)
        3. Exact Match vs Threshold Branching
        """
        # 1. Generate Semantic Vector
        v_text = embedder.embed_text(incoming_name)
        vector_np = np.array([v_text], dtype=np.float32)

        action = "CREATE_NEW_NODE"
        matched_canonical = None
        similarity_score = 0.0

        if faiss_index.index is not None and faiss_index.index.ntotal > 0:
            # 2. Primary Semantic Search (Top-K)
            distances, indices = faiss_index.search(vector_np, k=min(10, faiss_index.index.ntotal))
            
            # 3. Branching Logic
            for i, faiss_id in enumerate(indices[0]):
                if faiss_id == -1 or faiss_id >= len(self.mock_index_to_canonical):
                     continue # Invalid index
                     
                db_canonical = self.mock_index_to_canonical[faiss_id]
                db_aliases = self.mock_index_to_aliases[faiss_id]
                score = distances[0][i]

                # Condition A: Exact Match
                if incoming_name.lower() == db_canonical.lower() or incoming_name.lower() in [a.lower() for a in db_aliases]:
                    action = "MERGE_ALIAS"
                    matched_canonical = db_canonical
                    similarity_score = 1.0 # Exact match
                    break

                # Condition B: Threshold > 0.88 + Consistent Label (We assume label maps match here for brevity)
                if score > 0.88:
                    action = "MERGE_ALIAS"
                    matched_canonical = db_canonical
                    similarity_score = float(score)
                    break

        # Execute the required Action
        if action == "CREATE_NEW_NODE":
            # Add to FAISS and our mock map
            faiss_index.add_vectors(vector_np)
            self.mock_index_to_canonical.append(incoming_name)
            self.mock_index_to_aliases.append([])
            
            # Ideally execute Neo4j MERGE here
            print(f"[Resolution] CREATE_NEW_NODE instantiated for: {incoming_name}")
            return {"action": action, "canonical_name": incoming_name, "score": None}

        elif action == "MERGE_ALIAS":
            # Just append an alias via CYPHER. Do NOT create a graph node.
            # MATCH (n) WHERE n.canonical_name = $matched_canonical SET n.aliases = n.aliases + $incoming_name
            print(f"[Resolution] MERGE_ALIAS added '{incoming_name}' to node '{matched_canonical}' (Score: {similarity_score:.3f})")
            return {"action": action, "canonical_name": matched_canonical, "score": similarity_score}

# Singleton instance
resolver = ResolutionEngine()
