#!/usr/bin/env python
"""
Memory API Server Launcher
Launches the Memory Tool FastAPI server
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import uvicorn
    
    print("🧠 Starting Memory Tool API Server...")
    print("📍 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("\nPress Ctrl+C to stop server\n")
    
    uvicorn.run(
        "memory_tool.api.memory_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

