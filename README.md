# Context Auto Feed Agent - CAFA

## 🎯 Project Overview

A high-performance LLM playground featuring Google's Gemma models with optimized quantization and a **persistent model server architecture** for rapid development iteration.

### Core Features:
- **Gemma Model Integration**: Optimized implementations for Gemma-3-12B and Gemma-3-27B models
- **Advanced Quantization**: 4-bit and 8-bit quantization for memory efficiency
- **Real-time Streaming**: Token-by-token streaming chat interfaces
- **Hardware Optimization**: RTX 5090 optimized with bfloat16 support
- **Server/Client Architecture**: Load model once, test code changes instantly ⭐ **NEW**

## 🚀 Features

### ✅ Implemented
- **Gemma-3-12B with 8-bit quantization** (~6-8GB VRAM)
- **Gemma-3-27B with 4-bit quantization** (~7-10GB VRAM) ⭐ **Primary**
- **Real-time streaming chat** with token-by-token output
- **Conversation history management** with context limits
- **GPU optimization** for RTX 5090 with bfloat16 support
- **Automatic caching** to G drive (`/mnt/g/huggingface`)
- **Persistent model server** for rapid development (Flask API) ⭐ **NEW**
- **Fast client interface** with <1 second restart time ⭐ **NEW**
- **Markdown rendering support** (in development)

### 🎯 Primary Configuration
- **Model**: Gemma-3-27B-IT with 4-bit quantization
- **Memory usage**: ~7-10GB VRAM (vs ~54GB full precision)
- **Quality**: Highest available with efficient memory usage
- **Speed**: Fast inference with streaming output

## 🛠️ Technology Stack

- **LLM Model**: Google Gemma-3-27B-IT (primary), Gemma-3-12B-IT (alternative)
- **Quantization**: BitsAndBytes (4-bit/8-bit)
- **Inference**: HuggingFace Transformers with streaming
- **Hardware**: NVIDIA RTX 5090 (34.2GB VRAM)
- **Precision**: bfloat16 compute optimized
- **Cache**: G drive (`/mnt/g/huggingface`) for model storage
- **Server**: Flask HTTP API for persistent model hosting
- **Python**: 3.12.3 (WSL)
- **CUDA**: 12.1

## 📋 Prerequisites

- Python 3.9+
- CUDA-compatible GPU (recommended for local inference)
- Sufficient RAM (32GB+ recommended for Gemma-27B)
- Git

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Person
```

2. Create a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate.fish  # Fish shell
# or source venv/bin/activate   # Bash shell
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Environment is auto-configured in `venv/bin/activate.fish`:
```fish
set -gx HF_HOME /mnt/g/huggingface
set -gx TRANSFORMERS_CACHE /mnt/g/huggingface
set -gx HF_DATASETS_CACHE /mnt/g/huggingface
```

## 🏗️ Project Structure

```
llm-playground/
├── src/
│   ├── models/          # Model integration and management
│   ├── memory/          # Long-term memory systems
│   ├── rag/             # RAG implementation
│   ├── processing/      # Document processing
│   ├── api/             # API endpoints
│   └── ui/              # User interface
├── data/
│   ├── documents/       # Input documents
│   ├── embeddings/      # Vector embeddings
│   └── memory/          # Memory storage
├── config/              # Configuration files
├── tests/               # Unit and integration tests
├── notebooks/           # Jupyter notebooks for experimentation
└── docs/                # Documentation
```

## 🚀 Quick Start

### Method 1: Traditional (Simple, slower iteration)

```bash
source venv/bin/activate.fish
python src/streaming_chat_27B_Q4.py  # Takes 2-6 min to load
```

### Method 2: Server/Client (Recommended for development) ⭐

**Terminal 1 - Start Server (once):**
```bash
source venv/bin/activate.fish
python src/model_server.py  # Takes 2-6 min initially, then stays loaded
```

**Terminal 2 - Use Client (instant restarts):**
```bash
source venv/bin/activate.fish
python src/model_client.py  # <1 second startup!
```

Now you can:
- Modify `model_client.py` and restart instantly
- Test different parameters without reloading
- Send API requests from custom scripts

**See `SERVER_SETUP.md` for complete documentation.**

## 🧪 Usage Examples

### Direct Model Usage
```python
from src.main import GemmaStreamingChat

# Initialize model (takes 2-6 min)
chat = GemmaStreamingChat()

