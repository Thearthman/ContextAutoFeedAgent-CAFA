# Memory Tool - 长期记忆系统

## 概述

Memory Tool 是一个基于语义向量的长期记忆存储和检索系统，支持：
- 📝 **记忆存储**：保存文本记忆并生成语义向量
- 🔍 **语义检索**：根据查询内容检索最相关的记忆
- ⏰ **时间衰减**：模拟人类记忆的遗忘曲线
- 🌐 **API 接口**：提供 FastAPI RESTful API

## 项目结构

```
src/
└── memory_tool/           # 核心记忆模块
    ├── __init__.py
    ├── embeddings.py      # 文本向量化
    ├── memory_store.py    # 记忆存储和检索
    ├── decay.py           # 时间衰减逻辑
    └── api/               # API 接口
        ├── __init__.py
        ├── memory_manager.py  # 记忆管理器
        └── memory_api.py      # FastAPI 接口
tests/
└── test_memory.py         # 测试文件
run_memory_api.py          # API 启动脚本
test_memory_basic.py       # 快速测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `sentence-transformers`: 文本向量化
- `chromadb`: 向量数据库（可选）
- `fastapi`: API 框架
- `uvicorn`: ASGI 服务器

### 2. 基础使用

#### Python API

```python
from src.memory_tool.memory_store import MemoryStore

# 创建记忆存储
store = MemoryStore()

# 添加记忆
store.add_memory("我在考试中错了牛顿第三定律的题", importance=0.9)
store.add_memory("我在复习时发现自己不理解热力学第二定律", importance=0.8)

# 搜索相关记忆
results = store.search("复习热力学", top_k=3)
for result in results:
    print(f"记忆: {result['text']}")
    print(f"相似度: {result['similarity']}")

# 执行时间衰减
store.decay(half_life_days=7.0)
```

#### REST API

启动 API 服务器：

```bash
# 方式 1: 使用启动脚本（推荐）
python run_memory_api.py

# 方式 2: 直接使用 uvicorn
cd src
uvicorn memory_tool.api.memory_api:app --reload --port 8000
```

API 端点：

**存储记忆**
```bash
curl -X POST "http://localhost:8000/store?text=我今天学习了Python编程"
```

**检索记忆**
```bash
curl "http://localhost:8000/recall?query=Python学习"
```

**触发衰减**
```bash
curl -X POST "http://localhost:8000/decay"
```

## 核心功能

### 1. 语义向量化 (embeddings.py)

使用 `sentence-transformers` 的 `all-MiniLM-L6-v2` 模型将文本转换为 384 维向量。

```python
from src.memory_tool.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()

# 生成向量
embedding = generator.embed("这是一段文本")

# 计算相似度
similarity = generator.similarity("文本A", "文本B")
```

### 2. 记忆存储 (memory_store.py)

- **存储格式**：JSON 文件（默认 `memory_data.json`）
- **记忆结构**：
  ```json
  {
    "text": "记忆内容",
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

