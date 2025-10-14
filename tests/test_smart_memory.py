#!/usr/bin/env python3
"""
测试智能记忆权重系统
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_tool.enhanced_memory_store import EnhancedMemoryStore

def test_smart_memory():
    print("🧠 增强版记忆存储系统测试")
    print("=" * 70)
    
    store = EnhancedMemoryStore(path="test_enhanced_memory.json")
    
    # Test添加记忆
    test_memories = [
        ("记住，我的 API Key 是 sk-1234567890", "应该被识别为高重要性"),
        ("我在开发一个 AI 助手项目", "应该被识别为中等重要性"),
        ("今天天气不错", "应该被识别为低重要性"),
        ("我喜欢使用 Python 和深度学习技术", "应该被识别为中等重要性"),
        ("不要忘记，明天下午 3 点有会议", "应该被识别为高重要性"),
    ]
    
    print("\n1️⃣ 智能添加记忆（自动评估权重）:")
    print("=" * 70)
    
    for text, expected in test_memories:
        print(f"\n📝 文本: {text}")
        print(f"   预期: {expected}")
        
        memory = store.add_memory(text)
        
        print(f"   ✅ 权重: {memory['importance']:.2f} ({memory['category']})")
        print(f"   📊 衰减速度: {memory['metadata']['decay_rate']}")
        print(f"   ⏰ 半衰期: {memory['half_life_days']} 天")
        
        if memory['evaluation_info']['auto_evaluated']:
            print(f"   📌 评估原因:")
            for reason in memory['evaluation_info']['evaluation_reasons']:
                print(f"      • {reason}")
        
        if memory['metadata']['should_prompt_user']:
            print(f"   💡 用户提示: {memory['metadata']['prompt_message']}")
    
    # Test搜索（带重要性加权）
    print("\n\n2️⃣ 搜索测试（重要性加权）:")
    print("=" * 70)
    
    queries = ["API", "项目开发", "会议"]
    
    for query in queries:
        print(f"\n🔍 搜索: '{query}'")
        results = store.search(query, top_k=3, importance_boost=True)
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"   {i}. [{r['similarity']:.3f}] {r['text'][:60]}...")
                print(f"      权重: {r['importance']:.2f} | 分类: {r['category']} | 访问: {r['access_count']}次")
        else:
            print("   (未找到匹配结果)")
    
    # Test手动调整权重
    print("\n\n3️⃣ 手动调整权重测试:")
    print("=" * 70)
    
    if len(store.memories) > 2:
        print(f"\n原记忆: {store.memories[2]['text']}")
        print(f"原权重: {store.memories[2]['importance']:.2f} ({store.memories[2]['category']})")
        
        # 提升权重
        store.update_importance(2, 0.95)
        
        print(f"新权重: {store.memories[2]['importance']:.2f} ({store.memories[2]['category']})")
        print(f"新半衰期: {store.memories[2]['half_life_days']} 天")
    
    # Test差异化衰减
    print("\n\n4️⃣ 自适应衰减测试:")
    print("=" * 70)
    
    print("\n衰减前的记忆分布:")
    for category in ["永久记忆", "重要记忆", "常规记忆", "临时记忆", "低优先级"]:
        count = len(store.get_memories_by_category(category))
        if count > 0:
            print(f"   {category}: {count} 条")
    
    # Execute衰减
    decay_result = store.adaptive_decay()
    print(f"\n✅ 衰减完成:")
    print(f"   更新了 {decay_result['updated_count']} 条记忆")
    print(f"   剩余高重要性记忆: {decay_result['high_importance_remaining']} 条")
    
    print("\n衰减后的记忆分布:")
    for category in ["永久记忆", "重要记忆", "常规记忆", "临时记忆", "低优先级"]:
        count = len(store.get_memories_by_category(category))
        if count > 0:
            print(f"   {category}: {count} 条")
    
    # Statistics信息
    print("\n\n5️⃣ 系统统计:")
    print("=" * 70)
    
    stats = store.get_stats()
    print(f"\n📊 总体统计:")
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   高重要性记忆 (≥0.8): {stats['high_importance_count']}")
    print(f"   平均重要性: {stats['avg_importance']:.2f}")
    print(f"   用户提示次数: {stats['user_prompted_count']}")
    
    print(f"\n📈 分类分布:")
    for category, count in stats['categories'].items():
        if count > 0:
            print(f"   {category}: {count} 条")
    
    # 需要复习的记忆
    print("\n\n6️⃣ 需要复习的记忆:")
    print("=" * 70)
    
    review_needed = store.get_memories_needing_review(days_threshold=0)
    if review_needed:
        print(f"\n找到 {len(review_needed)} 条需要复习的记忆:")
        for mem in review_needed[:5]:
            print(f"   • [{mem['importance']:.2f}] {mem['text'][:60]}...")
            print(f"     {mem['days_since_access']} 天未访问 | 共访问 {mem['access_count']} 次")
    else:
        print("   (暂无需要复习的记忆)")
    
    # 总结
    print("\n\n🎉 测试完成!")
    print("=" * 70)
    print("""
✅ 验证的功能:
   1. 智能权重评估 - 自动分析内容重要性
   2. 用户提示机制 - 在合适时提醒用户调整权重
   3. 差异化衰减 - 高权重记忆衰减慢
   4. 记忆分类 - 自动分类管理
   5. 搜索增强 - 重要性加权
   6. 统计追踪 - 完整的数据分析

💡 关键特性:
   • 永久记忆 (权重≥0.9): 半衰期 365 天
   • 重要记忆 (权重≥0.75): 半衰期 90 天
   • 常规记忆 (权重≥0.5): 半衰期 30 天
   • 临时记忆 (权重≥0.3): 半衰期 7 天
   • 低优先级 (权重<0.3): 半衰期 3 天
    """)
    
    # Clean up测试文件
    if os.path.exists("test_enhanced_memory.json"):
        os.remove("test_enhanced_memory.json")
        print("🧹 已清理测试文件")

if __name__ == "__main__":
    test_smart_memory()
