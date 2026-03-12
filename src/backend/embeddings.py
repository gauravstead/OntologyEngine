from sentence_transformers import SentenceTransformer

class LocalEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initialize the embedding model locally, explicitly mapped to CPU
        to save VRAM for other LLMs/Next.js as per strict architectural constraints.
        """
        print(f"Loading generic sentence transformer: {model_name} strictly on CPU.")
        # `device='cpu'` is essential to strictly enforce the no-VRAM rule. 
        self.model = SentenceTransformer(model_name, device='cpu')

    def embed_text(self, text: str) -> list[float]:
        # Encode returns a numpy array.
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# Singleton instance for the application to use
embedder = LocalEmbedder()
