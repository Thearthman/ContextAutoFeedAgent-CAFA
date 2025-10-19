#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Tool 交互式测试工具
允许用户手动操作：检索记忆、调整权重、管理记忆等
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


class InteractiveMemoryTool:
    """交互式 Memory Tool"""
    
    def __init__(self, memory_file="interactive_memory.json"):
        self.store = MemoryStore(path=memory_file)
        self.memory_file = memory_file
        
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "=" * 70)
        print("🧠 Memory Tool 交互式测试")
        print("=" * 70)
        print("\n选择操作:")
        print("  1. 🔍 检索记忆 (输入查询)")
        print("  2. 📝 添加记忆 (手动输入)")
        print("  3. 📊 查看所有记忆")
        print("  4. ⚖️  调整记忆权重")
        print("  5. 🗑️  删除记忆")
        print("  6. ⏰ 执行时间衰减")
        print("  7. 📥 从 conversations.json 导入")
        print("  8. 📈 显示统计信息")
        print("  9. 💾 保存并退出")
        print("  0. ❌ 退出")
        print("\n" + "=" * 70)
        
    def search_memory(self):
        """交互式检索记忆"""
        print("\n" + "─" * 70)
        print("🔍 检索记忆")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空，请先添加或导入记忆")
            return
        
        query = input("\n输入查询内容 (或按 Enter 返回): ").strip()
        if not query:
            return
        
        top_k = input("返回多少条结果？ (默认 5): ").strip()
        top_k = int(top_k) if top_k.isdigit() else 5
        
        print(f"\n🔍 搜索: \"{query}\"")
        print("─" * 70)
        
        results = self.store.search(query, top_k=top_k)
        
        if not results:
            print("😕 没有找到相关记忆")
            return
        
        for i, result in enumerate(results, 1):
            similarity = result['similarity']
            text = result['text']
            
            # 根据相似度显示不同颜色（用符号表示）
            if similarity > 0.8:
                level = "🔥 极度相关"
            elif similarity > 0.6:
                level = "✅ 高度相关"
            elif similarity > 0.4:
                level = "✓  相关"
            else:
                level = "-  弱相关"
            
            print(f"\n[{i}] {level} (相似度: {similarity:.3f})")
            print(f"    {text[:150]}{'...' if len(text) > 150 else ''}")
        
        # 询问是否查看完整内容
        view = input("\n查看某条记忆的完整内容？输入序号 (或按 Enter 跳过): ").strip()
        if view.isdigit() and 1 <= int(view) <= len(results):
            idx = int(view) - 1
            print("\n" + "─" * 70)
            print("完整内容:")
            print("─" * 70)
            print(results[idx]['text'])
    
    def add_memory(self):
        """手动添加记忆"""
        print("\n" + "─" * 70)
        print("📝 添加记忆")
        print("─" * 70)
        
        print("\n输入记忆内容 (多行输入，输入 END 结束):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        
        text = '\n'.join(lines).strip()
        if not text:
            print("⚠️  内容为空，取消添加")
            return
        
        importance = input("\n重要性 (0-1，默认 0.7): ").strip()
        importance = float(importance) if importance else 0.7
        importance = max(0.0, min(1.0, importance))  # 限制在 0-1
        
        self.store.add_memory(text, importance=importance)
        print(f"\n✅ 已添加记忆 (重要性: {importance:.2f})")
    
    def view_all_memories(self):
        """查看所有记忆"""
        print("\n" + "─" * 70)
        print("📊 所有记忆")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空")
            return
        
        # 按重要性排序
        sorted_memories = sorted(
            enumerate(self.store.memories), 
            key=lambda x: x[1]['importance'], 
            reverse=True
        )
        
        for i, (idx, mem) in enumerate(sorted_memories, 1):
            importance = mem['importance']
            text = mem['text']
            timestamp = mem.get('timestamp', 'N/A')
            
            print(f"\n[{i}] 重要性: {importance:.3f} | 时间: {timestamp[:19] if timestamp != 'N/A' else 'N/A'}")
            print(f"    {text[:100]}{'...' if len(text) > 100 else ''}")
        
        print(f"\n共 {len(self.store.memories)} 条记忆")
    
    def adjust_weight(self):
        """调整记忆权重"""
        print("\n" + "─" * 70)
        print("⚖️  调整记忆权重")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空")
            return
        
        # 显示记忆列表
        for i, mem in enumerate(self.store.memories, 1):
            print(f"[{i}] 重要性: {mem['importance']:.3f} | {mem['text'][:60]}...")
        
        idx = input(f"\n选择要调整的记忆 (1-{len(self.store.memories)}): ").strip()
        if not idx.isdigit() or not (1 <= int(idx) <= len(self.store.memories)):
            print("⚠️  无效的序号")
            return
        
        idx = int(idx) - 1
        current = self.store.memories[idx]['importance']
        
        print(f"\n当前重要性: {current:.3f}")
        new_importance = input("新的重要性 (0-1): ").strip()
        
        try:
            new_importance = float(new_importance)
            new_importance = max(0.0, min(1.0, new_importance))
            
            self.store.memories[idx]['importance'] = new_importance
            self.store._save()
            
            print(f"✅ 已更新: {current:.3f} → {new_importance:.3f}")
        except ValueError:
            print("⚠️  无效的数值")
    
    def delete_memory(self):
        """删除记忆"""
        print("\n" + "─" * 70)
        print("🗑️  删除记忆")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空")
            return
        
        # 显示记忆列表
        for i, mem in enumerate(self.store.memories, 1):
            print(f"[{i}] {mem['text'][:80]}...")
        
        idx = input(f"\n选择要删除的记忆 (1-{len(self.store.memories)}): ").strip()
        if not idx.isdigit() or not (1 <= int(idx) <= len(self.store.memories)):
            print("⚠️  无效的序号")
            return
        
        idx = int(idx) - 1
        deleted = self.store.memories.pop(idx)
        self.store._save()
        
        print(f"\n✅ 已删除: {deleted['text'][:60]}...")
    
    def apply_decay(self):
        """执行时间衰减"""
        print("\n" + "─" * 70)
        print("⏰ 时间衰减")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空")
            return
        
        half_life = input("半衰期 (天数，默认 7): ").strip()
        half_life = float(half_life) if half_life else 7.0
        
        print("\n衰减前的前 5 条记忆:")
        for i, mem in enumerate(self.store.memories[:5], 1):
            print(f"  [{i}] 重要性: {mem['importance']:.4f}")
        
        self.store.decay(half_life_days=half_life)
        
        print(f"\n✅ 已执行衰减 (半衰期: {half_life} 天)")
        print("\n衰减后的前 5 条记忆:")
        for i, mem in enumerate(self.store.memories[:5], 1):
            print(f"  [{i}] 重要性: {mem['importance']:.4f}")
    
    def import_conversations(self):
        """从 conversations.json 导入"""
        print("\n" + "─" * 70)
        print("📥 导入对话")
        print("─" * 70)
        
        file_path = input("对话文件路径 (默认 conversations.json): ").strip()
        if not file_path:
            file_path = "conversations.json"
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return
        
        max_conv = input("导入多少个对话？ (默认 3): ").strip()
        max_conv = int(max_conv) if max_conv.isdigit() else 3
        
        max_msg = input("每个对话最多多少条消息？ (默认 10): ").strip()
        max_msg = int(max_msg) if max_msg.isdigit() else 10
        
        print(f"\n正在导入...")
        
        try:
            # 使用 test_large_conversations.py 的逻辑
            from test_large_conversations import extract_messages_from_conversation
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                count = 0
                for conv in data[:max_conv]:
                    messages = extract_messages_from_conversation(conv, max_msg)
                    for msg in messages:
                        if msg['role'] == 'assistant' and len(msg['content']) > 50:
                            self.store.add_memory(msg['content'], importance=0.7)
                            count += 1
                
                print(f"✅ 已导入 {count} 条记忆")
            else:
                print("❌ 不支持的文件格式")
        
        except Exception as e:
            print(f"❌ 导入失败: {e}")
    
    def show_stats(self):
        """显示统计信息"""
        print("\n" + "─" * 70)
        print("📈 统计信息")
        print("─" * 70)
        
        if not self.store.memories:
            print("⚠️  记忆库为空")
            return
        
        importances = [m['importance'] for m in self.store.memories]
        lengths = [len(m['text']) for m in self.store.memories]
        
        print(f"\n总记忆数: {len(self.store.memories)}")
        print(f"\n重要性统计:")
        print(f"  • 平均: {sum(importances) / len(importances):.3f}")
        print(f"  • 最高: {max(importances):.3f}")
        print(f"  • 最低: {min(importances):.3f}")
        
        print(f"\n长度统计:")
        print(f"  • 平均: {sum(lengths) / len(lengths):.0f} 字符")
        print(f"  • 最长: {max(lengths)} 字符")
        print(f"  • 最短: {min(lengths)} 字符")
        
        # 重要性分布
        high = sum(1 for i in importances if i > 0.7)
        medium = sum(1 for i in importances if 0.4 <= i <= 0.7)
        low = sum(1 for i in importances if i < 0.4)
        
        print(f"\n重要性分布:")
        print(f"  • 高 (>0.7): {high} 条 ({high/len(importances)*100:.1f}%)")
        print(f"  • 中 (0.4-0.7): {medium} 条 ({medium/len(importances)*100:.1f}%)")
        print(f"  • 低 (<0.4): {low} 条 ({low/len(importances)*100:.1f}%)")
    
    def run(self):
        """运行交互式界面"""
        print("\n" + "=" * 70)
        print("欢迎使用 Memory Tool 交互式测试工具")
        print("=" * 70)
        print(f"\n记忆文件: {self.memory_file}")
        print(f"当前记忆数: {len(self.store.memories)}")
        
        while True:
            self.show_menu()
            
            choice = input("\n请选择操作 (0-9): ").strip()
            
            if choice == '1':
                self.search_memory()
            elif choice == '2':
                self.add_memory()
            elif choice == '3':
                self.view_all_memories()
            elif choice == '4':
                self.adjust_weight()
            elif choice == '5':
                self.delete_memory()
            elif choice == '6':
                self.apply_decay()
            elif choice == '7':
                self.import_conversations()
            elif choice == '8':
                self.show_stats()
            elif choice == '9':
                print("\n💾 正在保存...")
                self.store._save()
                print("✅ 已保存，再见！")
                break
            elif choice == '0':
                save = input("\n保存更改？ (y/n): ").strip().lower()
                if save == 'y':
                    self.store._save()
                    print("✅ 已保存")
                print("👋 再见！")
                break
            else:
                print("⚠️  无效的选择，请重新输入")
            
            input("\n按 Enter 继续...")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Tool 交互式测试')
    parser.add_argument('--file', default='interactive_memory.json', 
                       help='记忆文件路径')
    
    args = parser.parse_args()
    
    tool = InteractiveMemoryTool(memory_file=args.file)
    
    try:
        tool.run()
    except KeyboardInterrupt:
        print("\n\n👋 已中断，再见！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


