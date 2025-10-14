#!/usr/bin/env python3
"""
Integrated LLM + Memory Tool
Implements complete logic from architecture diagram:
1. User Mode: Intelligently determine if memory retrieval is needed
2. Update Memory Mode: Automatically store important content in memory
"""

import sys
import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from threading import Lock
from flask import Flask, request, jsonify, Response

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.memory_tool.memory_store import MemoryStore
from src.memory_tool.embeddings import EmbeddingGenerator

app = Flask(__name__)

# Configuration
config = {
    "llm_service_url": "http://localhost:5000",
    "memory_service_url": "http://localhost:8000",
    "auto_store_memory": True,
    "memory_threshold": 0.7,  # Similarity threshold for determining if memory is needed
    "use_local_memory": True,  # Use local Memory or API
}

# Local Memory Store (if using local mode)
local_memory = None
embedding_model = None
model_lock = Lock()

# Statistics
stats = {
    "total_queries": 0,
    "memory_fetches": 0,
    "memory_stores": 0,
    "context_enhanced_queries": 0
}

def initialize():
    """Initialize service"""
    global local_memory, embedding_model
    
    print("=" * 70)
    print("🧠 Initializing integrated LLM + Memory service...")
    print("=" * 70)
    
    if config["use_local_memory"]:
        print("📦 Using local Memory Store")
        local_memory = MemoryStore()
        embedding_model = EmbeddingGenerator()
    else:
        print("🌐 Using remote Memory API")
    
    print(f"🔗 LLM service: {config['llm_service_url']}")
    print(f"🧠 Memory service: {config['memory_service_url']}")
    print(f"💾 Auto store memory: {config['auto_store_memory']}")
    print("=" * 70)

