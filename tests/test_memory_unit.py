#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Tool 单元测试套件
标准的程序员测试方式 - 验证每个功能是否正常工作
"""

import sys
import os
import unittest
import json
import tempfile
from datetime import datetime, timedelta

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memory_tool.memory_store import MemoryStore
from memory_tool.embeddings import EmbeddingGenerator


class TestEmbeddingGenerator(unittest.TestCase):
    """测试向量化生成器"""
    
    def setUp(self):
        """测试前准备"""
        self.generator = EmbeddingGenerator()
    
    def test_embed_returns_vector(self):
        """测试：embed() 应该返回向量"""
        text = "这是一个测试文本"
        embedding = self.generator.embed(text)
        
        # 验证返回的是向量
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding.shape), 1)  # 应该是一维向量
        self.assertGreater(len(embedding), 0)  # 向量长度应该 > 0
    
    def test_embed_consistency(self):
        """测试：相同输入应该产生相同向量"""
        text = "测试一致性"
        embedding1 = self.generator.embed(text)
        embedding2 = self.generator.embed(text)
        
        # 相同输入应该产生相同结果
        import numpy as np
        self.assertTrue(np.allclose(embedding1, embedding2))
    
    def test_similarity_calculation(self):
        """测试：相似度计算是否合理"""
        text1 = "我喜欢编程"
        text2 = "我热爱写代码"
        text3 = "今天天气很好"
        
        # 相似内容的相似度应该高于不相关内容
        sim_similar = self.generator.similarity(text1, text2)
        sim_different = self.generator.similarity(text1, text3)
        
        self.assertGreater(sim_similar, sim_different)
        
        # 相似度应该在 -1 到 1 之间
        self.assertGreaterEqual(sim_similar, -1)
        self.assertLessEqual(sim_similar, 1)
    
    def test_similarity_with_self(self):
        """测试：文本与自己的相似度应该接近 1"""
        text = "测试文本"
        similarity = self.generator.similarity(text, text)
        
        # 自己和自己的相似度应该非常高（接近1）
        self.assertGreater(similarity, 0.99)


class TestMemoryStore(unittest.TestCase):
    """测试记忆存储系统"""
    
    def setUp(self):
        """测试前准备 - 使用临时文件"""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        # 初始化为空JSON数组
        self.temp_file.write('[]')
        self.temp_file.close()
        self.store = MemoryStore(path=self.temp_file.name)
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_memory(self):
        """测试：添加记忆功能"""
        text = "这是一条测试记忆"
        importance = 0.8
        
        memory = self.store.add_memory(text, importance=importance)
        
        # 验证记忆被正确添加
        self.assertEqual(memory['text'], text)
        self.assertEqual(memory['importance'], importance)
        self.assertIn('embedding', memory)
        self.assertIn('timestamp', memory)
        
        # 验证记忆被保存到存储
        self.assertEqual(len(self.store.memories), 1)
    
    def test_add_multiple_memories(self):
        """测试：添加多条记忆"""
        memories_count = 5
        
        for i in range(memories_count):
            self.store.add_memory(f"记忆 {i}", importance=0.7)
        
        # 验证所有记忆都被添加
        self.assertEqual(len(self.store.memories), memories_count)
    
    def test_search_returns_results(self):
        """测试：搜索应该返回结果"""
        # 添加一些记忆
        self.store.add_memory("Python 是一门编程语言", importance=0.9)
        self.store.add_memory("Java 也是编程语言", importance=0.8)
        self.store.add_memory("今天天气很好", importance=0.7)
        
        # 搜索相关内容
        results = self.store.search("编程语言", top_k=2)
        
        # 验证返回结果
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)  # 不应超过 top_k
        
        # 验证结果格式
        for result in results:
            self.assertIn('text', result)
            self.assertIn('similarity', result)
    
    def test_search_returns_most_relevant(self):
        """测试：搜索应该返回最相关的结果"""
        # 添加记忆
        self.store.add_memory("Python 编程教程", importance=0.9)
        self.store.add_memory("Python 是很好的语言", importance=0.8)
        self.store.add_memory("天气预报", importance=0.7)
        
        # 搜索
        results = self.store.search("Python", top_k=3)
        
        # 验证最相关的结果排在前面
        self.assertGreater(results[0]['similarity'], results[-1]['similarity'])
        
        # Python 相关的结果应该排在前面
        self.assertIn('Python', results[0]['text'])
    
    def test_search_empty_store(self):
        """测试：空记忆库搜索应该返回空列表"""
        results = self.store.search("任何查询", top_k=5)
        
        self.assertEqual(results, [])
    
    def test_decay_reduces_importance(self):
        """测试：时间衰减应该降低重要性"""
        # 添加记忆
        memory = self.store.add_memory("测试记忆", importance=1.0)
        original_importance = memory['importance']
        
        # 修改时间戳为过去
        past_time = datetime.now() - timedelta(days=7)
        self.store.memories[0]['timestamp'] = past_time.isoformat()
        
        # 执行衰减
        self.store.decay(half_life_days=7.0)
        
        # 验证重要性降低
        new_importance = self.store.memories[0]['importance']
        self.assertLess(new_importance, original_importance)
    
    def test_decay_does_not_exceed_bounds(self):
        """测试：衰减后重要性不应该超出 0-1 范围"""
        self.store.add_memory("测试", importance=0.5)
        
        # 多次衰减
        for _ in range(10):
            self.store.decay(half_life_days=1.0)
        
        # 验证仍在合理范围
        importance = self.store.memories[0]['importance']
        self.assertGreaterEqual(importance, 0)
        self.assertLessEqual(importance, 1)
    
    def test_persistence(self):
        """测试：记忆应该被持久化保存"""
        text = "持久化测试"
        self.store.add_memory(text, importance=0.8)
        
        # 创建新的 store 实例，加载相同文件
        new_store = MemoryStore(path=self.temp_file.name)
        
        # 验证记忆被加载
        self.assertEqual(len(new_store.memories), 1)
        self.assertEqual(new_store.memories[0]['text'], text)
    
    def test_importance_bounds(self):
        """测试：重要性应该在 0-1 之间"""
        memory = self.store.add_memory("测试", importance=0.5)
        
        self.assertGreaterEqual(memory['importance'], 0)
        self.assertLessEqual(memory['importance'], 1)


class TestMemoryStoreEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.write('[]')
        self.temp_file.close()
        self.store = MemoryStore(path=self.temp_file.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_empty_text(self):
        """测试：空文本处理"""
        # 空文本会抛出异常（这是预期行为）
        with self.assertRaises(ValueError):
            self.store.add_memory("", importance=0.5)
    
    def test_very_long_text(self):
        """测试：非常长的文本"""
        long_text = "测试" * 10000  # 很长的文本
        memory = self.store.add_memory(long_text, importance=0.5)
        
        self.assertEqual(memory['text'], long_text)
    
    def test_special_characters(self):
        """测试：特殊字符处理"""
        special_text = "测试 @#$%^&*() 😊 🚀 \n\t"
        memory = self.store.add_memory(special_text, importance=0.5)
        
        self.assertEqual(memory['text'], special_text)
    
    def test_search_with_top_k_larger_than_memories(self):
        """测试：top_k 大于记忆数"""
        self.store.add_memory("测试1", importance=0.5)
        self.store.add_memory("测试2", importance=0.5)
        
        # 请求的结果数大于实际记忆数
        results = self.store.search("测试", top_k=100)
        
        # 应该返回所有记忆
        self.assertEqual(len(results), 2)
    
    def test_concurrent_operations(self):
        """测试：连续操作"""
        # 快速连续添加和搜索
        for i in range(10):
            self.store.add_memory(f"记忆 {i}", importance=0.5)
            results = self.store.search(f"记忆 {i}", top_k=1)
            self.assertGreater(len(results), 0)


class TestMemoryStorePerformance(unittest.TestCase):
    """测试性能"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.json'
        )
        self.temp_file.write('[]')
        self.temp_file.close()
        self.store = MemoryStore(path=self.temp_file.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_search_performance(self):
        """测试：搜索性能应该可接受"""
        # 添加一些记忆
        for i in range(50):
            self.store.add_memory(f"测试记忆 {i}", importance=0.5)
        
        # 测试搜索时间
        import time
        start = time.time()
        results = self.store.search("测试", top_k=10)
        duration = time.time() - start
        
        # 搜索应该在合理时间内完成（比如 5 秒）
        self.assertLess(duration, 5.0)
        self.assertGreater(len(results), 0)


def run_tests(verbosity=2):
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestEmbeddingGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryStore))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryStoreEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMemoryStorePerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 返回测试结果
    return result


def main():
    """主函数"""
    # 设置输出编码
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=" * 70)
    print("Memory Tool 单元测试套件")
    print("=" * 70)
    print("\n测试内容:")
    print("  1. 向量化功能测试")
    print("  2. 记忆存储功能测试")
    print("  3. 搜索功能测试")
    print("  4. 时间衰减测试")
    print("  5. 持久化测试")
    print("  6. 边界情况测试")
    print("  7. 性能测试")
    print("\n开始测试...\n")
    
    # 运行测试
    result = run_tests(verbosity=2)
    
    # 显示总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！Memory Tool 工作正常。")
        return 0
    else:
        print("\n❌ 有测试失败，需要修复。")
        
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())

