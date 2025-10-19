# 如何使用 ChatGPT 历史聊天记录测试 Memory Tool

## 🎉 我已经为你准备好了所有工具！

## 🚀 最简单的方法（3步完成）

### 步骤 1️⃣: 准备 ChatGPT 聊天记录

你有两个选择：

**选择 A: 使用真实的 ChatGPT 数据**
1. 访问 https://chat.openai.com
2. 点击左下角头像 → Settings → Data controls
3. 点击 "Export data" 并等待邮件
4. 下载 `conversations.json` 文件
5. 将文件重命名为 `chatgpt_export.json` 并放在项目根目录

**选择 B: 使用示例数据（快速测试）**
- 直接运行脚本，系统会自动创建示例文件

### 步骤 2️⃣: 运行导入脚本

**Windows 用户（推荐）：**
```cmd
双击运行: import_chatgpt.bat
```

**或者使用命令行：**
```bash
python tests/import_chatgpt_history.py
```

### 步骤 3️⃣: 查看结果

脚本会自动：
- ✅ 导入所有聊天记录
- ✅ 进行语义向量化
- ✅ 测试搜索功能
- ✅ 显示相似度分数
- ✅ 保存到 `chatgpt_memory_test.json`

## 📊 你会看到什么

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
✓ [  3] user       | 什么是机器学习？...
...

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

3. [相似度: 0.619]
   学习 Python 可以从以下几个方面入手...
```

## 🔧 自定义配置

如果你想自定义导入行为，编辑 `tests/import_chatgpt_history.py` 文件：

```python
# ========== 配置区域 ==========
json_file = "chatgpt_export.json"  # 你的文件路径

# 过滤选项
filter_role = None  # None=全部, 'user'=只导入用户消息, 'assistant'=只导入AI消息
min_length = 10     # 最小文本长度（跳过太短的消息）
importance_base = 0.7  # 基础重要性 (0-1之间)

# 测试查询（根据你的聊天内容修改）
test_queries = [
    "Python 编程",
    "机器学习",
    "数据库",
]
# ========== 配置区域结束 ==========
```

## 🎯 进一步测试

### 测试 1: 使用 Python 直接操作

```python
from src.memory_tool.memory_store import MemoryStore

# 加载导入的记忆
store = MemoryStore(path="chatgpt_memory_test.json")

# 搜索记忆
results = store.search("你想搜索的内容", top_k=5)
for r in results:
    print(f"相似度: {r['similarity']:.3f}")
    print(f"内容: {r['text']}\n")

# 测试时间衰减
print(f"衰减前重要性: {store.memories[0]['importance']}")
store.decay(half_life_days=7.0)
print(f"衰减后重要性: {store.memories[0]['importance']}")
```

### 测试 2: 启动 API 服务器

```bash
# 启动 Memory Tool API
python run_memory_api.py

# 在浏览器中访问
http://localhost:8000/docs

# 或使用 curl 测试
curl "http://localhost:8000/recall?query=Python编程"
```

## 📂 项目中新增的文件

我为你创建了以下文件：

1. **`tests/import_chatgpt_history.py`** - 主导入脚本
2. **`import_chatgpt.bat`** - Windows 一键启动脚本
3. **`docs/CHATGPT_IMPORT_GUIDE.md`** - 详细使用指南
4. **`CHATGPT_TEST_QUICKSTART.md`** - 快速开始指南
5. **`tests/README_IMPORT_TEST.md`** - 测试说明文档
6. **`chatgpt_export_example.json`** - 示例数据文件（供参考）

## 🎨 支持的文件格式

脚本会自动识别以下格式：

1. **简单消息数组**
   ```json
   [
     {"role": "user", "content": "你好"},
     {"role": "assistant", "content": "你好！"}
   ]
   ```

2. **ChatGPT 官方导出格式**（conversations.json）

3. **自定义对话格式**

## ❓ 常见问题

### Q: 我没有 ChatGPT 导出数据怎么办？
**A:** 直接运行脚本，选择创建示例文件，系统会自动生成测试数据。

### Q: 导入需要多长时间？
**A:** 
- 首次运行需要下载模型（约 1-2 分钟）
- 之后每条消息处理约 0.1-0.3 秒
- 100 条消息大约需要 10-30 秒

### Q: 可以只导入我的提问吗？
**A:** 可以！在配置中设置 `filter_role = "user"`

### Q: 如何查看导入的数据？
**A:** 导入的数据保存在 `chatgpt_memory_test.json`，你可以直接打开查看。

### Q: 出现编码错误怎么办？
**A:** 脚本已经自动处理 Windows UTF-8 编码问题，应该不会出现这个问题。

## 📚 详细文档

如果你想了解更多：

- **完整指南**: [docs/CHATGPT_IMPORT_GUIDE.md](docs/CHATGPT_IMPORT_GUIDE.md)
- **快速参考**: [CHATGPT_TEST_QUICKSTART.md](CHATGPT_TEST_QUICKSTART.md)
- **Memory Tool 文档**: [docs/MEMORY_TOOL_README.md](docs/MEMORY_TOOL_README.md)
- **测试说明**: [tests/README_IMPORT_TEST.md](tests/README_IMPORT_TEST.md)

## 🎉 开始使用吧！

现在你可以：

```bash
# 方法 1: 使用批处理（最简单）
双击运行: import_chatgpt.bat

# 方法 2: 使用 Python
python tests/import_chatgpt_history.py

# 方法 3: 使用现成的示例
# 项目已经包含了 chatgpt_export_example.json 示例文件
```

## 💡 小提示

1. **首次运行会下载模型**：大约 90MB，需要 1-2 分钟
2. **测试查询要匹配内容**：在配置中修改 `test_queries` 以匹配你的聊天内容
3. **可以多次导入**：每次导入会覆盖之前的测试数据
4. **查看详细日志**：脚本会显示每条记录的导入进度

---

<div align="center">
  <strong>祝测试顺利！如有问题，请查看详细文档。🚀</strong>
</div>


