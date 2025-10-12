#!/usr/bin/env python
"""
Memory API Server Launcher
启动 Memory Tool 的 FastAPI 服务器
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    
    print("🧠 Starting Memory Tool API Server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(
        "memory_tool.api.memory_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

