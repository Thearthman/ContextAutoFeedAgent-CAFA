# Memory Tool - Long-term Memory System

## Overview

Memory Tool is a semantic vector-based long-term memory storage and retrieval system that supports:
- 📝 **Memory Storage**: Save text memories and generate semantic vectors
- 🔍 **Semantic Retrieval**: Retrieve most relevant memories based on query content
- ⏰ **Time Decay**: Simulate human memory forgetting curve
- 🌐 **API Interface**: Provides FastAPI RESTful API

## Project Structure

```
src/
└── memory_tool/           # Core memory module
    ├── __init__.py
    ├── embeddings.py      # Text vectorization
    ├── memory_store.py    # Memory storage and retrieval
    
    ├── decay.py           # Time decay logic
    └── api/               # API interface
        ├── __init__.py
        ├── memory_manager.py  # Memory manager
        └── memory_api.py      # FastAPI interface
tests/
└── test_memory.py         # Test file
run_memory_api.py          # API startup script
test_memory_basic.py       # Quick test script
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Main dependencies:
- `sentence-transformers`: Text vectorization
- `chromadb`: Vector database (optional)
- `fastapi`: API framework
- `uvicorn`: ASGI server

### 2. Basic Usage

#### Python API

```python
from src.memory_tool.memory_store import MemoryStore

# Create memory store
store = MemoryStore()

# Add memories
store.add_memory("I got Newton's third law wrong in the exam", importance=0.9)
store.add_memory("I found I don't understand the second law of thermodynamics during review", importance=0.8)

# Search related memories
results = store.search("review thermodynamics", top_k=3)
for result in results:
    print(f"Memory: {result['text']}")
    print(f"Similarity: {result['similarity']}")

# Execute time decay
store.decay(half_life_days=7.0)
```

#### REST API

Start API server:

```bash
# Method 1: Use startup script (recommended)
python run_memory_api.py

# Method 2: Use uvicorn directly
cd src
uvicorn memory_tool.api.memory_api:app --reload --port 8000
```

API endpoints:

**Store memory**
```bash
curl -X POST "http://localhost:8000/store?text=I learned Python programming today"
```

**Retrieve memory**
```bash
curl "http://localhost:8000/recall?query=Python learning"
```

**Trigger decay**
```bash
curl -X POST "http://localhost:8000/decay"
```

## Core Features

### 1. Semantic Vectorization (embeddings.py)

Use `sentence-transformers`' `all-MiniLM-L6-v2` model to convert text to 384-dimensional vectors.

```python
from src.memory_tool.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()

# Generate vector
embedding = generator.embed("This is a piece of text")

# Calculate similarity
similarity = generator.similarity("Text A", "Text B")
```

### 2. Memory Storage (memory_store.py)

- **Storage format**: JSON file (default `memory_data.json`)
- **Memory structure**:
  ```json
  {
    "text": "Memory content",
    "embedding": [0.1, 0.2, ...],
    "importance": 0.9,
    "timestamp": "2025-10-12T10:30:00"
  }
  ```

### 3. 时间衰减

使用指数衰减公式模拟遗忘曲线：

```
decay_factor = 0.5 ^ (days_passed / half_life_days)
new_importance = old_importance * decay_factor
```

默认半衰期为 7 天，可自定义。

## 集成到 Obsidian

Memory Tool 设计用于集成到 Obsidian 笔记系统中：

1. **自动记忆提取**：从笔记中提取重要信息
2. **上下文检索**：根据当前笔记内容检索相关记忆
3. **智能提醒**：基于记忆重要性和时间衰减提供提醒

## API 文档

启动服务器后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 配置选项

### EmbeddingGenerator

```python
# 使用不同的模型
generator = EmbeddingGenerator(model_name="paraphrase-multilingual-MiniLM-L12-v2")
```

### MemoryStore

```python
# 自定义存储路径
store = MemoryStore(path="custom_memory.json")

# 自定义衰减参数
store.decay(half_life_days=14.0)
```

## 性能优化

- **模型缓存**：首次加载后模型会被缓存
- **批量处理**：支持批量添加和检索记忆
- **向量索引**：可集成 ChromaDB 或 FAISS 提升检索速度

## 未来计划

- [ ] 集成 ChromaDB 向量数据库
- [ ] 支持记忆分类和标签
- [ ] 实现记忆合并和去重
- [ ] 添加记忆重要性自动评估
- [ ] Obsidian 插件开发

## 测试

```bash
# 运行测试
python -m pytest tests/test_memory.py

# 测试 embeddings
python src/memory_tool/embeddings.py

# 测试 memory_store
python src/memory_tool/memory_store.py
```

## 故障排除

**问题：模型下载失败**
```bash
# 设置 HuggingFace 镜像
export HF_ENDPOINT=https://hf-mirror.com
```

**问题：导入错误**
```bash
# 确保从项目根目录运行
cd ContextAutoFeedAgent-CAFA
python -c "from src.memory_tool.memory_store import MemoryStore"
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

