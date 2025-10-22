# Memory Tool 测试工具

## 🚀 快速开始

**使用统一启动器（推荐）⭐⭐⭐⭐**

```bash
# Windows用户 - 双击运行
start_cafa.bat

# 或命令行（从项目根目录）
python start_cafa.py
```

**启动后选择模式 2 进入测试模式**

---

## 📋 测试功能列表

所有测试功能已整合到主启动器 `start_cafa.py` 中。

启动后：
1. 选择 **"2. 🧪 运行测试"**
2. 进入测试菜单，选择对应的测试

### 可用测试

1. **悬浮窗口检索测试** ⭐⭐⭐⭐ (最直观)
   - 自动导入ChatGPT历史记录
   - 启动记忆API服务器
   - 打开可视化UI
   - 图形化界面进行检索测试

2. **自动检索测试** ⭐⭐⭐ (最全面)
   - 批量自动检索所有记忆
   - 相似度分布分析
   - 生成详细JSON报告
   - 最佳和最差检索示例

3. **交互式测试** ⭐⭐ (最灵活)
   - 手动输入查询
   - 调整记忆权重
   - 添加/删除记忆
   - 时间衰减测试

4. **单元测试**
   - 测试EmbeddingGenerator
   - 测试MemoryStore
   - 边界情况测试
   - 性能测试

5. **对话数据测试**
   - 测试conversations.json（935个对话）
   - 可自定义处理数量
   - 大规模数据测试

6. **记忆对话测试**
   - 模拟真实对话流程
   - 自动存储和检索记忆
   - 评估记忆命中率
   - 生成效果分析报告

7. **导入ChatGPT记录**
   - 快速批量导入
   - 验证向量化效果
   - 基本搜索测试

---

## 🎯 推荐使用顺序

### 首次使用

1. **悬浮窗口检索测试** ⭐⭐⭐⭐
   ```
   最直观，最适合初学者
   启动后在UI中进行检索测试
   ```

2. **自动检索测试** ⭐⭐⭐
   ```
   全面评估系统性能
   查看相似度分布和质量报告
   ```

3. **交互式测试** ⭐⭐
   ```
   深入探索各项功能
   手动调整参数观察效果
   ```

### 开发调试

1. **单元测试** - 验证基础功能
2. **交互式测试** - 手动测试特定场景
3. **自动检索测试** - 批量验证改进效果

### 性能评估

1. **自动检索测试** - 获取量化指标
2. **对话数据测试** - 大规模数据验证
3. **记忆对话测试** - 实际场景评估

---

## 📊 输出文件说明

所有生成的文件都在**项目根目录**：

| 文件 | 来源测试 | 说明 |
|------|---------|------|
| `auto_retrieval_memory.json` | 自动检索测试 | 记忆库 |
| `auto_retrieval_report.json` | 自动检索测试 | 详细分析报告 |
| `interactive_memory.json` | 交互式测试 | 交互式记忆库 |
| `test_large_conversations_memory.json` | 对话数据测试 | 记忆库 |
| `test_conversation_memory.json` | 记忆对话测试 | 记忆库 |
| `memory_test_report.json` | 记忆对话测试 | 测试报告 |
| `chatgpt_memory_test.json` | 导入ChatGPT | 记忆库 |

---

## 💡 快速命令

### 启动测试

```bash
# 从项目根目录
python start_cafa.py
# 选择: 2 (测试模式)
```

### 直接运行特定测试脚本

如果你想直接运行某个测试，可以：

```bash
# 自动检索测试
python tests/auto_retrieval_test.py --conversations 10 --messages 30

# 对话数据测试
python tests/test_large_conversations.py --conversations 20 --messages 50

# 交互式测试
python tests/interactive_memory_test.py

# 单元测试
python tests/test_memory_unit.py

# 导入ChatGPT记录
python tests/import_chatgpt_history.py conversations.json

# 记忆对话测试
python tests/test_memory_with_conversation.py
```

---

## 📚 相关文档

- **启动指南**: [../docs/启动指南_最新.md](../docs/启动指南_最新.md)
- **悬浮窗口测试**: [../docs/悬浮窗口检索测试指南.md](../docs/悬浮窗口检索测试指南.md)
- **测试快速开始**: [../docs/开始测试.md](../docs/开始测试.md)
- **Memory Tool文档**: [../docs/MEMORY_TOOL_README.md](../docs/MEMORY_TOOL_README.md)

---

## ❓ 常见问题

### Q: 如何运行测试？

**A**: 
```bash
python start_cafa.py
# 选择: 2 (运行测试)
# 然后选择具体的测试项目
```

### Q: 哪个测试最适合我？

**A**: 
- **新手**：悬浮窗口检索测试（选项1）- 最直观
- **评估**：自动检索测试（选项2）- 最全面
- **开发**：单元测试（选项4）- 最基础
- **实验**：交互式测试（选项3）- 最灵活

### Q: 测试需要多长时间？

**A**:
- 悬浮窗口测试: 2-5分钟（含导入和启动）
- 自动检索测试: 3-5分钟
- 交互式测试: 由你决定
- 单元测试: 10-30秒
- 对话数据测试: 1-3分钟（取决于数量）

### Q: 测试文件存在哪里？

**A**: 所有生成的文件都在**项目根目录**，不在tools目录下。

---

## 🎉 立即开始

```bash
# 最简单的方式
python start_cafa.py
```

选择适合你的测试，开始体验Memory Tool！

---

<div align="center">
  <strong>🚀 统一入口，所有功能！</strong>
</div>
