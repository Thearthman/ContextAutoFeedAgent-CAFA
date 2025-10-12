# MEMORYTOOL_MEMORY.md - Memory Tool Internal Knowledge

**Last Updated**: October 2025  
**Core Model**: sentence-transformers/all-MiniLM-L6-v2  
**Storage**: JSON file-based with numpy arrays

## 🎯 Purpose

Internal technical knowledge for Memory Tool development. For user docs, see MEMORY_TOOL_README.md.

---

## 🔧 Core Architecture

### Components
```
memory_tool/
├── embeddings.py       # SentenceTransformer wrapper
├── memory_store.py     # Storage + retrieval + decay
├── decay.py            # (placeholder for future)
└── api/
    ├── memory_manager.py   # Coordinator layer
    └── memory_api.py       # FastAPI endpoints
```

### Data Flow
```
Text → EmbeddingGenerator → 384-dim vector → MemoryStore → JSON file
Query → Vector → Cosine similarity → Top-K results
```

---

## 📊 Technical Specs

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: ~1000 sentences/sec on CPU
- **Size**: ~90MB
- **Language**: English (multilingual variant available)

### Memory Structure
```json
{
  "text": "记忆内容",
  "embedding": [0.1, 0.2, ...],  // 384 floats
  "importance": 0.9,              // 0-1 scale
  "timestamp": "2025-10-12T10:30:00"
}
```

### Decay Formula
```python
decay_factor = 0.5 ** (days_passed / half_life_days)
new_importance = old_importance * decay_factor
```
- Default half-life: 7 days
- Exponential decay curve
- Mimics Ebbinghaus forgetting curve

---

## 🐛 Troubleshooting

### Import Errors
```python
# Wrong (from obsidian_memory_tool):
from memory_tool.memory_store import MemoryStore

# Correct (in CAFA):
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from memory_tool.memory_store import MemoryStore
```

### Model Download Issues
```bash
# Set mirror if HuggingFace blocked
export HF_ENDPOINT=https://hf-mirror.com

# Manual download location
~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2
```

### JSON File Corruption
```python
# Backup before decay operations
import shutil
shutil.copy("memory_data.json", "memory_data.backup.json")
```

### Slow Similarity Search
- **Issue**: O(n) linear search for each query
- **Solution**: Use ChromaDB or FAISS for >1000 memories
- **Current**: Acceptable for <500 memories

---

## 💡 Development Tips

### Testing Workflow
```bash
# Quick test
python test_memory_basic.py

# API server
python run_memory_api.py

# Manual test
python -c "from src.memory_tool.memory_store import MemoryStore; ..."
```

### API Endpoints
```
POST /store?text=...     # Add memory
GET  /recall?query=...   # Search memories
POST /decay              # Trigger decay
```

### Performance Notes
- **First load**: ~2-3 seconds (model download)
- **Subsequent**: <100ms (model cached)
- **Embedding**: ~10ms per text
- **Search**: ~1ms per 100 memories

---

## 🔍 Known Issues

### Expected Behaviors
1. **First run slow**: Model downloads ~90MB
2. **Decay has no effect on new memories**: Days passed ≈ 0
3. **JSON file grows**: No auto-cleanup (by design)

### Actual Bugs
- None currently known

---

## 📋 Migration Notes (from obsidian_memory_tool)

### Changes Made
- Moved from `obsidian_memory_tool/` to `ContextAutoFeedAgent-CAFA/src/`
- Updated imports to use `sys.path` injection
- Merged requirements into main `requirements.txt`
- Created `run_memory_api.py` launcher
- Added `test_memory_basic.py` for quick validation

### File Mapping
```
obsidian_memory_tool/memory_tool/  → src/memory_tool/
obsidian_memory_tool/api/          → src/memory_tool/api/
obsidian_memory_tool/tests/        → tests/
obsidian_memory_tool/requirements.txt → merged into main
```

---

## 🚀 Future Improvements

### High Priority
- [ ] ChromaDB integration for scalability
- [ ] Batch embedding for multiple texts
- [ ] Memory deduplication logic
- [ ] Auto-importance scoring (based on content)

### Medium Priority
- [ ] Memory categories/tags
- [ ] Export to Obsidian markdown
- [ ] Configurable decay curves
- [ ] Memory merge/consolidation

### Low Priority
- [ ] Multi-language support
- [ ] Image memory support
- [ ] Graph-based memory connections

---

## 📝 Configuration

### Default Values
```python
# embeddings.py
model_name = "all-MiniLM-L6-v2"

# memory_store.py
path = "memory_data.json"
importance = 1.0
half_life_days = 7.0
top_k = 3
```

### Environment Variables
```bash
# Optional: Custom model cache
export SENTENCE_TRANSFORMERS_HOME=/path/to/cache

# Optional: HuggingFace token (for private models)
export HF_TOKEN=your_token_here
```

---

## 🔗 Integration Points

### With Gemma LLM
```python
# Use memory as context for LLM
memories = store.search(user_query, top_k=3)
context = "\n".join([m["text"] for m in memories])
prompt = f"Context:\n{context}\n\nQuestion: {user_query}"
```

### With Obsidian
- Parse markdown files → extract key sentences → store as memories
- On note open → search related memories → display in sidebar
- Periodic decay → update memory importance

---

**Note**: Update this file when:
- API endpoints change
- Performance issues discovered
- Integration patterns established
- Bug fixes implemented

