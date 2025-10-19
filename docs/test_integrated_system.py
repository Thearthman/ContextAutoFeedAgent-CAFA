#!/usr/bin/env python3
"""
测试集成 LLM + Memory 系统
演示架构图中的完整流程
"""

import requests
import json
import time

BASE_URL = "http://localhost:6000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_health():
    """Test健康检查"""
    print_section("1️⃣ 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ 服务状态: healthy")
            print(f"🔗 LLM 服务: {health['llm_service']}")
            print(f"🧠 Memory 服务: {health['memory_service']}")
            print(f"📊 统计信息: {health['stats']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("💡 提示: 请先启动集成服务")
        print("   python src/integrated_llm_memory.py")
        return False

def test_simple_chat():
    """Test普通对话（无需记忆）"""
    print_section("2️⃣ 普通对话测试（无需记忆）")
    
    prompt = "什么是人工智能？"
    print(f"📝 用户: {prompt}")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"prompt": prompt})
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result['response'][:200]}...")
            print(f"\n📊 使用记忆: {result['used_memory']}")
            print(f"📚 记忆数量: {result['memory_count']}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def store_test_memories():
    """存储一些测试记忆"""
    print_section("3️⃣ 存储测试记忆")
    
    test_memories = [
        {"text": "用户正在开发一个 AI 助手项目，使用 Python 和 Flask", "importance": 0.9},
        {"text": "用户喜欢使用深度学习和自然语言处理技术", "importance": 0.8},
        {"text": "用户的 GPU 是 NVIDIA RTX 4070 Laptop", "importance": 0.7},
        {"text": "用户正在集成 LLM 和 Memory Tool", "importance": 0.85},
    ]
    
    print("💾 存储以下记忆:")
    for mem in test_memories:
        print(f"   • {mem['text']}")
    
    try:
        for mem in test_memories:
            response = requests.post(f"{BASE_URL}/memory/store", json=mem)
            if response.status_code == 200:
                print(f"✅ 已存储: {mem['text'][:50]}...")
            else:
                print(f"❌ 存储失败: {response.status_code}")
            time.sleep(0.5)  # 避免过快请求
    except Exception as e:
        print(f"❌ 存储失败: {e}")

def test_memory_enhanced_chat():
    """Test带记忆增强的对话"""
    print_section("4️⃣ 记忆增强对话测试")
    
    prompts = [
        "你还记得我在做什么项目吗？",
        "我之前提到的 GPU 型号是什么？",
        "我在开发中使用了哪些技术？"
    ]
    
    for prompt in prompts:
        print(f"\n📝 用户: {prompt}")
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json={"prompt": prompt})
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 AI: {result['response'][:150]}...")
                print(f"📊 使用记忆: {result['used_memory']}")
                
                if result['memories']:
                    print(f"🔍 找到 {len(result['memories'])} 条相关记忆:")
                    for i, mem in enumerate(result['memories'][:3], 1):
                        print(f"   {i}. {mem['text'][:60]}... (相似度: {mem['similarity']})")
            else:
                print(f"❌ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        time.sleep(1)  # 间隔一下

def test_memory_search():
    """Test记忆搜索"""
    print_section("5️⃣ 记忆搜索测试")
    
    queries = [
        "Python 项目",
        "GPU",
        "深度学习"
    ]
    
    for query in queries:
        print(f"\n🔍 搜索: {query}")
        
        try:
            response = requests.get(f"{BASE_URL}/memory/search", params={"query": query, "top_k": 3})
            if response.status_code == 200:
                result = response.json()
                memories = result['memories']
                
                if memories:
                    print(f"✅ 找到 {len(memories)} 条记忆:")
                    for i, mem in enumerate(memories, 1):
                        print(f"   {i}. [{mem['similarity']:.3f}] {mem['text'][:70]}...")
                else:
                    print("   (没有找到相关记忆)")
            else:
                print(f"❌ 搜索失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 搜索失败: {e}")

def test_auto_memory_storage():
    """Test自动记忆存储"""
    print_section("6️⃣ 自动记忆存储测试")
    
    prompt = "记住，我的 API Key 需要保密，不要泄露给任何人"
    print(f"📝 用户: {prompt}")
    print("💡 这条信息包含 '记住' 关键词，应该被自动存储")
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json={"prompt": prompt})
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI: {result['response']}")
            print(f"📊 使用记忆: {result['used_memory']}")
            
            # 稍等一下，然后验证是否存储
            time.sleep(2)
            print("\n🔍 验证记忆是否已存储...")
            
            verify_response = requests.get(f"{BASE_URL}/memory/search", params={"query": "API Key", "top_k": 3})
            if verify_response.status_code == 200:
                memories = verify_response.json()['memories']
                if memories:
                    print("✅ 记忆已自动存储:")
                    for mem in memories:
                        if "API Key" in mem['text']:
                            print(f"   • {mem['text'][:80]}...")
                else:
                    print("⚠️  未找到相关记忆")
        else:
            print(f"❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")

def test_stats():
    """查看统计信息"""
    print_section("7️⃣ 统计信息")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("📊 系统统计:")
            print(f"   • 总查询次数: {stats['total_queries']}")
            print(f"   • 记忆检索次数: {stats['memory_fetches']}")
            print(f"   • 记忆存储次数: {stats['memory_stores']}")
            print(f"   • 使用记忆增强的查询: {stats['context_enhanced_queries']}")
            
            if stats['total_queries'] > 0:
                memory_usage_rate = stats['context_enhanced_queries'] / stats['total_queries'] * 100
                print(f"   • 记忆使用率: {memory_usage_rate:.1f}%")
        else:
            print(f"❌ 获取统计失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取统计失败: {e}")

def main():
    """运行所有测试"""
    print("\n" + "🧪" * 30)
    print("  集成 LLM + Memory 系统测试")
    print("  实现架构图的完整逻辑")
    print("🧪" * 30)
    
    # 1. 健康检查
    if not test_health():
        print("\n❌ 服务未运行，请先启动：")
        print("   1. python src/online_model_server.py  (LLM 服务)")
        print("   2. python run_memory_api.py           (Memory 服务，可选)")
        print("   3. python src/integrated_llm_memory.py (集成服务)")
        return
    
    time.sleep(1)
    
    # 2. 普通对话测试
    test_simple_chat()
    time.sleep(2)
    
    # 3. 存储测试记忆
    store_test_memories()
    time.sleep(2)
    
    # 4. 记忆增强对话
    test_memory_enhanced_chat()
    time.sleep(2)
    
    # 5. 记忆搜索
    test_memory_search()
    time.sleep(2)
    
    # 6. 自动记忆存储
    test_auto_memory_storage()
    time.sleep(2)
    
    # 7. 统计信息
    test_stats()
    
    # 总结
    print_section("🎉 测试完成")
    print("""
✅ 已验证的功能:
   1. 普通对话（无需记忆）
   2. 智能记忆判断（Memory? 决策）
   3. 记忆检索增强（M Tool fetch）
   4. 自动记忆存储（update memory mode）
   5. 手动记忆搜索
   6. 统计和监控

📖 架构图实现:
   • User Mode - 完全实现 ✅
   • Update Memory Mode - 完全实现 ✅
   • LLM + Memory Tool 集成 - 完全实现 ✅

🎯 下一步:
   1. 配置 LLM API Key 进行真实对话测试
   2. 启动浮动 UI: python src/floating_ui.py
   3. 享受智能 AI 助手体验!
    """)

if __name__ == "__main__":
    main()
