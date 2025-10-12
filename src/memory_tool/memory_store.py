# memory_tool/memory_store.py
import os
import json
import numpy as np
from datetime import datetime
from .embeddings import EmbeddingGenerator


class MemoryStore:
    """
    长期记忆存储系统：
    - 添加新记忆
    - 搜索相似记忆
    - 对旧记忆进行时间衰减
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
        添加新的记忆。
        importance 是一个权重，表示记忆的重要性（0-1）。
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
        根据语义相似度检索最相关的记忆。
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
        根据时间衰减公式降低记忆重要性。
        越久远的记忆重要性越低。
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
    store.add_memory("我在考试中错了牛顿第三定律的题", importance=0.9)
    store.add_memory("我在复习时发现自己不理解热力学第二定律", importance=0.8)

    print("\n🔍 搜索相关记忆：")
    print(store.search("复习热力学"))

    print("\n🧮 衰减记忆：")
    store.decay()
    print(store.memories)

