# ChatGPT 历史聊天记录导入测试

## ✅ 已完成的功能

本目录包含用于将 ChatGPT 聊天记录导入到 Memory Tool 进行测试的工具。

## 📁 文件说明

- **`import_chatgpt_history.py`** - 主导入脚本
  - 支持多种 ChatGPT 导出格式
  - 自动语义向量化
  - 可配置的过滤和重要性计算
  - 自动搜索功能测试

## 🚀 快速使用

### 方法 1: 使用 Windows 批处理（最简单）

从项目根目录运行：
```cmd
import_chatgpt.bat
```

### 方法 2: 使用 Python 脚本

```bash
python tests/import_chatgpt_history.py
```

## 📝 使用步骤

1. **准备数据文件**
   - 从 ChatGPT 导出聊天记录（JSON 格式）
   - 将文件命名为 `chatgpt_export.json` 放在项目根目录
   - 或者在脚本中修改文件路径

2. **运行导入脚本**
   ```bash
   python tests/import_chatgpt_history.py
   ```

3. **查看结果**
   - 导入的记忆保存在 `chatgpt_memory_test.json`
   - 自动执行搜索测试
   - 查看导入统计和相似度分数

## ⚙️ 配置选项

编辑 `import_chatgpt_history.py` 中的配置区域：

```python
# 文件路径
json_file = "chatgpt_export.json"

# 过滤选项
filter_role = None      # None=全部, 'user'=只导入用户, 'assistant'=只导入助手
min_length = 10         # 最小文本长度（字符）
importance_base = 0.7   # 基础重要性值 (0-1)

# 测试查询
test_queries = [
    "Python 编程",
    "机器学习",
    "数据库",
]
```

## 🎯 测试场景

### 场景 1: 基础功能测试
导入少量数据，验证基本的存储和检索功能：
```bash
# 使用示例数据（自动创建）
python tests/import_chatgpt_history.py
```

### 场景 2: 大规模数据测试
导入完整的 ChatGPT 历史记录，测试性能：
```python
# 配置指向完整导出文件
json_file = "conversations.json"
```

### 场景 3: 特定内容测试
只导入特定角色或主题的消息：
```python
# 只导入用户提问
filter_role = "user"
min_length = 20  # 过滤短消息
```

## 📊 输出示例

```
============================================================
ChatGPT 聊天记录导入工具
============================================================

📂 正在读取文件: chatgpt_export.json
✅ 找到 16 条对话记录

============================================================
开始导入...
============================================================
✓ [  1] user       | 如何学习 Python 编程？...
✓ [  2] assistant  | 学习 Python 可以从以下几个方面入手...
...
============================================================

✅ 导入完成!
   导入: 16 条
   跳过: 0 条
   总计: 16 条

============================================================
🔍 测试记忆搜索功能
============================================================

查询: "Python 编程"
------------------------------------------------------------
1. [相似度: 0.765]
   如何学习 Python 编程？...

2. [相似度: 0.659]
   如何学习 Python 编程？我是一个完全的新手。...
```

## 🔧 进阶使用

### 使用 Python API 直接操作

```python
from src.memory_tool.memory_store import MemoryStore

# 加载导入的记忆
store = MemoryStore(path="chatgpt_memory_test.json")

# 自定义搜索
results = store.search("你的查询", top_k=5)
for r in results:
    print(f"[{r['similarity']:.3f}] {r['text']}")

# 测试时间衰减
store.decay(half_life_days=7.0)

# 查看统计信息
print(f"总记忆数: {len(store.memories)}")
print(f"平均重要性: {sum(m['importance'] for m in store.memories) / len(store.memories):.3f}")
```

### 集成到 REST API

1. 修改 `src/memory_tool/api/memory_manager.py`:
   ```python
   def __init__(self):
       self.store = MemoryStore(path="chatgpt_memory_test.json")
   ```

2. 启动 API 服务器:
   ```bash
   python run_memory_api.py
   ```

3. 测试 API:
   ```bash
   curl "http://localhost:8000/recall?query=Python编程"
   ```

## 📚 相关文档

- **详细指南**: [docs/CHATGPT_IMPORT_GUIDE.md](../docs/CHATGPT_IMPORT_GUIDE.md)
- **快速开始**: [CHATGPT_TEST_QUICKSTART.md](../CHATGPT_TEST_QUICKSTART.md)
- **Memory Tool 文档**: [docs/MEMORY_TOOL_README.md](../docs/MEMORY_TOOL_README.md)

## 🐛 故障排除

### 问题: 编码错误
**解决**: 脚本已自动处理 Windows UTF-8 编码问题

### 问题: 找不到模块
**解决**: 确保从项目根目录运行，或已安装依赖
```bash
pip install -r requirements.txt
```

### 问题: JSON 解析错误
**解决**: 验证 JSON 文件格式正确
```bash
python -m json.tool chatgpt_export.json
```

### 问题: 导入速度慢
**原因**: 首次下载 sentence-transformers 模型
**解决**: 耐心等待，后续运行会使用缓存

## ✨ 功能特性

- ✅ 自动识别多种 ChatGPT 导出格式
- ✅ 语义向量化和相似度搜索
- ✅ 可配置的过滤条件
- ✅ 自动重要性评分
- ✅ 实时进度显示
- ✅ 自动搜索测试
- ✅ Windows UTF-8 编码支持
- ✅ 非交互式环境支持

## 🎉 下一步

完成导入测试后，你可以：

1. 分析记忆数据的质量和分布
2. 调整重要性计算算法
3. 优化搜索和衰减策略
4. 集成到实际应用中
5. 开发自定义的可视化界面

---

<div align="center">
  <strong>祝测试顺利！</strong>
</div>


