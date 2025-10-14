# 架构实现对照文档

## 📊 架构图 vs 项目实现

### 架构图概览

架构图展示了三个主要部分：

1. **基础架构**：User Input + Context → LLM + Memory Tool → Output
2. **User Mode**：智能判断是否需要记忆检索
3. **Update Memory Mode**：自动存储重要上下文到记忆

---

## ✅ 项目实现映射

### 1. 基础组件

| 架构图组件 | 项目实现 | 文件路径 | 状态 |
|----------|---------|---------|------|
| **Memory 数据库** | JSON 文件存储 | `memory_data.json` | ✅ |
| **Memory Tool** | MemoryStore + Embeddings | `src/memory_tool/` | ✅ |
| **LLM** | 本地 Gemma / 线上 API | `src/main.py` / `src/online_model_server.py` | ✅ |
| **User Input** | Flask API + 浮动 UI | `src/floating_ui.py` | ✅ |
| **Output** | HTTP 响应 + UI 显示 | 各服务器 | ✅ |

### 2. User Mode（用户模式）

**架构图流程：**
```
User Input → LLM → Memory? 
           ↓ yes    ↓ no
      M Tool fetch  直接输出
           ↓
       Memory 检索
           ↓
        Output
```

**项目实现：**

| 功能 | 实现方式 | 代码位置 |
|------|---------|---------|
| **User Input** | POST /chat | `integrated_llm_memory.py:chat()` |
| **Memory? 判断** | `should_fetch_memory()` | 第 70-90 行 |
| **M Tool fetch** | `fetch_memory()` | 第 92-114 行 |
| **LLM 处理** | `call_llm()` | 第 124-141 行 |
| **Output** | JSON 响应 | 返回结果 |

**判断逻辑：**
- ✅ 关键词检测（"记得"、"之前"、"上次"等）
- ✅ 可扩展为 LLM 智能判断
- ✅ 相似度阈值控制

### 3. Update Memory Mode（更新记忆模式）

**架构图流程：**
```
Context → memory tool indexing → Memory
```

**项目实现：**

| 功能 | 实现方式 | 代码位置 |
|------|---------|---------|
| **Context 提取** | 对话内容 | 用户输入 + AI 响应 |
| **重要性判断** | `should_store_as_memory()` | 第 162-181 行 |
| **Memory indexing** | `store_to_memory()` | 第 143-160 行 |
| **Memory 存储** | MemoryStore.add_memory() | `memory_store.py` |

**存储策略：**
- ✅ 包含重要信息的对话
- ✅ 用户明确要求记住的内容
- ✅ 长回答（可能包含重要信息）
- ✅ 可配置的重要性评分

---

## 🔄 完整数据流

### 场景 1：普通对话（无需记忆）

```
用户: "今天天气怎么样？"
  ↓
[should_fetch_memory] → false
  ↓
[call_llm] → "今天天气晴朗..."
  ↓
[should_store_as_memory] → false
  ↓
返回响应
```

### 场景 2：需要记忆的对话

```
用户: "你还记得我之前说过的那个项目吗？"
  ↓
[should_fetch_memory] → true
  ↓
[fetch_memory] → 检索到 3 条相关记忆
  ↓
[build_context_with_memory] → 构建增强上下文
  ↓
[call_llm] → "根据你之前提到的项目..."
  ↓
[should_store_as_memory] → true
  ↓
[store_to_memory] → 存储对话
  ↓
返回响应 + 记忆信息
```

### 场景 3：主动存储记忆

```
用户: "记住，我的生日是 10 月 15 日"
  ↓
[should_fetch_memory] → true (关键词 "记住")
  ↓
[fetch_memory] → 检查是否已有生日信息
  ↓
[call_llm] → "好的，我会记住..."
  ↓
[should_store_as_memory] → true (关键词判断)
  ↓
[store_to_memory] → 高重要性存储
  ↓
返回确认响应
```

---

## 🏗️ 系统架构层次

