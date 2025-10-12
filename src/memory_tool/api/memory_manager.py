# memory_tool/api/memory_manager.py
from ..memory_store import MemoryStore

class MemoryManager:
    """
    MemoryManager 负责协调长期记忆模块的使用：
    - 添加新记忆
    - 搜索记忆
    """

    def __init__(self):
        self.store = MemoryStore()

    def add_memory(self, text: str):
        """存储一段记忆"""
        return self.store.add_memory(text)

    def search_memory(self, query: str, top_k: int = 3):
        """搜索最相关记忆"""
        return self.store.search(query, top_k=top_k)

    def decay_memories(self):
        """执行记忆衰减"""
        return self.store.decay()

