# memory_tool/api/memory_api.py
from fastapi import FastAPI
from .memory_manager import MemoryManager

app = FastAPI(title="Obsidian AI Memory API")

memory = MemoryManager()

@app.post("/store")
def store_memory(text: str):
    """存储一条记忆"""
    memory.add_memory(text)
    return {"message": "Memory stored successfully"}

@app.get("/recall")
def recall_memory(query: str):
    """检索相似记忆"""
    results = memory.search_memory(query)
    return {"matches": results}

@app.post("/decay")
def decay_memories():
    """触发记忆衰减"""
    updated = memory.decay_memories()
    return {"message": "Memories decayed", "count": len(updated)}

