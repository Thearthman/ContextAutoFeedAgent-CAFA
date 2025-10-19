#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Tool 对话场景测试
使用 ChatGPT 历史对话记录，模拟 Memory Tool 在实际对话中的应用
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_tool.memory_store import MemoryStore


class ConversationMemoryTester:
    """对话场景下的 Memory Tool 测试器"""
    
    def __init__(self, memory_file: str = "test_conversation_memory.json"):
        """初始化测试器"""
        self.store = MemoryStore(path=memory_file)
        self.conversation_log = []
        self.memory_usage_stats = {
            'memories_stored': 0,
            'memories_retrieved': 0,
            'useful_retrievals': 0,
            'contexts_enhanced': 0
        }
        
    def load_conversation_history(self, json_file: str) -> List[Dict]:
        """加载 ChatGPT 对话历史"""
        print(f"📂 正在加载对话历史: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析对话
        conversations = []
        if isinstance(data, list):
            for item in data:
                if 'role' in item and 'content' in item:
                    conversations.append({
                        'role': item['role'],
                        'content': item['content'],
                        'timestamp': item.get('timestamp', None)
                    })
        
        print(f"✅ 已加载 {len(conversations)} 条对话\n")
        return conversations
    
    def should_store_as_memory(self, content: str, role: str) -> bool:
        """判断是否应该存储为记忆"""
        # 存储策略：
        # 1. 用户的重要问题（较长的问题）
        # 2. 助手的知识性回答（包含关键信息）
        
        if role == 'user':
            # 用户问题：长度 > 15 的存储
            return len(content) > 15
        
        elif role == 'assistant':
            # 助手回答：包含知识性内容的存储
            knowledge_indicators = [
                '方法', '步骤', '原则', '包括', '可以', 
                '需要', '建议', '例如', '主要', '关键'
            ]
            return any(indicator in content for indicator in knowledge_indicators)
        
        return False
    
    def calculate_memory_importance(self, content: str, role: str) -> float:
        """计算记忆重要性"""
        importance = 0.5
        
        # 长度因素
        if len(content) > 100:
            importance += 0.2
        if len(content) > 200:
            importance += 0.1
        
        # 内容因素
        important_keywords = ['重要', '关键', '必须', '核心', '基础']
        for keyword in important_keywords:
            if keyword in content:
                importance += 0.1
                break
        
        # 角色因素
        if role == 'user':
            importance += 0.1  # 用户问题通常更重要
        
        return min(1.0, importance)
    
    def retrieve_relevant_memories(self, query: str, top_k: int = 3) -> List[Dict]:
        """检索相关记忆"""
        if not self.store.memories:
            return []
        
        results = self.store.search(query, top_k=top_k)
        self.memory_usage_stats['memories_retrieved'] += len(results)
        
        # 过滤相似度阈值
        relevant = [r for r in results if r['similarity'] > 0.5]
        if relevant:
            self.memory_usage_stats['useful_retrievals'] += len(relevant)
            self.memory_usage_stats['contexts_enhanced'] += 1
        
        return relevant
    
    def simulate_conversation_with_memory(self, conversations: List[Dict]):
        """模拟带记忆的对话流程"""
        print("=" * 70)
        print("🤖 开始模拟对话场景（集成 Memory Tool）")
        print("=" * 70)
        print()
        
        for i, conv in enumerate(conversations, 1):
            role = conv['role']
            content = conv['content']
            
            print(f"\n{'─' * 70}")
            print(f"对话轮次 #{i}")
            print(f"{'─' * 70}")
            
            if role == 'user':
                print(f"👤 用户: {content[:80]}{'...' if len(content) > 80 else ''}")
                print()
                
                # 在用户提问时，检索相关记忆
                print("🧠 检索相关记忆...")
                relevant_memories = self.retrieve_relevant_memories(content, top_k=3)
                
                if relevant_memories:
                    print(f"   ✅ 找到 {len(relevant_memories)} 条相关记忆:\n")
                    for j, mem in enumerate(relevant_memories, 1):
                        similarity = mem['similarity']
                        text = mem['text']
                        
                        # 判断是否有用
                        if similarity > 0.7:
                            usefulness = "🔥 高度相关"
                        elif similarity > 0.5:
                            usefulness = "✓ 相关"
                        else:
                            usefulness = "- 弱相关"
                        
                        print(f"   [{j}] {usefulness} (相似度: {similarity:.3f})")
                        print(f"       {text[:100]}{'...' if len(text) > 100 else ''}")
                        print()
                    
                    print("   💡 这些记忆可以帮助提供更好的回答上下文\n")
                else:
                    print("   ℹ️  暂无相关记忆，这是新话题\n")
            
            elif role == 'assistant':
                print(f"🤖 助手: {content[:80]}{'...' if len(content) > 80 else ''}")
                print()
                
                # 判断是否存储为记忆
                if self.should_store_as_memory(content, role):
                    importance = self.calculate_memory_importance(content, role)
                    self.store.add_memory(content, importance=importance)
                    self.memory_usage_stats['memories_stored'] += 1
                    
                    print(f"   📝 已存储为记忆 (重要性: {importance:.2f})")
                else:
                    print(f"   ℹ️  未存储（非关键信息）")
            
            # 记录对话日志
            self.conversation_log.append({
                'turn': i,
                'role': role,
                'content': content,
                'memories_retrieved': len(relevant_memories) if role == 'user' else 0,
                'memory_stored': self.should_store_as_memory(content, role) if role == 'assistant' else False
            })
        
        print(f"\n{'=' * 70}")
        print("✅ 对话模拟完成")
        print(f"{'=' * 70}\n")
    
    def analyze_memory_effectiveness(self):
        """分析记忆系统的效果"""
        print("\n" + "=" * 70)
        print("📊 Memory Tool 效果分析")
        print("=" * 70)
        
        stats = self.memory_usage_stats
        total_memories = len(self.store.memories)
        
        print(f"\n📈 统计数据:")
        print(f"   • 总对话轮次: {len(self.conversation_log)}")
        print(f"   • 存储的记忆数: {stats['memories_stored']}")
        print(f"   • 记忆库大小: {total_memories} 条")
        print(f"   • 检索次数: {stats['memories_retrieved']}")
        print(f"   • 有用的检索: {stats['useful_retrievals']}")
        print(f"   • 上下文增强次数: {stats['contexts_enhanced']}")
        
        # 计算效率指标
        user_turns = sum(1 for log in self.conversation_log if log['role'] == 'user')
        if user_turns > 0:
            retrieval_rate = stats['contexts_enhanced'] / user_turns * 100
            print(f"\n📊 效率指标:")
            print(f"   • 记忆命中率: {retrieval_rate:.1f}%")
            print(f"     (在 {user_turns} 次用户提问中，{stats['contexts_enhanced']} 次找到相关记忆)")
        
        if stats['memories_retrieved'] > 0:
            usefulness_rate = stats['useful_retrievals'] / stats['memories_retrieved'] * 100
            print(f"   • 记忆有用率: {usefulness_rate:.1f}%")
            print(f"     (检索到的记忆中，有 {usefulness_rate:.1f}% 是高度相关的)")
        
        print(f"\n💡 分析:")
        if retrieval_rate > 60:
            print(f"   ✅ 记忆系统表现优秀！大部分提问都能找到相关上下文")
        elif retrieval_rate > 30:
            print(f"   ✓ 记忆系统表现良好，能为部分对话提供上下文")
        else:
            print(f"   ⚠️  记忆命中率较低，可能需要调整存储策略")
        
        if total_memories > 0:
            avg_importance = sum(m['importance'] for m in self.store.memories) / total_memories
            print(f"   • 平均记忆重要性: {avg_importance:.3f}")
    
    def test_memory_recall_scenarios(self):
        """测试记忆召回场景"""
        print("\n" + "=" * 70)
        print("🧪 测试记忆召回能力")
        print("=" * 70)
        
        # 定义测试查询
        test_queries = [
            "如何学习编程",
            "机器学习相关",
            "数据库优化",
            "Git 使用技巧",
            "系统设计",
        ]
        
        print("\n测试不同主题的记忆召回:\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"{i}. 查询: \"{query}\"")
            results = self.store.search(query, top_k=3)
            
            if results and results[0]['similarity'] > 0.5:
                print(f"   ✅ 找到相关记忆:")
                for j, r in enumerate(results[:2], 1):
                    if r['similarity'] > 0.5:
                        print(f"      [{j}] (相似度: {r['similarity']:.3f}) {r['text'][:60]}...")
            else:
                print(f"   ℹ️  未找到相关记忆")
            print()
    
    def test_memory_decay_effect(self):
        """测试时间衰减效果"""
        print("\n" + "=" * 70)
        print("⏰ 测试时间衰减机制")
        print("=" * 70)
        
        if not self.store.memories:
            print("\n⚠️  没有记忆数据，跳过衰减测试")
            return
        
        # 记录衰减前
        before_importances = [m['importance'] for m in self.store.memories[:5]]
        
        print(f"\n衰减前前5条记忆的重要性:")
        for i, imp in enumerate(before_importances, 1):
            print(f"   记忆 {i}: {imp:.4f}")
        
        # 执行衰减（半衰期7天）
        print(f"\n执行时间衰减 (半衰期: 7天)...")
        self.store.decay(half_life_days=7.0)
        
        # 记录衰减后
        after_importances = [m['importance'] for m in self.store.memories[:5]]
        
        print(f"\n衰减后前5条记忆的重要性:")
        for i, imp in enumerate(after_importances, 1):
            change = ((imp - before_importances[i-1]) / before_importances[i-1] * 100)
            print(f"   记忆 {i}: {imp:.4f} (变化: {change:.2f}%)")
        
        print(f"\n💡 说明: 刚创建的记忆衰减很小，真实场景中历史记忆会逐渐淡化")
    
    def generate_report(self, output_file: str = "memory_test_report.json"):
        """生成测试报告"""
        report = {
            'test_time': datetime.now().isoformat(),
            'statistics': self.memory_usage_stats,
            'total_conversations': len(self.conversation_log),
            'total_memories': len(self.store.memories),
            'conversation_log': self.conversation_log[:10],  # 只保存前10条
            'memory_samples': [
                {
                    'text': m['text'][:100],
                    'importance': m['importance'],
                    'timestamp': m['timestamp']
                }
                for m in self.store.memories[:5]
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试报告已保存: {output_file}")


def main():
    """主测试流程"""
    print("\n" + "=" * 70)
    print("🧠 Memory Tool 对话场景测试系统")
    print("=" * 70)
    
    print("\n📖 测试说明:")
    print("本测试将模拟实际对话场景，演示 Memory Tool 如何:")
    print("  1. 在用户提问时检索相关历史记忆")
    print("  2. 存储重要的对话内容作为未来参考")
    print("  3. 评估记忆系统对对话质量的提升")
    print()
    
    # 配置 - 支持命令行参数
    import sys
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # 自动查找可用的对话文件
        possible_files = [
            "conversations.json",      # 优先使用 conversations.json
            "chatgpt_export.json",
            "chatgpt_export_example.json"
        ]
        json_file = None
        for file in possible_files:
            if os.path.exists(file):
                json_file = file
                break
        
        if not json_file:
            json_file = "chatgpt_export.json"  # 默认值
    
    # 检查文件
    if not os.path.exists(json_file):
        print(f"❌ 错误: 找不到文件 '{json_file}'")
        print("\n请确保:")
        print("  1. 已准备好 ChatGPT 对话历史文件")
        print("  2. 文件命名为 chatgpt_export.json")
        print("  3. 文件在项目根目录")
        print("\n或运行以下命令创建示例文件:")
        print("  python tests/import_chatgpt_history.py")
        return
    
    try:
        # 创建测试器
        tester = ConversationMemoryTester()
        
        # 1. 加载对话历史
        conversations = tester.load_conversation_history(json_file)
        
        if not conversations:
            print("❌ 没有找到有效的对话数据")
            return
        
        # 2. 模拟对话流程
        tester.simulate_conversation_with_memory(conversations)
        
        # 3. 分析效果
        tester.analyze_memory_effectiveness()
        
        # 4. 测试记忆召回
        tester.test_memory_recall_scenarios()
        
        # 5. 测试时间衰减
        tester.test_memory_decay_effect()
        
        # 6. 生成报告
        tester.generate_report()
        
        print("\n" + "=" * 70)
        print("🎉 测试完成!")
        print("=" * 70)
        print("\n下一步:")
        print("  • 查看详细报告: memory_test_report.json")
        print("  • 查看记忆数据: test_conversation_memory.json")
        print("  • 调整存储策略: 编辑 should_store_as_memory() 方法")
        print("  • 优化重要性计算: 编辑 calculate_memory_importance() 方法")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


