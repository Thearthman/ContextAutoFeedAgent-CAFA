#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Tool 自动检索测试工具
自动检索所有内容，分析检索质量和效果
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_tool.memory_store import MemoryStore


class AutoRetrievalTester:
    """自动检索测试器"""
    
    def __init__(self, memory_file="auto_retrieval_memory.json"):
        self.store = MemoryStore(path=memory_file)
        self.memory_file = memory_file
        self.results = {
            'total_queries': 0,
            'total_retrievals': 0,
            'high_similarity_count': 0,
            'medium_similarity_count': 0,
            'low_similarity_count': 0,
            'queries': []
        }
        
    def load_from_conversations(self, json_file="conversations.json", 
                                max_conversations=10, 
                                max_messages=20):
        """从 conversations.json 加载数据"""
        print("\n" + "=" * 70)
        print("📥 加载对话数据")
        print("=" * 70)
        
        if not os.path.exists(json_file):
            print(f"❌ 文件不存在: {json_file}")
            return False
        
        print(f"正在从 {json_file} 加载...")
        print(f"配置: {max_conversations} 个对话, 每个对话 {max_messages} 条消息\n")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                count = 0
                for conv in data[:max_conversations]:
                    title = conv.get('title', f'对话 {count+1}')
                    print(f"处理对话: {title[:50]}...")
                    
                    messages = self._extract_messages(conv, max_messages)
                    for msg in messages:
                        # 存储助手回答
                        if msg['role'] == 'assistant' and len(msg['content']) > 50:
                            self.store.add_memory(msg['content'], importance=0.7)
                            count += 1
                
                print(f"\n✅ 已加载 {count} 条记忆到记忆库")
                return True
            else:
                print("❌ 不支持的文件格式")
                return False
        
        except Exception as e:
            print(f"❌ 加载失败: {e}")
            return False
    
    def _extract_messages(self, conversation, max_messages):
        """从对话中提取消息"""
        messages = []
        
        try:
            mapping = conversation.get('mapping', {})
            for node_id, node in mapping.items():
                if not node.get('message'):
                    continue
                
                msg = node['message']
                author = msg.get('author', {})
                role = author.get('role', 'unknown')
                
                if role == 'system':
                    continue
                
                content_data = msg.get('content', {})
                parts = content_data.get('parts', [])
                content = ' '.join(str(part) for part in parts if part)
                
                if content and len(content.strip()) > 0:
                    messages.append({
                        'role': role,
                        'content': content,
                        'timestamp': msg.get('create_time', None)
                    })
                    
                    if len(messages) >= max_messages:
                        break
            
            messages.sort(key=lambda m: m.get('timestamp', 0) or 0)
        
        except Exception as e:
            print(f"  警告: 提取消息出错: {e}")
        
        return messages
    
    def auto_retrieve_all(self, top_k=5, similarity_threshold=0.4):
        """自动检索所有记忆"""
        print("\n" + "=" * 70)
        print("🔍 开始自动检索测试")
        print("=" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空，请先加载数据")
            return
        
        total_memories = len(self.store.memories)
        print(f"\n记忆库大小: {total_memories} 条")
        print(f"检索参数: top_k={top_k}, 相似度阈值={similarity_threshold}")
        print("\n开始批量检索...\n")
        
        # 使用每条记忆作为查询
        for i, memory in enumerate(self.store.memories, 1):
            query = memory['text'][:200]  # 使用前200字符作为查询
            
            print(f"[{i}/{total_memories}] 检索中...")
            
            # 执行检索
            results = self.store.search(query, top_k=top_k)
            
            # 分析结果
            query_result = {
                'query_idx': i,
                'query_text': query[:100],
                'results': []
            }
            
            high_sim = 0
            medium_sim = 0
            low_sim = 0
            
            for result in results:
                similarity = result['similarity']
                
                if similarity > 0.8:
                    high_sim += 1
                elif similarity > 0.5:
                    medium_sim += 1
                else:
                    low_sim += 1
                
                query_result['results'].append({
                    'text': result['text'][:100],
                    'similarity': similarity
                })
            
            self.results['queries'].append(query_result)
            self.results['total_queries'] += 1
            self.results['total_retrievals'] += len(results)
            self.results['high_similarity_count'] += high_sim
            self.results['medium_similarity_count'] += medium_sim
            self.results['low_similarity_count'] += low_sim
            
            # 显示进度
            if i % 10 == 0 or i == total_memories:
                print(f"  进度: {i}/{total_memories} ({i/total_memories*100:.1f}%)")
        
        print(f"\n✅ 检索完成！共执行 {total_memories} 次检索")
    
    def analyze_results(self):
        """分析检索结果"""
        print("\n" + "=" * 70)
        print("📊 检索结果分析")
        print("=" * 70)
        
        if self.results['total_queries'] == 0:
            print("⚠️  没有检索结果")
            return
        
        total_queries = self.results['total_queries']
        total_retrievals = self.results['total_retrievals']
        high_sim = self.results['high_similarity_count']
        medium_sim = self.results['medium_similarity_count']
        low_sim = self.results['low_similarity_count']
        
        print(f"\n📈 总体统计:")
        print(f"  • 查询次数: {total_queries}")
        print(f"  • 检索结果总数: {total_retrievals}")
        print(f"  • 平均每次检索结果数: {total_retrievals/total_queries:.1f}")
        
        print(f"\n🎯 相似度分布:")
        print(f"  • 高相似度 (>0.8): {high_sim} 条 ({high_sim/total_retrievals*100:.1f}%)")
        print(f"  • 中相似度 (0.5-0.8): {medium_sim} 条 ({medium_sim/total_retrievals*100:.1f}%)")
        print(f"  • 低相似度 (<0.5): {low_sim} 条 ({low_sim/total_retrievals*100:.1f}%)")
        
        # 计算平均相似度
        all_similarities = []
        for query in self.results['queries']:
            for result in query['results']:
                all_similarities.append(result['similarity'])
        
        if all_similarities:
            avg_sim = sum(all_similarities) / len(all_similarities)
            max_sim = max(all_similarities)
            min_sim = min(all_similarities)
            
            print(f"\n📊 相似度统计:")
            print(f"  • 平均相似度: {avg_sim:.3f}")
            print(f"  • 最高相似度: {max_sim:.3f}")
            print(f"  • 最低相似度: {min_sim:.3f}")
        
        # 质量评估
        print(f"\n💡 质量评估:")
        if high_sim / total_retrievals > 0.5:
            print(f"  ✅ 优秀 - 超过一半的检索结果高度相关")
        elif high_sim / total_retrievals > 0.3:
            print(f"  ✓  良好 - 有较多高度相关的结果")
        else:
            print(f"  ⚠️  需改进 - 高相关结果较少，建议优化向量化或存储策略")
    
    def show_top_queries(self, n=10):
        """显示最佳和最差的检索结果"""
        print("\n" + "=" * 70)
        print(f"🏆 检索效果示例 (前 {n} 个)")
        print("=" * 70)
        
        if not self.results['queries']:
            print("⚠️  没有检索结果")
            return
        
        # 按平均相似度排序
        sorted_queries = sorted(
            self.results['queries'],
            key=lambda q: sum(r['similarity'] for r in q['results']) / len(q['results']) if q['results'] else 0,
            reverse=True
        )
        
        print("\n📈 最佳检索示例 (相似度最高):\n")
        for i, query in enumerate(sorted_queries[:n], 1):
            if not query['results']:
                continue
            
            avg_sim = sum(r['similarity'] for r in query['results']) / len(query['results'])
            print(f"[{i}] 查询: {query['query_text']}...")
            print(f"    平均相似度: {avg_sim:.3f}")
            
            for j, result in enumerate(query['results'][:3], 1):
                print(f"    [{j}] ({result['similarity']:.3f}) {result['text'][:60]}...")
            print()
        
        print("\n" + "─" * 70)
        print("📉 需要改进的检索示例 (相似度较低):\n")
        
        for i, query in enumerate(sorted_queries[-n:], 1):
            if not query['results']:
                continue
            
            avg_sim = sum(r['similarity'] for r in query['results']) / len(query['results'])
            print(f"[{i}] 查询: {query['query_text']}...")
            print(f"    平均相似度: {avg_sim:.3f}")
            
            for j, result in enumerate(query['results'][:3], 1):
                print(f"    [{j}] ({result['similarity']:.3f}) {result['text'][:60]}...")
            print()
    
    def test_specific_queries(self, queries, top_k=5):
        """测试特定查询"""
        print("\n" + "=" * 70)
        print("🎯 特定查询测试")
        print("=" * 70)
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}] 查询: \"{query}\"")
            print("─" * 70)
            
            results = self.store.search(query, top_k=top_k)
            
            if not results:
                print("  ❌ 未找到相关结果")
                continue
            
            for j, result in enumerate(results, 1):
                similarity = result['similarity']
                text = result['text']
                
                if similarity > 0.8:
                    level = "🔥"
                elif similarity > 0.6:
                    level = "✅"
                elif similarity > 0.4:
                    level = "✓ "
                else:
                    level = "- "
                
                print(f"  [{j}] {level} 相似度: {similarity:.3f}")
                print(f"      {text[:120]}...")
    
    def export_report(self, output_file="auto_retrieval_report.json"):
        """导出检索报告"""
        report = {
            'test_time': datetime.now().isoformat(),
            'memory_file': self.memory_file,
            'statistics': {
                'total_memories': len(self.store.memories),
                'total_queries': self.results['total_queries'],
                'total_retrievals': self.results['total_retrievals'],
                'avg_results_per_query': self.results['total_retrievals'] / self.results['total_queries'] if self.results['total_queries'] > 0 else 0,
                'high_similarity_count': self.results['high_similarity_count'],
                'medium_similarity_count': self.results['medium_similarity_count'],
                'low_similarity_count': self.results['low_similarity_count'],
            },
            'sample_queries': self.results['queries'][:20]  # 保存前20个查询示例
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 检索报告已保存: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Tool 自动检索测试')
    parser.add_argument('--file', default='conversations.json', 
                       help='对话文件路径')
    parser.add_argument('--conversations', type=int, default=5, 
                       help='加载多少个对话')
    parser.add_argument('--messages', type=int, default=20, 
                       help='每个对话提取多少条消息')
    parser.add_argument('--top-k', type=int, default=5, 
                       help='每次检索返回多少结果')
    parser.add_argument('--memory', default='auto_retrieval_memory.json',
                       help='记忆文件路径')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔍 Memory Tool 自动检索测试系统")
    print("=" * 70)
    
    tester = AutoRetrievalTester(memory_file=args.memory)
    
    # 1. 加载数据
    if not tester.store.memories:
        print("\n记忆库为空，正在加载数据...")
        success = tester.load_from_conversations(
            args.file, 
            args.conversations, 
            args.messages
        )
        if not success:
            return
    else:
        print(f"\n使用现有记忆库: {args.memory}")
        print(f"记忆数: {len(tester.store.memories)}")
    
    # 2. 自动检索测试
    tester.auto_retrieve_all(top_k=args.top_k)
    
    # 3. 分析结果
    tester.analyze_results()
    
    # 4. 显示示例
    tester.show_top_queries(n=5)
    
    # 5. 测试特定查询
    test_queries = [
        "如何学习",
        "问题解决",
        "编程技巧",
        "系统设计",
    ]
    tester.test_specific_queries(test_queries, top_k=3)
    
    # 6. 导出报告
    tester.export_report()
    
    print("\n" + "=" * 70)
    print("✅ 自动检索测试完成！")
    print("=" * 70)
    print("\n查看:")
    print(f"  • 记忆数据: {args.memory}")
    print(f"  • 检索报告: auto_retrieval_report.json")


if __name__ == "__main__":
    main()


