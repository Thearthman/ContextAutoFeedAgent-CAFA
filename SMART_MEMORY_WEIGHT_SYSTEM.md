# 智能记忆权重系统

## 🎯 系统概述

智能记忆权重系统是对原有记忆工具的重大升级，实现了：

1. **自动权重评估** - AI 智能分析内容重要性
2. **用户提示机制** - 在合适时提醒用户调整权重
3. **差异化衰减** - 高权重记忆衰减慢，保存更久
4. **记忆分类管理** - 自动分类为5个等级
5. **智能搜索增强** - 重要记忆优先显示

---

## 🧠 核心功能

### 1. 智能权重评估

系统会自动分析文本内容，评估其重要性：

#### 评估维度

| 维度 | 权重影响 | 示例 |
|------|---------|------|
| **高重要性关键词** | +0.3 | "记住"、"重要"、"API Key"、"密码"、"不要忘记" |
| **中重要性关键词** | +0.15 | "喜欢"、"项目"、"学习"、"需要" |
| **事实性信息** | +0.2 | 日期、型号、"我的...是"句式 |
| **个人信息** | +0.25 | 姓名、电话、邮箱、公司 |
| **内容长度** | ±0.1 | 长文本 +0.1，短文本 -0.15 |
| **低价值内容** | -0.2 | 简单问候语（"你好"、"谢谢"） |

#### 评估示例

```python
# 示例 1: 高重要性
文本: "记住，我的 API Key 是 sk-1234567890"
权重: 1.00 (永久记忆)
原因: 
  • 包含高重要性关键词: '记住'、'API'
  • 包含事实性信息

# 示例 2: 中等重要性
文本: "我在开发一个 AI 助手项目"
权重: 0.65 (常规记忆)
原因:
  • 包含中重要性关键词: '项目'

# 示例 3: 低重要性
文本: "今天天气不错"
权重: 0.35 (临时记忆)
原因:
  • 内容过短
```

---

### 2. 记忆分类系统

根据权重自动分类为5个等级：

| 分类 | 权重范围 | 半衰期 | 描述 |
|------|---------|--------|------|
| **永久记忆** | ≥ 0.9 | 365 天 | 几乎不会衰减，长期保存 |
| **重要记忆** | 0.75-0.89 | 90 天 | 衰减缓慢，重点保留 |
| **常规记忆** | 0.5-0.74 | 30 天 | 正常衰减，定期复习 |
| **临时记忆** | 0.3-0.49 | 7 天 | 快速衰减，短期有效 |
| **低优先级** | < 0.3 | 3 天 | 快速遗忘，不重要 |

---

### 3. 差异化衰减

**核心特性**：高权重记忆衰减慢，保存更久

#### 衰减公式

```python
decay_factor = 0.5 ^ (days_passed / half_life_days)
new_importance = original_importance * decay_factor
```

#### 衰减对比

以 0.9 权重的永久记忆为例：

| 时间 | 重要性 | 说明 |
|------|--------|------|
| 添加时 | 0.900 | 原始权重 |
| 1天后 | 0.898 | 几乎无变化 |
| 1周后 | 0.887 | 轻微衰减 |
| 1个月后 | 0.845 | 仍保持高重要性 |
| 3个月后 | 0.758 | 降为重要记忆 |
| 1年后 | 0.450 | 降为常规记忆 |

对比 0.5 权重的常规记忆：

| 时间 | 重要性 | 说明 |
|------|--------|------|
| 添加时 | 0.500 | 原始权重 |
| 1天后 | 0.488 | 开始衰减 |
| 1周后 | 0.435 | 明显衰减 |
| 1个月后 | 0.250 | 降为临时记忆 |
| 3个月后 | 0.062 | 快速遗忘 |
| 1年后 | 0.000 | 完全遗忘 |

**结论**：永久记忆（0.9+）在1年后仍保留约50%重要性，而常规记忆（0.5）在1个月后就降到50%

---

### 4. 用户提示机制

系统会在适当时机提示用户调整权重：

#### 提示触发条件

1. **高价值内容检测** (权重 ≥ 0.8)
   ```
   💡 检测到高价值内容（权重: 0.85），是否需要设为永久保存？
   ```

2. **明确保存指令** ("记住"、"不要忘记"等)
   ```
   💡 检测到明确保存指令，建议提高权重至 0.95+
   ```

3. **中等权重确认** (0.5 ≤ 权重 ≤ 0.7)
   ```
   💡 内容权重为 0.65，这个信息对你重要吗？
   ```

#### 用户响应

用户可以选择：
- ✅ **接受建议** - 使用推荐权重
- 🔧 **手动调整** - 自定义权重值
- ⏭️ **跳过** - 使用自动评估权重

---

### 5. 搜索增强

搜索时可以启用**重要性加权**：

```python
# 普通搜索
results = store.search("Python", importance_boost=False)

# 重要性加权搜索
results = store.search("Python", importance_boost=True)
```

**加权效果**：
- 高权重记忆在相似度相近时会排名更靠前
- 加权公式：`boosted_similarity = similarity * (1 + importance * 0.2)`

**示例**：
```
查询: "编程"

不加权结果:
1. [0.75] "今天学习了编程" (权重: 0.3)
2. [0.72] "我喜欢用Python编程" (权重: 0.9)

加权结果:
1. [0.85] "我喜欢用Python编程" (权重: 0.9) ← 提升了
2. [0.76] "今天学习了编程" (权重: 0.3)
```

---

## 📊 使用示例

### 基础使用

