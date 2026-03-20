# Qwen Agent System

An intelligent AI agent powered by Qwen3-VL with autonomous tool usage capabilities. Features web search, webpage reading, local file access, and a modern ChatGPT-like interface with real-time tool execution display.

---

## Currently working on: Agent Tool Development
> Implementing web search, content extraction, and file reading tools with autonomous usage

## ✨ Features

- 🤖 **Qwen3-VL-30B-A3B-Thinking**: Advanced vision-language model with chain-of-thought reasoning (MoE: 30B total, 3.3B active)
- 🔧 **Autonomous Tool Usage**: Agent automatically decides when to use tools
- 🔍 **Web Search**: Google search integration for current information
- 📄 **Web Reader**: Extract and read content from any webpage
- 📂 **File Reader**: Access local .md and .txt files
- ⚡ **Server/Client Architecture**: Load model once, iterate instantly
- 🪟 **Agent UI**: Modern interface with real-time tool execution display
- 📊 **Real-time Streaming**: See agent thinking and tool usage live
- 🎯 **GPU Optimized**: RTX 5090 with bfloat16 support
- 🔌 **HTTP API**: RESTful API for integration with other tools

### Legacy Support
- Gemma-3-27B & 12B models still available via `model_server.py`

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

### 2. Start the Qwen Agent Server

```bash
source venv/bin/activate.fish
python src/qwen_agent_server.py
```
*First load takes 2-6 minutes. Server keeps model in GPU memory.*

### 3. Launch the Agent UI

**Agent UI with Tool Display (Recommended)** 🤖
```bash
python src/agent_ui.py
```
Modern interface showing real-time tool usage and agent reasoning.

**Features:**
- 🔍 Autonomous web search when needed
- 📄 Automatic webpage content extraction
- 📂 Local file reading on request
- Real-time tool execution display
- Toggle tool details visibility

---

## 🔧 Available Tools

### 1. Web Search (`google_search`)
Searches Google for current information, news, articles, etc.
- Returns: Top search results with titles, URLs, and snippets
- Autonomous: Agent decides when web search is needed

### 2. Web Reader (`read_webpage`)
Extracts main content from any webpage.
- Input: URL from search results or user query
- Returns: Clean text content without ads/navigation
- Use case: Reading articles, documentation, etc.

### 3. File Reader (`read_local_file`)
Reads local markdown and text files.
- Supports: `.md` and `.txt` files
- Security: Path validation to prevent directory traversal
- Returns: File content with metadata

---

## 🧠 How the Agent Works

The agent uses Cursor-style autonomous tool calling:

1. **User Query**: You ask a question
2. **Agent Reasoning**: Qwen decides if tools are needed
3. **Tool Execution**: Agent calls tools autonomously (can be parallel)
4. **Iteration**: Agent can make multiple tool calls if needed
5. **Final Response**: Agent synthesizes information and responds

**Example Flow:**
```
User: "What's the latest news on AI safety?"
↓
Agent: *Thinks* "I need current information"
↓
Agent: *Calls google_search("AI safety news 2025")*
↓
Tool: *Returns search results*
↓
Agent: *Calls read_webpage(top_result_url)*
↓
Tool: *Returns article content*
↓
Agent: "Based on recent articles, here's what's happening..."
```

---

## 🎛️ Legacy: Gemma Models

**For non-agent chat (legacy):**
```bash
# Start Gemma server
python src/model_server.py

# Use Gemma UI
python src/floating_ui.py
```

Gemma models are still available but don't support structured tool calling.

---

## 🤖 Agent UI Features

The agent UI (`src/agent_ui.py`) provides an advanced chat experience:

- **Real-time Tool Display**: See agent using tools live
  - 🔍 Web search queries
  - 📄 Webpage reading
  - 📂 File access
- **Tool Details Toggle** 🔧: Show/hide detailed tool execution
- **Markdown Rendering**: Bold, italic, code blocks, headings, lists, quotes
- **Pin Button** 📌: Keep window always on top
- **Clear History** 🧹: Start fresh conversation
- **Keyboard Shortcuts**:
  - `Enter`: Send message
  - `Shift+Enter`: New line in input

The UI dynamically shows:
- When agent decides to use a tool
- Tool parameters (search query, URL, file path)
- Tool execution results (truncated for readability)
- Final synthesized response

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

- **Primary Model**: Qwen3-VL-30B-A3B-Thinking-FP8
  - MoE architecture (30B total, 3.3B active)
  - Chain-of-thought reasoning (Thinking mode)
  - Vision-language support
- **Agent Framework**: qwen-agent with structured function calling
- **Tools**: 
  - Web scraping: BeautifulSoup4, requests
  - File access: pathlib with security validation
- **Quantization**: BitsAndBytes (4-bit NF4)
- **Framework**: HuggingFace Transformers
- **Server**: Flask REST API with SSE streaming
- **UI**: Tkinter with custom markdown and tool display
- **GPU**: CUDA 12.1 with bfloat16 optimization
- **Python**: 3.12.3

### Legacy
- **Legacy Models**: Gemma-3-27B-IT, Gemma-3-12B-IT (no tool support)

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
│   ├── qwen_agent_server.py      # Qwen agent with tools ⭐ NEW
│   ├── agent_ui.py               # Agent UI with tool display ⭐ NEW
│   ├── tools/                    # Agent tools ⭐ NEW
│   │   ├── web_search.py         # Google search tool
│   │   ├── web_reader.py         # Webpage content extraction
│   │   └── file_reader.py        # Local file reading
│   ├── main.py                   # Core Gemma implementation (legacy)
│   ├── model_server.py           # Gemma Flask server (legacy)
│   ├── floating_ui.py            # Gemma UI (legacy)
│   └── model_client.py           # CLI client (legacy)
├── requirements.txt              # Dependencies
├── README.md                     # This file
└── MEMORY.md                     # Internal knowledge base
```

---

## 🎯 Model Specifications

### Primary: Qwen3-VL-30B-A3B-Thinking-FP8
- **Architecture**: Mixture of Experts (MoE)
  - Total parameters: 30B
  - Active parameters: ~3.3B (efficient!)
- **Memory**: ~12-16GB VRAM (FP8 quantization)
- **Loading**: 3-5 minutes
- **Quality**: Excellent with chain-of-thought reasoning
- **Tool Calling**: Native structured output with qwen-agent
- **Output**: Up to 2000 tokens
- **Special Features**:
  - Vision-Language support (images)
  - Thinking mode: `<think>...</think>` blocks for transparency
  - MoE efficiency: Only activates 3.3B params per inference

**Why MoE is Perfect for Agents:**
- Small active footprint (3.3B) = fast inference
- Large total capacity (30B) = smart decisions
- Thinking mode = visible reasoning process

### Legacy: Gemma Models
- Gemma-3-27B Q4: ~16GB VRAM, no tool support, no vision
- Still available via `model_server.py` for non-agent use

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

- ✅ **October 2025 - Agent System**: Migrated to Qwen3-VL with tool support
- ✅ **Tool Integration**: Web search, webpage reading, file access
- ✅ **Agent UI**: Real-time tool execution display
- ✅ **qwen-agent**: Structured function calling framework
- ✅ Autonomous tool usage (Cursor-style)
- ✅ Multi-turn agent reasoning
- ✅ Server/client architecture for rapid development
- ✅ Complete requirements.txt with agent dependencies

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
