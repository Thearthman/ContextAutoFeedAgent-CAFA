# Gemma LLM Playground

A high-performance LLM playground featuring Google's Gemma models with optimized quantization, persistent model server architecture, and a modern ChatGPT-like floating UI.

---

## ✨ Features

- 🤖 **Gemma-3-27B & Gemma-3-12B**: Optimized 4-bit and 8-bit quantized models
- ⚡ **Server/Client Architecture**: Load model once, iterate instantly
- 🪟 **Floating UI**: Modern ChatGPT-like interface with markdown rendering
- 📊 **Real-time Streaming**: Token-by-token response generation
- 🎯 **GPU Optimized**: RTX 5090 with bfloat16 support
- 🔌 **HTTP API**: RESTful API for integration with other tools

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd Person

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate.fish  # or: source venv/bin/activate

# Install system dependencies (required for floating UI on WSL/Linux)
sudo apt-get update
sudo apt-get install -y python3-tk

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Start the Model Server

```bash
source venv/bin/activate.fish
python src/model_server.py
```
*First load takes 2-6 minutes. Server keeps model in GPU memory.*

### 3. Choose Your Interface

**Option A: Floating UI (Recommended)** 🪟
```bash
python src/floating_ui.py
```
Modern ChatGPT-like window with markdown rendering.

**Option B: Command-Line Client**
```bash
python src/model_client.py
```
Terminal-based interactive chat.

**Option C: Standalone (No Server)**
```bash
python src/streaming_chat_27B_Q4.py
```
Simple standalone script (slower iteration).

---

## 🪟 Floating UI Features

The floating UI (`src/floating_ui.py`) provides a modern chat experience:

- **Markdown Rendering**: Bold, italic, code blocks, headings, lists, quotes
- **Pin Button** 📌: Keep window always on top
- **Clear History** 🧹: Start fresh conversation
- **Statistics** 📊: View token counts and session info
- **Keyboard Shortcuts**:
  - `Enter`: Send message
  - `Shift+Enter`: New line in input

<div align="center">
  <em>Modern, responsive UI with real-time markdown rendering</em>
</div>

---

## 📖 Usage Examples

### Python API

```python
from src.model_client import GemmaClient

# Connect to running server
client = GemmaClient()

# Generate response
response = client.generate("Explain quantum computing")
print(response)

# Clear conversation history
client.clear_history()

# Get statistics
stats = client.get_stats()
print(f"Total tokens: {stats['total_tokens_generated']}")
```

### HTTP API (cURL)

```bash
# Generate response
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "max_new_tokens": 500}'

# Check server health
curl http://localhost:5000/health

# Clear conversation history
curl -X POST http://localhost:5000/clear_history

# Get statistics
curl http://localhost:5000/stats
```

### Quick Test Script

```python
from src.model_client import GemmaClient

client = GemmaClient()

# Test multiple prompts
prompts = [
    "What is machine learning?",
    "Explain neural networks",
    "What is a transformer?"
]

for prompt in prompts:
    response = client.generate(prompt, max_new_tokens=200)
    print(f"Q: {prompt}\nA: {response}\n")
```

---

## 🛠️ Technology Stack

- **Models**: Google Gemma-3-27B-IT (primary), Gemma-3-12B-IT (alternative)
- **Quantization**: BitsAndBytes (4-bit/8-bit)
- **Framework**: HuggingFace Transformers
- **Server**: Flask REST API
- **UI**: Tkinter with custom markdown renderer
- **GPU**: CUDA 12.1 with bfloat16 optimization
- **Python**: 3.12.3

---

## ⚡ Why Server/Client Architecture?

**Traditional Approach:**
- Each code change requires 2-6 minute model reload
- Testing 3 prompts = 6-18 minutes
- GPU memory cleared on every restart

**Our Approach:**
- Model loads once (2-6 min initial)
- Code changes restart in <1 second
- Testing 3 prompts = 2-6 minutes (first load only)
- GPU memory stays loaded

**Result:** 3x-10x faster development iteration! 🚀

---

## 📁 Project Structure