# Generate response with streaming
response = chat.generate_response(
    "Explain quantum computing",
    max_new_tokens=500,
    temperature=0.7
)
```

### Server/Client API Usage
```python
from src.model_client import GemmaClient

# Connect to running server (instant)
client = GemmaClient()

# Generate response
response = client.generate("What is quantum computing?")
print(response)

# Clear history
client.clear_history()

# Get statistics
stats = client.get_stats()
```

### Quick Testing Script
```python
# quick_test.py
from src.model_client import GemmaClient

client = GemmaClient()

# Test multiple prompts rapidly
prompts = ["Question 1", "Question 2", "Question 3"]
for prompt in prompts:
    response = client.generate(prompt, max_new_tokens=200)
    print(f"Q: {prompt}\nA: {response}\n")
```

### HTTP API (cURL)
```bash
# Generate response
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "max_new_tokens": 100}'

# Check server health
curl http://localhost:5000/health

# Get statistics
curl http://localhost:5000/stats
```

## ⚡ Development Benefits

### Server/Client Architecture Advantages:

**Before (Traditional):**
- Each code change = 2-6 minute model reload
- 3 tests = 6-18 minutes total 😫
- GPU memory cleared on every run
- Slow iteration cycle

**After (Server/Client):**
- Model loads once (2-6 min) ⚡
- Code changes = <1 second restart
- 3 tests = 2-6 minutes total (first load only) 🚀
- GPU memory stays loaded
- Rapid iteration cycle

**Example workflow:**
```bash
# Day 1, 9:00 AM - Start server
python src/model_server.py  # 3 min load

# 9:03 AM - Test prompt 1
python src/model_client.py  # <1 sec

# 9:05 AM - Modify code, test prompt 2  
python src/model_client.py  # <1 sec

# 9:07 AM - Modify code, test prompt 3
python src/model_client.py  # <1 sec

# Total time: ~3 minutes vs ~9 minutes traditional!
```

## 🔬 Experiments

This playground supports various experimental setups:

1. **Rapid Prompt Engineering**: Test variations instantly with server/client
2. **Parameter Tuning**: Compare temperature/top_p/top_k combinations quickly
3. **Model Comparison**: Easy A/B testing between configurations
4. **Integration Testing**: HTTP API for external tool integration

## 📊 Monitoring & Evaluation

- Memory usage tracking (via GPU memory display in model info)
- Response quality metrics
- Conversation statistics (turns, tokens, sessions)
- Performance benchmarking
- Server health checks (`/health` endpoint)
- Real-time token streaming for immediate feedback

## 📁 Key Files

### Core Implementation
- `src/main.py` - OOP streaming chat with optimizations
- `src/streaming_chat_27B_Q4.py` - Standalone 27B Q4 interface
- `src/streaming_chat.py` - Standalone 12B 8-bit interface

### Server/Client Architecture ⭐
- `src/model_server.py` - Persistent Flask API server
- `src/model_client.py` - Fast client with instant restart
- `SERVER_SETUP.md` - Complete server/client documentation

### Configuration
- `requirements.txt` - All dependencies with versions
- `venv/bin/activate.fish` - Environment setup with HF cache paths
- `MEMORY.md` - Project knowledge base and troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 References

- [Google Gemma Models](https://ai.google.dev/gemma)
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [Long-term Memory in AI Systems](https://arxiv.org/abs/2301.04589)

## 🐛 Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :5000

# Kill existing process
kill -9 <PID>
```

**Client can't connect:**
```bash
# Verify server is running
curl http://localhost:5000/health
```

**Python venv broken:**
```bash
# Recreate with WSL Python
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate.fish
pip install -r requirements.txt
```

**Import errors:**
- Always run from project root: `python src/model_server.py`
- Never run from inside src/: `cd src && python model_server.py` ❌

**See `MEMORY.md` for complete troubleshooting guide.**

## 📞 Support

For questions and support, please open an issue or check `MEMORY.md` for common solutions.

---

**Status**: ✅ Production Ready | **Last Updated**: October 2025

### Recent Updates:
- ✅ Server/Client architecture for rapid development
- ✅ Fixed Python venv (WSL Python 3.12)
- ✅ Complete requirements.txt with all dependencies
- ✅ Fixed deprecation warnings (dtype vs torch_dtype)
- 🚧 UI interface with markdown rendering (in progress)
- 📋 LaTeX rendering support (planned)
