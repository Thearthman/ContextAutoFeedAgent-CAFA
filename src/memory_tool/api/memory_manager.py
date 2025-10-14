# memory_tool/api/memory_manager.py
from ..memory_store import MemoryStore

class MemoryManager:
    """
    MemoryManager coordinates long-term memory module usage:
    - Add new memories
    - Search memories
    """

    def __init__(self):
        self.store = MemoryStore()

    def add_memory(self, text: str):
        """Store a memory"""
        return self.store.add_memory(text)

    def search_memory(self, query: str, top_k: int = 3):
        """Search for most relevant memories"""
        return self.store.search(query, top_k=top_k)

    def decay_memories(self):
        """Execute memory decay"""
        return self.store.decay()

