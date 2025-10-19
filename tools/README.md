# Memory Tool 测试工具

## 🚀 快速开始

这个文件夹包含了所有 Memory Tool 的测试启动工具。

---

## 📋 工具列表

### 1️⃣ test_conversations.bat ⭐ (推荐)

**功能**：测试你的 conversations.json 文件（ChatGPT 官方导出格式）

**数据**：你有 **935 个对话**！

**使用方法**：
```cmd
双击运行: test_conversations.bat
```

**或命令行**：
```bash
cd ..
python tests/test_large_conversations.py --conversations 5 --messages 20
```

**生成结果**：
- `test_large_conversations_memory.json` - 记忆数据

---

### 2️⃣ test_memory_conversation.bat

**功能**：对话场景测试 - 模拟真实对话流程

**特点**：
- 逐轮模拟对话
- 自动存储和检索记忆
- 生成效果分析报告
- 评估记忆命中率

**使用方法**：
```cmd
双击运行: test_memory_conversation.bat
```

**或命令行**：
```bash
cd ..
python tests/test_memory_with_conversation.py
```

**生成结果**：
- `test_conversation_memory.json` - 记忆数据
- `memory_test_report.json` - 测试报告

---

### 3️⃣ import_chatgpt.bat

**功能**：简单导入测试 - 批量导入对话记录

**特点**：
- 快速批量导入
- 测试基本搜索功能
- 验证向量化效果

**使用方法**：
```cmd
双击运行: import_chatgpt.bat
```

**或命令行**：
```bash
cd ..
python tests/import_chatgpt_history.py
```

**生成结果**：
- `chatgpt_memory_test.json` - 记忆数据

---

## 🎯 推荐使用顺序

### 首次使用

1. **test_conversations.bat** - 用你的真实数据测试
   ```
   双击运行，查看 935 个对话的测试效果
   ```

2. **test_memory_conversation.bat** - 深度测试
   ```
   模拟对话场景，评估实际效果
   ```

### 日常开发

- 快速验证功能 → `import_chatgpt.bat`
- 完整测试评估 → `test_memory_conversation.bat`
- 大规模数据测试 → `test_conversations.bat`

---

## 📊 测试参数调整

### test_conversations.bat

编辑批处理文件，修改参数：

```batch
python tests\test_large_conversations.py ^
  --conversations 10 ^     REM 处理多少个对话
  --messages 30            REM 每个对话提取多少消息
```

或直接在命令行使用：
```bash
# 测试更多数据
python tests/test_large_conversations.py --conversations 20 --messages 50

# 全面测试（会比较慢）
python tests/test_large_conversations.py --conversations 100 --messages 100
```

---

## 📚 详细文档

- **完整指南**：[../docs/Memory_Tool测试指南_完整版.md](../docs/Memory_Tool测试指南_完整版.md)
- **对话测试**：[../docs/如何测试Memory_Tool在对话中的效果.md](../docs/如何测试Memory_Tool在对话中的效果.md)
- **导入测试**：[../docs/如何使用ChatGPT历史记录测试Memory_Tool.md](../docs/如何使用ChatGPT历史记录测试Memory_Tool.md)
- **快速入口**：[../开始测试.md](../开始测试.md)

---

## 💡 常见问题

### Q: 应该用哪个工具？

**A**: 推荐顺序：
1. `test_conversations.bat` - 测试你的真实数据（935个对话）
2. `test_memory_conversation.bat` - 评估实际对话效果
3. `import_chatgpt.bat` - 快速功能验证

### Q: 测试需要多长时间？

**A**: 
- `test_conversations.bat`（3个对话）：1-2 分钟
- `test_memory_conversation.bat`：30秒 - 1分钟
- `import_chatgpt.bat`：30秒 - 1分钟

### Q: 可以测试更多对话吗？

**A**: 可以！编辑 `test_conversations.bat` 或使用命令行：
```bash
python tests/test_large_conversations.py --conversations 50 --messages 30
```

### Q: 生成的文件在哪里？

**A**: 所有生成的文件都在**项目根目录**：
- `test_large_conversations_memory.json`
- `test_conversation_memory.json`
- `memory_test_report.json`

---

## 🔧 故障排除

### 问题：找不到文件

**检查**：确保从项目根目录运行，或使用批处理文件

### 问题：导入太慢

**解决**：减少处理的对话数量
```bash
--conversations 3 --messages 10
```

### 问题：内存不足

**解决**：使用 `test_conversations.bat`，它会限制数据量

---

## 📈 下一步

完成测试后：

1. ✅ 查看测试报告分析结果
2. ✅ 根据指标优化策略
3. ✅ 调整存储和检索逻辑
4. ✅ 重新测试验证改进
5. ✅ 集成到实际应用

---

<div align="center">
  <strong>开始测试你的 Memory Tool！🚀</strong>
</div>