```python
from memory_tool.enhanced_memory_store import EnhancedMemoryStore

# 创建增强版记忆存储
store = EnhancedMemoryStore()

# 1. 自动评估权重
memory = store.add_memory("记住，我的生日是10月15日")

print(f"权重: {memory['importance']}")  # 1.00
print(f"分类: {memory['category']}")    # 永久记忆
print(f"半衰期: {memory['half_life_days']}天")  # 365

# 2. 手动指定权重
memory = store.add_memory(
    "这是一个测试",
    importance=0.7,
    auto_evaluate=False
)

# 3. 搜索（重要性加权）
results = store.search("生日", importance_boost=True)

# 4. 自适应衰减
decay_result = store.adaptive_decay()
print(f"更新了 {decay_result['updated_count']} 条记忆")

# 5. 手动调整权重
store.update_importance(memory_index=0, new_importance=0.95)
```

### 高级功能

```python
# 获取特定分类的记忆
permanent_memories = store.get_memories_by_category("永久记忆")

# 获取需要复习的记忆
review_list = store.get_memories_needing_review(days_threshold=30)

# 统计信息
stats = store.get_stats()
print(f"总记忆数: {stats['total_memories']}")
print(f"高重要性记忆: {stats['high_importance_count']}")
print(f"平均重要性: {stats['avg_importance']:.2f}")
```

---

## 🔄 集成到现有系统

### 更新 integrated_llm_memory.py

```python
# 使用增强版记忆存储
from memory_tool.enhanced_memory_store import EnhancedMemoryStore

# 初始化
local_memory = EnhancedMemoryStore()

# 存储时包含提示信息
memory = local_memory.add_memory(text, auto_evaluate=True)

# 如果需要提示用户
if memory['metadata']['should_prompt_user']:
    prompt_msg = memory['metadata']['prompt_message']
    # 发送提示给用户界面
    send_notification(prompt_msg)
```

### API 端点

添加新的 API 端点来支持权重调整：

```python
@app.route('/memory/evaluate', methods=['POST'])
def evaluate_weight():
    """评估文本权重（不存储）"""
    text = request.json.get('text')
    weight, reasons = weight_evaluator.evaluate_weight(text)
    return jsonify({
        "weight": weight,
        "reasons": reasons,
        "category": weight_evaluator.get_weight_category(weight)
    })

@app.route('/memory/update_weight', methods=['POST'])
def update_memory_weight():
    """更新记忆权重"""
    memory_id = request.json.get('memory_id')
    new_weight = request.json.get('weight')
    success = store.update_importance(memory_id, new_weight)
    return jsonify({"success": success})
```

---

## 📈 性能对比

### 记忆保留率对比

| 时间 | 高权重(0.9+) | 中权重(0.5) | 低权重(0.3) |
|------|-------------|------------|------------|
| 1周后 | 98% | 87% | 70% |
| 1月后 | 94% | 50% | 12% |
| 3月后 | 84% | 13% | 0% |
| 1年后 | 50% | 0% | 0% |

### 用户满意度提升

- ✅ **减少误存储** - 低价值内容快速遗忘
- ✅ **保护重要信息** - 高价值内容长期保存
- ✅ **智能提醒** - 避免错误分类
- ✅ **透明化** - 用户了解为什么是这个权重

---

## 🎯 最佳实践

### 1. 权重选择建议

| 内容类型 | 推荐权重 | 示例 |
|---------|---------|------|
| **账号密码** | 0.95+ | API Key、密码、秘钥 |
| **个人信息** | 0.85-0.95 | 生日、电话、地址 |
| **重要事件** | 0.75-0.85 | 会议、截止日期 |
| **项目信息** | 0.6-0.75 | 工作项目、学习计划 |
| **偏好设置** | 0.5-0.7 | 喜好、习惯 |
| **临时信息** | 0.3-0.5 | 临时想法、草稿 |
| **闲聊内容** | < 0.3 | 问候、天气 |

### 2. 定期维护

```python
# 每天执行一次衰减
store.adaptive_decay()

# 每周检查需要复习的记忆
review_list = store.get_memories_needing_review(days_threshold=7)

# 每月查看统计
stats = store.get_stats()
```

### 3. 权重调整策略

- **初次添加**：依赖自动评估
- **使用一段时间后**：根据实际重要性手动调整
- **频繁访问的记忆**：考虑提升权重
- **不再需要的记忆**：降低权重让其自然衰减

---

## 🔍 常见问题

### Q1: 为什么我的重要记忆权重只有 0.7？

A: 自动评估基于内容特征。如果你认为很重要，可以手动调整：

```python
store.update_importance(memory_index, 0.95)
```

### Q2: 衰减速度可以调整吗？

A: 可以通过调整权重来间接控制。权重越高，衰减越慢。或者可以自定义半衰期：

```python
AdaptiveDecay.calculate_decay(
    original_importance=0.8,
    days_passed=30,
    custom_half_life=60  # 自定义半衰期
)
```

### Q3: 如何设置永不衰减的记忆？

A: 设置权重为 1.0，这样衰减会非常缓慢（1年后仍有50%重要性）。如果需要完全不衰减，可以在衰减时跳过高权重记忆：

```python
if memory['importance'] >= 0.95:
    continue  # 跳过永久记忆
```

### Q4: 用户提示会打扰用户吗？

A: 提示是可选的，你可以：
1. 在 UI 中作为非侵入式通知显示
2. 仅在用户主动查看记忆时显示
3. 完全关闭提示功能

---

## 🎉 总结

智能记忆权重系统实现了你的需求：

✅ **自动检测权重** - AI 智能分析内容重要性
✅ **提醒用户调整** - 在合适时机提示用户
✅ **差异化衰减** - 高权重记忆保存更久
✅ **透明可控** - 用户随时可以查看和调整

这个系统让记忆管理变得更智能、更人性化！🚀
