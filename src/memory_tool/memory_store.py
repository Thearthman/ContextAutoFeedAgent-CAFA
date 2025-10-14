# memory_tool/memory_store.py
import os
import json
import numpy as np
from datetime import datetime
from .embeddings import EmbeddingGenerator


class MemoryStore:
    """
    Long-term memory storage system:
    - Add new memories
    - Search similar memories
    - Apply time decay to old memories
    """

    def __init__(self, path: str = "memory_data.json"):
        self.path = path
        self.model = EmbeddingGenerator()
        self.memories = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, ensure_ascii=False, indent=2)

    def add_memory(self, text: str, importance: float = 1.0):
        """
        Add a new memory.
        importance is a weight representing the memory's importance (0-1).
        """
        embedding = self.model.embed(text).tolist()
        memory = {
            "text": text,
            "embedding": embedding,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        self.memories.append(memory)
        self._save()
        return memory

    def search(self, query: str, top_k: int = 3):
        """
        Retrieve the most relevant memories based on semantic similarity.
        """
        if not self.memories:
            return []

        query_vec = self.model.embed(query)
        scores = []

        for mem in self.memories:
            emb = np.array(mem["embedding"])
            sim = np.dot(query_vec, emb) / (np.linalg.norm(query_vec) * np.linalg.norm(emb))
            scores.append((mem, sim))

        results = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        return [{"text": m["text"], "similarity": round(s, 3)} for m, s in results]

    def decay(self, half_life_days: float = 7.0):
        """
        Reduce memory importance based on time decay formula.
        Older memories have lower importance.
        """
        now = datetime.now()
        for mem in self.memories:
            t = datetime.fromisoformat(mem["timestamp"])
            days_passed = (now - t).days
            decay_factor = 0.5 ** (days_passed / half_life_days)
            mem["importance"] *= decay_factor
        self._save()
        return self.memories


if __name__ == "__main__":
    store = MemoryStore()
    store.add_memory("I got Newton's third law wrong in the exam", importance=0.9)
    store.add_memory("I found I don't understand the second law of thermodynamics during review", importance=0.8)

    print("\n🔍 Search related memories:")
    print(store.search("thermodynamics review"))

    print("\n🧮 Decay memories:")
    store.decay()
    print(store.memories)