```
┌─────────────────────────────────────────────────┐
│           浮动 UI (Floating UI)                  │
│         src/floating_ui.py                       │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│     集成服务 (Integrated Service)                │
│     src/integrated_llm_memory.py                 │
│                                                   │
│  • 智能记忆判断 (Memory? Decision)               │
│  • 上下文增强 (Context Enhancement)              │
│  • 自动记忆存储 (Auto Memory Storage)            │
└──────────┬──────────────────────┬────────────────┘
           │                      │
           ↓                      ↓
┌──────────────────────┐  ┌─────────────────────┐
│   LLM 服务            │  │  Memory 服务         │
│   (port 5000)         │  │  (port 8000)        │
│                       │  │                     │
│ • 本地 Gemma          │  │ • MemoryStore       │
│ • 线上 API (OpenAI等) │  │ • 语义搜索           │
│ • 流式输出            │  │ • 时间衰减           │
└──────────────────────┘  └─────────────────────┘
```

---

## 🚀 使用方式

### 1. 启动所有服务

```bash
# 终端 1: 启动 Memory API (可选，如果使用本地模式)
python run_memory_api.py

# 终端 2: 启动 LLM 服务（线上模式）
python src/online_model_server.py

# 终端 3: 启动集成服务
python src/integrated_llm_memory.py

# 终端 4: 启动浮动 UI
python src/floating_ui.py
```

### 2. API 使用示例

**智能聊天：**
```bash
curl -X POST http://localhost:6000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你还记得我上次提到的那个项目吗？"}'
```

**响应示例：**
```json
{
  "response": "根据你之前提到的 AI 助手项目...",
  "used_memory": true,
  "memory_count": 3,
  "memories": [
    {"text": "用户提到了 AI 助手项目", "similarity": 0.85}
  ]
}
```

**手动搜索记忆：**
```bash
curl "http://localhost:6000/memory/search?query=AI项目&top_k=5"
```

**手动存储记忆：**
```bash
curl -X POST http://localhost:6000/memory/store \
  -H "Content-Type: application/json" \
  -d '{"text": "用户喜欢用 Python 编程", "importance": 0.9}'
```

---

## 📈 统计与监控

访问 `http://localhost:6000/stats` 查看：

- `total_queries`: 总查询次数
- `memory_fetches`: 记忆检索次数
- `memory_stores`: 记忆存储次数
- `context_enhanced_queries`: 使用记忆增强的查询次数

---

## 🎯 架构优势

### 符合架构图的设计

✅ **分离关注点**：
- LLM 专注于生成
- Memory Tool 专注于存储和检索
- 集成层协调两者

✅ **智能决策**：
- 自动判断何时需要记忆
- 自动判断何时存储记忆
- 可配置的阈值和策略

✅ **可扩展性**：
- 支持本地和远程 LLM
- 支持本地和 API Memory
- 易于添加新的判断逻辑

✅ **用户友好**：
- 统一的聊天接口
- 透明的记忆使用
- 流式输出支持

---

## 🔧 配置选项

编辑 `src/integrated_llm_memory.py` 的 `config` 字典：

```python
config = {
    "llm_service_url": "http://localhost:5000",      # LLM 服务地址
    "memory_service_url": "http://localhost:8000",   # Memory 服务地址
    "auto_store_memory": True,                       # 自动存储记忆
    "memory_threshold": 0.7,                         # 相似度阈值
    "use_local_memory": True,                        # 使用本地 Memory
}
```

---

## 🎉 总结

**当前项目完全实现了架构图中的所有核心概念：**

1. ✅ **User Mode** - 智能记忆检索
2. ✅ **Update Memory Mode** - 自动记忆存储
3. ✅ **LLM + Memory Tool** - 完整集成
4. ✅ **流式输出** - 实时响应
5. ✅ **多服务架构** - 模块化设计

**与架构图的差异：**

- 📈 **改进**：添加了统计和监控
- 📈 **改进**：支持本地和远程两种模式
- 📈 **改进**：可配置的判断策略
- 🔄 **扩展**：支持流式聊天
- 🔄 **扩展**：支持手动记忆操作

项目现在是一个**完整的、符合架构图逻辑的智能 AI 助手系统**！
