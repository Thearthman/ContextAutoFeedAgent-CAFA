# memory_tool/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingGenerator:
    """
    A simple embedding generator using SentenceTransformer.
    Class for generating text semantic vectors.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load lightweight vector model
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> np.ndarray:
        """
        Convert text to vector.
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")
        embedding = self.model.encode(text)
        return np.array(embedding)

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts (cosine similarity).
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(sim)


# Test
if __name__ == "__main__":
    generator = EmbeddingGenerator()
    sim = generator.similarity("Hello, how are you today?", "The weather is nice today, how are you?")
    print(f"Similarity: {sim:.3f}")