class IntegratedLLMMemory:
    """Intelligent agent integrating LLM and Memory Tool"""
    
    def __init__(self):
        self.llm_url = config["llm_service_url"]
        self.memory_url = config["memory_service_url"]
        self.use_local = config["use_local_memory"]
    
    def should_fetch_memory(self, user_input: str) -> bool:
        """
        Determine if memory retrieval is needed
        This is the "Memory?" decision point in the architecture diagram
        """
        # Keyword judgment (simple implementation)
        memory_keywords = [
            "remember", "before", "last time", "mentioned", "said", "told",
            "recall", "history", "previously", "once", "earlier"
        ]
        
        # If user input contains memory-related keywords
        for keyword in memory_keywords:
            if keyword in user_input.lower():
                return True
        
        # TODO: Can use LLM for smarter judgment
        # For example: Send a small prompt to ask LLM if context is needed
        
        return False
    
    def fetch_memory(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Fetch relevant memories from Memory Tool
        This is the "M Tool fetch" part in the architecture diagram
        """
        if self.use_local:
            # Use local Memory
            results = local_memory.search(query, top_k=top_k)
        else:
            # Use Memory API
            try:
                response = requests.get(
                    f"{self.memory_url}/recall",
                    params={"query": query, "top_k": top_k},
                    timeout=5
                )
                if response.status_code == 200:
                    results = response.json()["matches"]
                else:
                    results = []
            except Exception as e:
                print(f"⚠️  Memory API call failed: {e}")
                results = []
        
        stats["memory_fetches"] += 1
        return results
    
    def build_context_with_memory(self, user_input: str, memories: List[Dict]) -> str:
        """
        Build context with memories
        """
        if not memories:
            return user_input
        
        context = "Relevant memories:\n"
        for i, mem in enumerate(memories, 1):
            context += f"{i}. {mem['text']} (similarity: {mem['similarity']})\n"
        
        context += f"\nCurrent question: {user_input}"
        return context
    
    def call_llm(self, prompt: str, stream: bool = False) -> str:
        """Call LLM service to generate response"""
        try:
            endpoint = "/generate_stream" if stream else "/generate"
            response = requests.post(
                f"{self.llm_url}{endpoint}",
                json={"prompt": prompt, "max_new_tokens": 1000},
                timeout=30 if not stream else None,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return response  # Return streaming response object
                else:
                    return response.json()["response"]
            else:
                return f"LLM service error: {response.status_code}"
        except Exception as e:
            return f"LLM call failed: {e}"
    
    def store_to_memory(self, text: str, importance: float = 0.8):
        """
        将内容存储到记忆中
        这是架构图中的 "memory tool indexing" 部分
        """
        if not config["auto_store_memory"]:
            return
        
        if self.use_local:
            # 使用本地 Memory
            local_memory.add_memory(text, importance=importance)
        else:
            # 使用 Memory API
            try:
                requests.post(
                    f"{self.memory_url}/store",
                    params={"text": text, "importance": importance},
                    timeout=5
                )
            except Exception as e:
                print(f"⚠️  Memory 存储失败: {e}")
        
        stats["memory_stores"] += 1
    
    def should_store_as_memory(self, text: str, response: str) -> bool:
        """
        判断对话是否值得存储为记忆
        """
        # 简单规则：
        # 1. 用户输入或回答包含重要信息
        # 2. 回答长度超过一定阈值
        # 3. 包含事实性信息
        
        important_patterns = [
            "我", "我的", "我喜欢", "我不喜欢", "我需要",
            "记住", "记得", "重要", "注意"
        ]
        
        for pattern in important_patterns:
            if pattern in text:
                return True
        
        # 如果回答很长，可能包含重要信息
        if len(response) > 100:
            return True
        
        return False
    
    def process_query(self, user_input: str, stream: bool = False):
        """
        处理用户查询的完整流程
        实现架构图中的 User Mode 逻辑
        """
        stats["total_queries"] += 1
        
        # 1. 判断是否需要记忆（架构图：Memory? 决策）
        need_memory = self.should_fetch_memory(user_input)
        
        memories = []
        if need_memory:
            # 2. 获取相关记忆（架构图：M Tool fetch）
            print(f"🔍 检索相关记忆...")
            memories = self.fetch_memory(user_input, top_k=3)
            
            if memories:
                print(f"✅ 找到 {len(memories)} 条相关记忆")
                stats["context_enhanced_queries"] += 1
        
        # 3. 构建上下文
        if memories:
            enhanced_prompt = self.build_context_with_memory(user_input, memories)
        else:
            enhanced_prompt = user_input
        
        # 4. 调用 LLM 生成响应
        print(f"🤖 调用 LLM 生成响应...")
        response = self.call_llm(enhanced_prompt, stream=stream)
        
        # 5. 判断是否存储为记忆（架构图：update memory mode）
        if not stream and self.should_store_as_memory(user_input, response):
            print(f"💾 存储到记忆...")
            # 存储用户输入
            self.store_to_memory(f"用户问题: {user_input}", importance=0.7)
            # 存储重要的回答片段（可以做摘要）
            if len(response) > 50:
                summary = response[:200] + "..." if len(response) > 200 else response
                self.store_to_memory(f"AI回答: {summary}", importance=0.6)
        
        return {
            "response": response,
            "used_memory": bool(memories),
            "memory_count": len(memories),
            "memories": memories if memories else None
        }

# Global agent
agent = None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "llm_service": config["llm_service_url"],
        "memory_service": config["memory_service_url"],
        "stats": stats
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    统一的聊天接口
    自动处理记忆检索和存储
    """
    try:
        data = request.json
        user_input = data.get('prompt') or data.get('message')
        
        if not user_input:
            return jsonify({"error": "缺少 prompt 或 message"}), 400
        
        print(f"\n📨 收到用户输入: {user_input[:50]}...")
        
        with model_lock:
            result = agent.process_query(user_input, stream=False)
        
        return jsonify({
            "response": result["response"],
            "used_memory": result["used_memory"],
            "memory_count": result["memory_count"],
            "memories": result["memories"],
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat_stream', methods=['POST'])
def chat_stream():
    """
    流式聊天接口
    """
    try:
        data = request.json
        user_input = data.get('prompt') or data.get('message')
        
        if not user_input:
            return jsonify({"error": "缺少 prompt 或 message"}), 400
        
        def generate_sse():
            try:
                # 先获取记忆
                need_memory = agent.should_fetch_memory(user_input)
                memories = []
                
                if need_memory:
                    memories = agent.fetch_memory(user_input, top_k=3)
                    # 发送记忆信息
                    yield f"data: {json.dumps({'type': 'memory', 'memories': memories})}\n\n"
                
                # 构建上下文
                if memories:
                    enhanced_prompt = agent.build_context_with_memory(user_input, memories)
                else:
                    enhanced_prompt = user_input
                
                # 调用 LLM 流式生成
                llm_response = agent.call_llm(enhanced_prompt, stream=True)
                
                full_response = ""
                for line in llm_response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_str = line_text[6:]
                            try:
                                token_data = json.loads(data_str)
                                if not token_data.get('done', False):
                                    token = token_data.get('token', '')
                                    full_response += token
                                    yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
                            except:
                                pass
                
                # 存储记忆
                if agent.should_store_as_memory(user_input, full_response):
                    agent.store_to_memory(f"用户问题: {user_input}", importance=0.7)
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done', 'used_memory': bool(memories)})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return Response(generate_sse(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/memory/search', methods=['GET'])
def search_memory():
    """手动搜索记忆"""
    query = request.args.get('query')
    top_k = int(request.args.get('top_k', 5))
    
    if not query:
        return jsonify({"error": "缺少 query 参数"}), 400
    
    memories = agent.fetch_memory(query, top_k=top_k)
    return jsonify({"memories": memories})

@app.route('/memory/store', methods=['POST'])
def store_memory():
    """手动存储记忆"""
    data = request.json
    text = data.get('text')
    importance = data.get('importance', 0.8)
    
    if not text:
        return jsonify({"error": "缺少 text 参数"}), 400
    
    agent.store_to_memory(text, importance=importance)
    return jsonify({"message": "记忆已存储"})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics"""
    return jsonify(stats)

@app.route('/config', methods=['GET'])
def get_config():
    """Get配置"""
    return jsonify(config)

@app.route('/config', methods=['POST'])
def update_config():
    """Update配置"""
    data = request.json
    for key in ['llm_service_url', 'memory_service_url', 'auto_store_memory', 'memory_threshold']:
        if key in data:
            config[key] = data[key]
    return jsonify({"message": "配置已更新", "config": config})

if __name__ == "__main__":
    # Initialize
    initialize()
    
    # Create集成代理
    agent = IntegratedLLMMemory()
    
    print("\n✅ 集成服务启动成功！")
    print("📍 API 端点:")
    print("   - POST /chat - 智能聊天（自动记忆）")
    print("   - POST /chat_stream - 流式聊天")
    print("   - GET  /memory/search - 搜索记忆")
    print("   - POST /memory/store - 存储记忆")
    print("   - GET  /stats - 统计信息")
    print("\n🌐 服务运行在 http://localhost:6000")
    print("=" * 70)
    
    # 启动服务器（使用不同的端口）
    app.run(host='0.0.0.0', port=6000, debug=False, threaded=True)
