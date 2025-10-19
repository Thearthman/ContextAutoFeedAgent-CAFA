#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ChatGPT 聊天记录导入工具
将 ChatGPT 导出的聊天记录导入到 Memory Tool 中进行测试
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 设置 Windows 控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_tool.memory_store import MemoryStore


class ChatGPTImporter:
    """ChatGPT 聊天记录导入器"""
    
    def __init__(self, memory_file: str = "chatgpt_memory_test.json"):
        """
        初始化导入器
        
        Args:
            memory_file: Memory Tool 存储文件名
        """
        self.store = MemoryStore(path=memory_file)
        self.imported_count = 0
        self.skipped_count = 0
        
    def import_from_json(self, json_file: str, 
                        filter_role: str = None, 
                        min_length: int = 10,
                        importance_base: float = 0.7):
        """
        从 ChatGPT 导出的 JSON 文件中导入聊天记录
        
        Args:
            json_file: ChatGPT 导出的 JSON 文件路径
            filter_role: 只导入特定角色的消息 ('user', 'assistant', 或 None 表示全部)
            min_length: 最小文本长度，过滤掉太短的消息
            importance_base: 基础重要性值 (0-1)
        """
        print(f"\n📂 正在读取文件: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持不同的 ChatGPT 导出格式
        conversations = self._parse_chatgpt_format(data)
        
        print(f"✅ 找到 {len(conversations)} 条对话记录\n")
        print("=" * 60)
        print("开始导入...")
        print("=" * 60)
        
        for conv in conversations:
            role = conv.get('role', 'unknown')
            content = conv.get('content', '')
            timestamp = conv.get('timestamp', None)
            
            # 应用过滤条件
            if filter_role and role != filter_role:
                self.skipped_count += 1
                continue
                
            if len(content.strip()) < min_length:
                self.skipped_count += 1
                continue
            
            # 计算重要性 (可以根据长度、角色等因素调整)
            importance = self._calculate_importance(content, role, importance_base)
            
            # 添加到 Memory Store
            self.store.add_memory(content, importance=importance)
            self.imported_count += 1
            
            # 显示进度
            print(f"✓ [{self.imported_count:3d}] {role:10s} | {content[:60]}...")
        
        print("=" * 60)
        print(f"\n✅ 导入完成!")
        print(f"   导入: {self.imported_count} 条")
        print(f"   跳过: {self.skipped_count} 条")
        print(f"   总计: {self.imported_count + self.skipped_count} 条")
        
    def _parse_chatgpt_format(self, data):
        """
        解析 ChatGPT 的不同导出格式
        
        支持的格式:
        1. 标准对话格式: [{"role": "user", "content": "..."}]
        2. 完整导出格式: {"conversations": [...], "title": "..."}
        3. 单个对话格式: {"mapping": {...}, "title": "..."}
        """
        conversations = []
        
        # 格式1: 直接是消息数组
        if isinstance(data, list):
            for msg in data:
                if isinstance(msg, dict) and 'content' in msg:
                    conversations.append({
                        'role': msg.get('role', 'unknown'),
                        'content': msg.get('content', ''),
                        'timestamp': msg.get('timestamp', None)
                    })
        
        # 格式2: 包含 conversations 字段
        elif isinstance(data, dict) and 'conversations' in data:
            for conv in data['conversations']:
                if 'messages' in conv:
                    for msg in conv['messages']:
                        conversations.append({
                            'role': msg.get('role', 'unknown'),
                            'content': msg.get('content', ''),
                            'timestamp': msg.get('timestamp', None)
                        })
        
        # 格式3: ChatGPT 官方导出格式 (mapping 结构)
        elif isinstance(data, dict) and 'mapping' in data:
            mapping = data['mapping']
            for node_id, node in mapping.items():
                if node.get('message'):
                    msg = node['message']
                    content_parts = msg.get('content', {}).get('parts', [])
                    content = ' '.join(str(part) for part in content_parts if part)
                    
                    if content:
                        conversations.append({
                            'role': msg.get('author', {}).get('role', 'unknown'),
                            'content': content,
                            'timestamp': msg.get('create_time', None)
                        })
        
        # 格式4: 简单的文本数组
        elif isinstance(data, dict) and 'messages' in data:
            for msg in data['messages']:
                conversations.append({
                    'role': msg.get('role', 'unknown'),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', None)
                })
        
        return conversations
    
    def _calculate_importance(self, content: str, role: str, base: float) -> float:
        """
        根据内容特征计算重要性
        
        Args:
            content: 消息内容
            role: 角色 (user/assistant)
            base: 基础重要性值
        """
        importance = base
        
        # 根据长度调整重要性
        if len(content) > 200:
            importance += 0.1
        if len(content) > 500:
            importance += 0.1
        
        # 用户提问通常更重要
        if role == 'user':
            importance += 0.05
        
        # 限制在 0-1 范围内
        return min(1.0, importance)
    
    def test_search(self, queries: list):
        """
        测试导入的记忆搜索功能
        
        Args:
            queries: 要测试的查询列表
        """
        print("\n" + "=" * 60)
        print("🔍 测试记忆搜索功能")
        print("=" * 60)
        
        for query in queries:
            print(f"\n查询: \"{query}\"")
            print("-" * 60)
            results = self.store.search(query, top_k=3)
            
            for i, result in enumerate(results, 1):
                print(f"{i}. [相似度: {result['similarity']:.3f}]")
                print(f"   {result['text'][:100]}...")
                print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("ChatGPT 聊天记录导入工具")
    print("=" * 60)
    
    # 使用示例
    print("\n📖 使用说明:")
    print("1. 从 ChatGPT 导出聊天记录 (JSON 格式)")
    print("2. 将 JSON 文件放在项目根目录或 tests 目录")
    print("3. 修改下面的 json_file 路径指向你的文件")
    print("4. 运行本脚本: python tests/import_chatgpt_history.py\n")
    
    # ========== 配置区域 ==========
    # 请修改这里的文件路径为你的 ChatGPT 导出文件
    json_file = "chatgpt_export.json"  # 修改为你的文件路径
    
    # 过滤选项
    filter_role = None  # None=全部, 'user'=只导入用户消息, 'assistant'=只导入助手消息
    min_length = 10  # 最小文本长度
    importance_base = 0.7  # 基础重要性 (0-1)
    
    # 测试查询
    test_queries = [
        "Python 编程",
        "机器学习",
        "数据库",
    ]
    # ========== 配置区域结束 ==========
    
    # 检查文件是否存在
    if not os.path.exists(json_file):
        print(f"\n❌ 错误: 找不到文件 '{json_file}'")
        print("\n请按以下步骤操作:")
        print("1. 打开 ChatGPT (https://chat.openai.com)")
        print("2. 点击左下角个人头像 > Settings > Data controls")
        print("3. 点击 'Export data' 导出数据")
        print("4. 等待邮件通知，下载 conversations.json 文件")
        print("5. 将文件重命名为 chatgpt_export.json 并放在项目根目录")
        print("\n或者创建一个测试文件:")
        print('   echo \'[{"role":"user","content":"测试消息"}]\' > chatgpt_export.json\n')
        
        # 创建示例文件
        try:
            create_example = input("是否创建示例文件用于测试? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # 非交互式环境，自动创建示例文件
            create_example = 'y'
            print("检测到非交互式环境，自动创建示例文件...")
        
        if create_example == 'y':
            example_data = [
                {"role": "user", "content": "如何学习 Python 编程？"},
                {"role": "assistant", "content": "学习 Python 可以从以下几个方面入手：1. 基础语法 2. 数据结构 3. 面向对象编程 4. 实践项目"},
                {"role": "user", "content": "什么是机器学习？"},
                {"role": "assistant", "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策，而无需明确编程。"},
                {"role": "user", "content": "SQL 数据库如何优化查询性能？"},
                {"role": "assistant", "content": "数据库查询优化可以通过以下方式：1. 创建索引 2. 优化查询语句 3. 避免 SELECT * 4. 使用 EXPLAIN 分析查询计划"},
            ]
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(example_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已创建示例文件: {json_file}")
        else:
            return
    
    # 开始导入
    try:
        importer = ChatGPTImporter()
        importer.import_from_json(
            json_file=json_file,
            filter_role=filter_role,
            min_length=min_length,
            importance_base=importance_base
        )
        
        # 测试搜索功能
        importer.test_search(test_queries)
        
        print("\n" + "=" * 60)
        print("🎉 测试完成!")
        print("=" * 60)
        print(f"\n记忆数据已保存到: chatgpt_memory_test.json")
        print("你可以继续使用以下命令测试:")
        print("  python tests/test_memory_basic.py")
        print("  python run_memory_api.py")
        
    except Exception as e:
        print(f"\n❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