```
Person/
├── src/
│   ├── main.py                   # Core implementation (OOP)
│   ├── model_server.py           # Flask API server
│   ├── model_client.py           # CLI client
│   ├── floating_ui.py            # GUI with markdown rendering ⭐
│   ├── streaming_chat_27B_Q4.py  # Standalone 27B interface
│   └── streaming_chat.py         # Standalone 12B interface
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── MEMORY.md                     # Internal knowledge base
```

---

## 🎯 Model Specifications

### Primary: Gemma-3-27B Q4
- **Memory**: ~16GB VRAM
- **Loading**: 2-6 minutes
- **Quality**: Highest
- **Output**: Up to 1000 tokens

### Alternative: Gemma-3-12B 8-bit
- **Memory**: ~6-8GB VRAM
- **Loading**: ~2 minutes  
- **Quality**: High
- **Output**: Up to 200 tokens

---

## 🔧 Configuration

Models are automatically cached to G drive to save space:
```fish
# In venv/bin/activate.fish
set -gx HF_HOME /mnt/g/huggingface
set -gx TRANSFORMERS_CACHE /mnt/g/huggingface
set -gx HF_DATASETS_CACHE /mnt/g/huggingface
```

---

## 🤝 API Reference

### Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/generate` | POST | Generate response |
| `/clear_history` | POST | Clear conversation |
| `/stats` | GET | Get statistics |
| `/update_system_prompt` | POST | Change system prompt |
| `/shutdown` | POST | Shutdown server |

### Generate Request Format

```json
{
  "prompt": "Your question here",
  "max_new_tokens": 1000,
  "temperature": 0.7,
  "top_p": 0.9,
  "top_k": 40
}
```

### Response Format

```json
{
  "response": "Generated text...",
  "prompt": "Your question here",
  "timestamp": 1234567890.123
}
```

---

## 🐛 Troubleshooting

**Server won't start:**
```bash
# Check if port 5000 is already in use
lsof -i :5000
kill -9 <PID>
```

**Client can't connect:**
```bash
# Verify server is running
curl http://localhost:5000/health
```

**UI window won't open:**
```bash
# On WSL/Linux, install tkinter first
sudo apt-get install -y python3-tk

# Test tkinter availability
python -c "import tkinter"
```

**Import errors:**
```bash
# Always run from project root, not from src/
python src/model_server.py  ✅
cd src && python model_server.py  ❌
```

For detailed troubleshooting, see `MEMORY.md`.

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Model load time | 2-6 minutes |
| Token generation | 15-25 tokens/sec |
| Client startup | <1 second |
| Memory footprint | ~16GB VRAM |

---

## 🧪 Development

### Running Tests

```python
# Quick test multiple prompts
python src/model_client.py
# Then use quick_test() function
```

### Modifying the UI

```bash
# Edit floating_ui.py, then restart (instant)
python src/floating_ui.py
```

### Adding New Features

1. Start server: `python src/model_server.py`
2. Edit client code: `src/model_client.py` or `src/floating_ui.py`
3. Restart client: `<1 second` (model stays loaded!)

---

## 📝 Requirements

**Hardware:**
- NVIDIA GPU with CUDA support (16GB+ VRAM recommended)
- 32GB+ RAM
- ~50GB disk space for models

**Software:**
- Python 3.9+
- CUDA 11.8+ (12.1 recommended)
- Linux (WSL2 on Windows supported)

See `requirements.txt` for Python package dependencies.

---

## 🌟 Recent Updates

- ✅ **October 2025**: Added floating UI with markdown rendering
- ✅ Implemented always-on-top pin feature
- ✅ Server/client architecture for rapid development
- ✅ Fixed deprecation warnings (dtype vs torch_dtype)
- ✅ Complete requirements.txt with all dependencies

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔗 Resources

- [Google Gemma Documentation](https://ai.google.dev/gemma)
- [BitsAndBytes Quantization](https://github.com/TimDettmers/bitsandbytes)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)

---

## 📞 Support

- Check `MEMORY.md` for detailed troubleshooting
- Open an issue for bugs or feature requests
- Review server logs for debugging

---

<div align="center">
  <strong>Built with ❤️ for rapid LLM experimentation</strong>
</div>
