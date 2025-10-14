# memory_tool/api/memory_api.py
from fastapi import FastAPI
from .memory_manager import MemoryManager

app = FastAPI(title="Obsidian AI Memory API")

memory = MemoryManager()

@app.post("/store")
def store_memory(text: str):
    """Store a memory"""
    memory.add_memory(text)
    return {"message": "Memory stored successfully"}

@app.get("/recall")
def recall_memory(query: str):
    """Retrieve similar memories"""
    results = memory.search_memory(query)
    return {"matches": results}

@app.post("/decay")
def decay_memories():
    """Trigger memory decay"""
    updated = memory.decay_memories()
    return {"message": "Memories decayed", "count": len(updated)}

