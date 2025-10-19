#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大型 conversations.json 文件测试脚本
专门处理 ChatGPT 官方导出的完整对话历史
"""

import sys
import os
import json

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_tool.memory_store import MemoryStore


def extract_messages_from_conversation(conversation, max_messages=50):
    """从单个对话中提取消息"""
    messages = []
    
    try:
        mapping = conversation.get('mapping', {})
        
        # 遍历 mapping 获取消息
        for node_id, node in mapping.items():
            if not node.get('message'):
                continue
            
            msg = node['message']
            author = msg.get('author', {})
            role = author.get('role', 'unknown')
            
            # 跳过系统消息
            if role == 'system':
                continue
            
            content_data = msg.get('content', {})
            parts = content_data.get('parts', [])
            
            # 合并所有 parts
            content = ' '.join(str(part) for part in parts if part)
            
            if content and len(content.strip()) > 0:
                messages.append({
                    'role': role,
                    'content': content,
                    'timestamp': msg.get('create_time', None)
                })
                
                if len(messages) >= max_messages:
                    break
        
        # 按时间排序
        messages.sort(key=lambda m: m.get('timestamp', 0) or 0)
        
    except Exception as e:
        print(f"警告: 解析对话时出错: {e}")
    
    return messages


def load_conversations_incrementally(json_file, max_conversations=5, max_messages_per_conv=20):
    """增量加载对话，避免内存溢出"""
    print(f"\n📂 正在加载大型对话文件: {json_file}")
    print(f"   限制: 最多 {max_conversations} 个对话，每个对话最多 {max_messages_per_conv} 条消息")
    print()
    
    all_messages = []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            # 读取文件开头以确定格式
            content = f.read(1024 * 1024)  # 读取前 1MB
            f.seek(0)
            
            # 尝试解析为 JSON
            print("正在解析 JSON...")
            data = json.load(f)
        
        if isinstance(data, list):
            total_conversations = len(data)
            print(f"✅ 找到 {total_conversations} 个对话")
            print()
            
            # 只处理前N个对话
            conversations_to_process = data[:max_conversations]
            
            for i, conversation in enumerate(conversations_to_process, 1):
                title = conversation.get('title', f'对话 {i}')
                print(f"处理对话 {i}/{len(conversations_to_process)}: {title[:50]}...")
                
                messages = extract_messages_from_conversation(conversation, max_messages_per_conv)
                print(f"  提取了 {len(messages)} 条消息")
                
                all_messages.extend(messages)
            
            print()
            print(f"✅ 总共提取了 {len(all_messages)} 条消息")
            
        else:
            print("❌ 不支持的 JSON 格式")
            return []
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    return all_messages


def test_with_large_file(json_file="conversations.json", 
                        max_conversations=3, 
                        max_messages_per_conv=20):
    """使用大型文件测试"""
    
    print("\n" + "=" * 70)
    print("🧠 大型 Conversations.json 文件测试")
    print("=" * 70)
    
    # 加载消息
    messages = load_conversations_incrementally(
        json_file, 
        max_conversations=max_conversations,
        max_messages_per_conv=max_messages_per_conv
    )
    
    if not messages:
        print("\n❌ 没有提取到有效消息")
        return
    
    # 创建 Memory Store
    print("\n" + "=" * 70)
    print("开始模拟对话场景")
    print("=" * 70)
    
    store = MemoryStore(path="test_large_conversations_memory.json")
    stats = {
        'stored': 0,
        'retrieved': 0,
        'useful_retrievals': 0
    }
    
    # 模拟对话
    for i, msg in enumerate(messages, 1):
        role = msg['role']
        content = msg['content']
        
        print(f"\n{'─' * 70}")
        print(f"消息 #{i}")
        print(f"{'─' * 70}")
        
        if role == 'user':
            print(f"👤 用户: {content[:100]}{'...' if len(content) > 100 else ''}")
            
            # 检索相关记忆
            if store.memories:
                print("\n🧠 检索相关记忆...")
                results = store.search(content, top_k=3)
                
                relevant = [r for r in results if r['similarity'] > 0.5]
                if relevant:
                    print(f"   ✅ 找到 {len(relevant)} 条相关记忆:")
                    for j, r in enumerate(relevant[:2], 1):
                        print(f"      [{j}] (相似度: {r['similarity']:.3f}) {r['text'][:80]}...")
                    stats['useful_retrievals'] += 1
                else:
                    print("   ℹ️  相关性较低")
                
                stats['retrieved'] += len(results)
        
        elif role == 'assistant':
            print(f"🤖 助手: {content[:100]}{'...' if len(content) > 100 else ''}")
            
            # 判断是否存储
            if len(content) > 50 and any(kw in content for kw in ['方法', '步骤', '可以', '需要', '建议']):
                importance = 0.7
                if len(content) > 200:
                    importance += 0.2
                
                store.add_memory(content, importance=importance)
                stats['stored'] += 1
                print(f"   📝 已存储为记忆 (重要性: {importance:.2f})")
    
    # 统计
    print("\n" + "=" * 70)
    print("📊 测试统计")
    print("=" * 70)
    print(f"   • 处理的消息数: {len(messages)}")
    print(f"   • 存储的记忆数: {stats['stored']}")
    print(f"   • 检索次数: {stats['retrieved']}")
    print(f"   • 有用的检索: {stats['useful_retrievals']}")
    print(f"   • 记忆库大小: {len(store.memories)} 条")
    
    user_messages = sum(1 for m in messages if m['role'] == 'user')
    if user_messages > 0:
        hit_rate = stats['useful_retrievals'] / user_messages * 100
        print(f"   • 记忆命中率: {hit_rate:.1f}%")
    
    # 测试搜索
    print("\n" + "=" * 70)
    print("🔍 测试记忆搜索")
    print("=" * 70)
    
    test_queries = [
        "编程相关",
        "如何学习",
        "问题解决",
    ]
    
    for query in test_queries:
        print(f"\n查询: \"{query}\"")
        results = store.search(query, top_k=3)
        if results and results[0]['similarity'] > 0.4:
            for i, r in enumerate(results[:2], 1):
                if r['similarity'] > 0.4:
                    print(f"   [{i}] (相似度: {r['similarity']:.3f}) {r['text'][:80]}...")
        else:
            print("   ℹ️  未找到相关记忆")
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    print(f"\n记忆数据已保存: test_large_conversations_memory.json")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试大型 conversations.json 文件')
    parser.add_argument('--file', default='conversations.json', help='对话文件路径')
    parser.add_argument('--conversations', type=int, default=3, help='最多处理多少个对话')
    parser.add_argument('--messages', type=int, default=20, help='每个对话最多提取多少条消息')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ 错误: 找不到文件 '{args.file}'")
        print("\n请确保:")
        print("  1. 文件存在")
        print("  2. 文件路径正确")
        print("\n使用方法:")
        print(f"  python {sys.argv[0]} --file conversations.json --conversations 5 --messages 30")
        return
    
    test_with_large_file(
        json_file=args.file,
        max_conversations=args.conversations,
        max_messages_per_conv=args.messages
    )


if __name__ == "__main__":
    main()

