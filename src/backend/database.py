import os
import faiss
import numpy as np
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-aura-db.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
            print("Successfully established Neo4j connection.")
        except Exception as e:
            print(f"Failed to create the Neo4j driver: {e}")

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print(f"Query failed: {query} with error {e}")
        finally:
            if session is not None:
                session.close()
        return response


class FAISSManager:
    def __init__(self, index_path="vector_index.faiss", dimension=384): # Default dimension for all-MiniLM-L6-v2
        self.index_path = index_path
        self.dimension = dimension
        
        # We use standard inner product for cosine similarity (vectors must be normalized)
        self.index = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            print(f"Loaded existing FAISS index from {self.index_path}")
        else:
            self.index = faiss.IndexFlatIP(self.dimension)
            print(f"Created new FAISS index with dimension {self.dimension}")

    def add_vectors(self, vectors: np.ndarray, save: bool = True):
        # Normalize for cosine similarity
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        if save:
            self.save_index()

    def search(self, query_vector: np.ndarray, k: int = 10):
        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, k)
        return distances, indices

    def save_index(self):
        faiss.write_index(self.index, self.index_path)


neo4j_db = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
faiss_index = FAISSManager()
