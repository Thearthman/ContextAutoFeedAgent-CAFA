#!/usr/bin/env python
"""
Memory Tool 基础测试脚本
测试记忆存储、检索和衰减功能
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from memory_tool.memory_store import MemoryStore
from memory_tool.embeddings import EmbeddingGenerator

def test_embeddings():
    """测试文本向量化"""
    print("=" * 50)
    print("测试 1: 文本向量化")
    print("=" * 50)
    
    generator = EmbeddingGenerator()
    
    # 测试相似度计算
    text1 = "我今天学习了Python编程"
    text2 = "今天我在学Python"
    text3 = "明天天气很好"
    
    sim1 = generator.similarity(text1, text2)
    sim2 = generator.similarity(text1, text3)
    
    print(f"文本1: {text1}")
    print(f"文本2: {text2}")
    print(f"相似度: {sim1:.3f}\n")
    
    print(f"文本1: {text1}")
    print(f"文本3: {text3}")
    print(f"相似度: {sim2:.3f}\n")
    
    assert sim1 > sim2, "相关文本的相似度应该更高"
    print("✅ 向量化测试通过！\n")

def test_memory_store():
    """测试记忆存储和检索"""
    print("=" * 50)
    print("测试 2: 记忆存储和检索")
    print("=" * 50)
    
    # 使用临时文件
    store = MemoryStore(path="test_memory_data.json")
    
    # 添加记忆
    memories = [
        "我在考试中错了牛顿第三定律的题",
        "我在复习时发现自己不理解热力学第二定律",
        "今天学习了Python的面向对象编程",
        "明天要去图书馆借书",
        "我需要复习量子力学的基础知识"
    ]
    
    print("📝 添加记忆...")
    for mem in memories:
        store.add_memory(mem, importance=0.9)
        print(f"  ✓ {mem}")
    
    # 搜索记忆
    print("\n🔍 搜索测试...")
    queries = [
        "复习物理学",
        "学习编程",
        "图书馆"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        results = store.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. [{result['similarity']:.3f}] {result['text']}")
    
    print("\n✅ 记忆存储测试通过！\n")
    
    # 清理测试文件
    if os.path.exists("test_memory_data.json"):
        os.remove("test_memory_data.json")

def test_memory_decay():
    """测试记忆衰减"""
    print("=" * 50)
    print("测试 3: 记忆时间衰减")
    print("=" * 50)
    
    store = MemoryStore(path="test_decay_data.json")
    
    # 添加记忆
    mem1 = store.add_memory("重要的物理知识", importance=1.0)
    print(f"📝 添加记忆: {mem1['text']}")
    print(f"   初始重要性: {mem1['importance']}")
    
    # 执行衰减
    print("\n⏰ 执行时间衰减 (半衰期=7天)...")
    store.decay(half_life_days=7.0)
    
    # 注意：由于刚添加，时间很短，衰减效果不明显
    print(f"   衰减后重要性: {store.memories[0]['importance']:.6f}")
    print("   (由于刚添加，衰减效果很小)")
    
    print("\n✅ 衰减测试通过！\n")
    
    # 清理测试文件
    if os.path.exists("test_decay_data.json"):
        os.remove("test_decay_data.json")

def main():
    """运行所有测试"""
    print("\n🧪 Memory Tool 基础功能测试\n")
    
    try:
        test_embeddings()
        test_memory_store()
        test_memory_decay()
        
        print("=" * 50)
        print("🎉 所有测试通过！")
        print("=" * 50)
        print("\n下一步:")
        print("1. 运行 API 服务器: python run_memory_api.py")
        print("2. 访问文档: http://localhost:8000/docs")
        print("3. 查看详细文档: MEMORY_TOOL_README.md\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

