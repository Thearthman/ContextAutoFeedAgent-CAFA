#!/usr/bin/env python3
"""
Qwen3-VL Agent Server with Tool Support
Loads Qwen model with qwen-agent framework for autonomous tool usage.

Tools available:
- google_search: Search the web
- read_webpage: Extract content from URLs
- read_local_file: Read local .md and .txt files

Usage:
    python src/qwen_agent_server.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, Response
import json
import time
from threading import Lock
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

# Import our cus127.0.0.1
from src.tools.web_search import google_search, TOOL_DEFINITION as SEARCH_TOOL
from src.tools.web_reader import read_webpage, TOOL_DEFINITION as READER_TOOL
from src.tools.file_reader import read_local_file, TOOL_DEFINITION as FILE_TOOL

app = Flask(__name__)

# Global agent instance
agent = None
agent_lock = Lock()

# Model configuration
# Using Qwen3-VL-30B-A3B-Thinking-FP8 for production AND testing
# 
# Key features:
# - Vision-Language support (VL) for image input capability
# - Thinking mode: Chain-of-thought reasoning with <think>...</think> blocks
# - MoE architecture: 30B total params, only 3.3B active during inference (efficient!)
# - FP8 quantization: Native low precision for speed
#
# Why this model:
# - Excellent reasoning for autonomous tool orchestration
# - Efficient despite 30B size (MoE activates only 3.3B)
# - Structured thinking output for transparency
# - Vision-ready for future image-based tasks
#
# Note: Using same model for dev/prod ensures no refactoring needed when scaling
MODEL_NAME = "Qwen/Qwen3-VL-30B-A3B-Thinking-FP8"


class WebSearchTool(BaseTool):
    """Qwen-agent wrapper for Google search."""
    name = "google_search"
    description = SEARCH_TOOL["description"]
    parameters = SEARCH_TOOL["parameters"]
    
    def call(self, params: dict, **kwargs) -> str:
        query = params.get("query", "")
        num_results = params.get("num_results", 10)
        return google_search(query, num_results)


class WebReaderTool(BaseTool):
    """Qwen-agent wrapper for webpage reading."""
    name = "read_webpage"
    description = READER_TOOL["description"]
    parameters = READER_TOOL["parameters"]
    
    def call(self, params: dict, **kwargs) -> str:
        url = params.get("url", "")
        max_length = params.get("max_length", 5000)
        return read_webpage(url, max_length)


class FileReaderTool(BaseTool):
    """Qwen-agent wrapper for local file reading."""
    name = "read_local_file"
    description = FILE_TOOL["description"]
    parameters = FILE_TOOL["parameters"]
    
    def call(self, params: dict, **kwargs) -> str:
        file_path = params.get("file_path", "")
        max_length = params.get("max_length", 10000)
        return read_local_file(file_path, max_length)


def initialize_agent():
    """Initialize Qwen agent with tools at startup."""
    global agent
    
    print("=" * 70)
    print("🚀 Starting Qwen3-VL Agent Server...")
    print("=" * 70)
    print(f"Loading model: {MODEL_NAME}")
    print("Model features: Vision-Language + Thinking (CoT reasoning)")
    print("Quantization: FP8 (native) or 4-bit fallback")
    start_time = time.time()
    
    try:
        # FP8 models are pre-quantized, but may need additional config
        # For Qwen3-VL-30B-A3B-Thinking-FP8:
        # - FP8 is baked into the model name
        # - May still benefit from BitsAndBytes for further optimization
        # - Check if model loads with native FP8 first, fallback to 4-bit if needed
        
        # Try loading with minimal quantization first (FP8 should be native)
        quantization_config = None  # Let FP8 model use native quantization
        
        # If OOM, uncomment this fallback:
        # quantization_config = BitsAndBytesConfig(
        #     load_in_4bit=True,
        #     bnb_4bit_compute_dtype=torch.bfloat16,
        #     bnb_4bit_quant_type="nf4",
        #     bnb_4bit_use_double_quant=True
        # )
        
        # Initialize agent with tools
        # Using qwen-agent's Assistant class which handles tool calling
        # Note: Qwen3-VL with Thinking mode will output <think>...</think> blocks
        llm_cfg = {
            'model': MODEL_NAME,
            'model_server': 'local',  # Use local model, not API
            'generate_cfg': {
                'max_new_tokens': 2000,
                'temperature': 0.7,
                'top_p': 0.9,
                'do_sample': True,  # Enable sampling for thinking mode
            }
        }
        
        # Register tools
        tools = [
            WebSearchTool(),
            WebReaderTool(),
            FileReaderTool()
        ]
        
        # Create agent
        agent = Assistant(
            llm=llm_cfg,
            name='QwenAgent',
            description='A helpful AI assistant with web search and file reading capabilities',
            function_list=tools
        )
        
        load_time = time.time() - start_time
        print(f"\n✅ Qwen Agent loaded successfully in {load_time:.1f} seconds")
        print(f"🔧 Tools registered: {len(tools)}")
        for tool in tools:
            print(f"   - {tool.name}")
        print(f"🌐 Server ready on http://localhost:5001")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    if agent is None:
        return jsonify({"status": "initializing"}), 503
    return jsonify({
        "status": "healthy",
        "model": MODEL_NAME,
        "tools": ["google_search", "read_webpage", "read_local_file"]
    })


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate a response with autonomous tool usage.
    
    Request JSON:
    {
        "prompt": "Your question here",
        "use_tools": true,  // Enable tool usage (default: true)
        "max_iterations": 5  // Max tool calls (default: 5)
    }
    """
    if agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
        
        use_tools = data.get('use_tools', True)
        max_iterations = data.get('max_iterations', 5)
        
        print(f"\n📨 Received request: {prompt[:50]}...")
        print(f"   Tools enabled: {use_tools}")
        
        # Thread-safe agent call
        with agent_lock:
            # Agent.run() handles the entire reasoning loop automatically
            messages = [{'role': 'user', 'content': prompt}]
            
            # Collect all response chunks
            full_response = ""
            tool_calls = []
            
            for response in agent.run(messages=messages):
                # Response format from qwen-agent
                if isinstance(response, dict):
                    if 'content' in response:
                        full_response += response['content']
                    if 'function_call' in response:
                        tool_calls.append(response['function_call'])
                elif isinstance(response, str):
                    full_response += response
        
        return jsonify({
            "response": full_response,
            "prompt": prompt,
            "tool_calls": tool_calls,
            "timestamp": time.time()
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/generate_stream', methods=['POST'])
def generate_stream():
    """
    Generate a streaming response with tool usage visible in real-time.
    
    SSE format:
    - Agent reasoning: {"type": "thinking", "content": "..."}
    - Tool calls: {"type": "tool_call", "tool": "...", "params": {...}}
    - Tool results: {"type": "tool_result", "result": "..."}
    - Final response: {"type": "response", "token": "...", "done": false}
    - Completion: {"type": "response", "token": "", "done": true}
    """
    if agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
        
        def generate_sse():
            """Generate Server-Sent Events with agent steps."""
            try:
                print(f"\n📨 Streaming request: {prompt[:50]}...")
                
                with agent_lock:
                    messages = [{'role': 'user', 'content': prompt}]
                    
                    # Stream agent responses
                    for response in agent.run(messages=messages):
                        if isinstance(response, dict):
                            # Handle different response types
                            if 'function_call' in response:
                                # Tool being called
                                func_call = response['function_call']
                                event = {
                                    'type': 'tool_call',
                                    'tool': func_call.get('name', 'unknown'),
                                    'params': func_call.get('arguments', {})
                                }
                                yield f"data: {json.dumps(event)}\n\n"
                            
                            elif 'observation' in response:
                                # Tool result
                                event = {
                                    'type': 'tool_result',
                                    'result': response['observation']
                                }
                                yield f"data: {json.dumps(event)}\n\n"
                            
                            elif 'content' in response:
                                # Agent thinking or final response
                                content = response['content']
                                
                                # Stream content token by token if possible
                                if content:
                                    for char in content:
                                        event = {
                                            'type': 'response',
                                            'token': char,
                                            'done': False
                                        }
                                        yield f"data: {json.dumps(event)}\n\n"
                        
                        elif isinstance(response, str):
                            # Direct string response - stream it
                            for char in response:
                                event = {
                                    'type': 'response',
                                    'token': char,
                                    'done': False
                                }
                                yield f"data: {json.dumps(event)}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'response', 'token': '', 'done': True})}\n\n"
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return Response(generate_sse(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear the conversation history."""
    if agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    
    with agent_lock:
        # Reset agent's memory
        agent.mem.clear()
    
    return jsonify({"message": "Conversation history cleared"})


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get agent statistics."""
    if agent is None:
        return jsonify({"error": "Agent not initialized"}), 503
    
    return jsonify({
        "model": MODEL_NAME,
        "tools": ["google_search", "read_webpage", "read_local_file"],
        "status": "ready"
    })


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server."""
    print("\n🛑 Shutting down agent server...")
    
    # Clean up GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Not running with the Werkzeug Server"}), 500
    
    func()
    return jsonify({"message": "Agent server shutting down..."})


if __name__ == "__main__":
    # Initialize agent before starting server
    initialize_agent()
    
    # Start Flask server on different port to avoid conflict with existing server
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)

