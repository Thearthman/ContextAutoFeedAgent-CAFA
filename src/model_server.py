#!/usr/bin/env python3
"""
Persistent Model Server for Gemma-3-27B Q4
Loads model once and keeps it in GPU memory, serves requests via HTTP API.

Usage:
    python src/model_server.py

The server will load the model once and keep it running.
Use client.py to send requests without reloading the model.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, Response
from src.main import GemmaStreamingChat
import json
import time
from threading import Lock

app = Flask(__name__)

# Global model instance (loaded once, persists in GPU)
model = None
model_lock = Lock()  # Thread safety for concurrent requests

def initialize_model():
    """Initialize the model once at startup."""
    global model
    print("=" * 70)
    print("🚀 Starting Gemma Model Server...")
    print("=" * 70)
    start_time = time.time()
    
    model = GemmaStreamingChat()
    
    load_time = time.time() - start_time
    print(f"\n✅ Model loaded successfully in {load_time:.1f} seconds")
    print(f"🌐 Server ready to accept requests on http://localhost:5000")
    print("=" * 70)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    if model is None:
        return jsonify({"status": "initializing"}), 503
    return jsonify({
        "status": "healthy",
        "model_id": model.model_id,
        "total_conversations": model.conversation_count + 1,
        "total_tokens_generated": model.total_tokens_generated
    })

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate a response to user input.
    
    Request JSON:
    {
        "prompt": "Your question here",
        "max_new_tokens": 1000,  // optional
        "temperature": 0.7,       // optional
        "top_p": 0.9,            // optional
        "top_k": 40              // optional
    }
    """
    if model is None:
        return jsonify({"error": "Model not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
        
        # Optional parameters
        max_new_tokens = data.get('max_new_tokens', 1000)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        top_k = data.get('top_k', 40)
        
        print(f"\n📨 Received request: {prompt[:50]}...")
        
        # Thread-safe generation
        with model_lock:
            response = model.generate_response(
                user_input=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
        
        return jsonify({
            "response": response,
            "prompt": prompt,
            "timestamp": time.time()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_stream', methods=['POST'])
def generate_stream():
    """
    Generate a streaming response (Server-Sent Events).
    
    Request JSON: Same as /generate
    """
    if model is None:
        return jsonify({"error": "Model not initialized"}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Missing 'prompt' in request"}), 400
        
        def generate_sse():
            """Generate Server-Sent Events with real token streaming."""
            try:
                print(f"\n📨 Streaming request: {prompt[:50]}...")
                
                # Use the new streaming method that yields tokens
                with model_lock:
                    for token in model.generate_response_stream(
                        user_input=prompt,
                        max_new_tokens=data.get('max_new_tokens', 1000),
                        temperature=data.get('temperature', 0.7),
                        top_p=data.get('top_p', 0.9),
                        top_k=data.get('top_k', 40)
                    ):
                        # Send each token immediately as it's generated
                        yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate_sse(), mimetype='text/event-stream')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear the conversation history."""
    if model is None:
        return jsonify({"error": "Model not initialized"}), 503
    
    with model_lock:
        model.clear_conversation_history()
    
    return jsonify({"message": "Conversation history cleared"})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics."""
    if model is None:
        return jsonify({"error": "Model not initialized"}), 503
    
    stats = model.get_conversation_stats()
    return jsonify(stats)

@app.route('/update_system_prompt', methods=['POST'])
def update_system_prompt():
    """
    Update the system prompt.
    
    Request JSON:
    {
        "system_prompt": "New system prompt here"
    }
    """
    if model is None:
        return jsonify({"error": "Model not initialized"}), 503
    
    try:
        data = request.json
        new_prompt = data.get('system_prompt')
        
        if not new_prompt:
            return jsonify({"error": "Missing 'system_prompt' in request"}), 400
        
        with model_lock:
            model.set_system_prompt(new_prompt)
        
        return jsonify({"message": "System prompt updated", "new_prompt": new_prompt})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server."""
    print("\n🛑 Shutting down server...")
    
    # Clean up GPU memory
    import torch
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        return jsonify({"error": "Not running with the Werkzeug Server"}), 500
    
    func()
    return jsonify({"message": "Server shutting down..."})

if __name__ == "__main__":
    # Initialize model before starting server
    initialize_model()
    
    # Start Flask server
    # Use threaded=False to avoid issues with PyTorch threading
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

