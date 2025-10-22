# ContextAutoFeedAgent-CAFA

**An intelligent AI assistant system integrating LLM (Large Language Models) with a smart memory management system, featuring context-aware memory retrieval and human-like memory mechanisms.**

---

## 🎯 Project Overview

ContextAutoFeedAgent-CAFA (Context Auto Feed Agent) is a complete AI assistant system that combines:
- **Multiple LLM Support**: Local models (Gemma) + Online APIs (OpenAI, Claude, Gemini, etc.)
- **Intelligent Memory System**: Semantic memory storage with smart weight evaluation and time decay
- **Modern UI**: ChatGPT-like floating interface with markdown rendering
- **Obsidian Integration**: Designed for deep integration with knowledge management systems

---

## ✨ Key Features

### 🤖 LLM Support
- **Local Models**: 
  - Gemma-3-27B (4-bit quantized)
  - Gemma-3-12B (8-bit quantized)
  - GPU optimized with CUDA support
- **Online APIs**:
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic (Claude)
  - Google (Gemini)
  - Chinese LLMs (Qwen, ERNIE)
  - Custom API endpoints

### 🧠 Smart Memory System ⭐
- **Semantic Vector Storage**: 384-dimensional embeddings with cosine similarity search
- **Intelligent Weight Evaluation**: AI-powered importance assessment (10+ dimensions)
- **5-Level Memory Classification**:
  | Level | Weight | Half-life | Examples |
  |-------|--------|-----------|----------|
  | Permanent | ≥0.9 | 365 days | API keys, passwords, birthdays |
  | Important | 0.75-0.89 | 90 days | Project info, meetings |
  | Regular | 0.5-0.74 | 30 days | Learning content, preferences |
  | Temporary | 0.3-0.49 | 7 days | Casual thoughts |
  | Low Priority | <0.3 | 3 days | Small talk, greetings |
- **Differential Decay**: Important memories last longer
- **User Prompting**: Intelligent suggestions for weight adjustment

### 🪟 Modern User Interface
- **Floating UI**: ChatGPT-style interface with markdown rendering
- **Real-time Streaming**: Token-by-token response generation
- **Memory Management**: Visual memory retrieval and testing
- **API Switching**: Easy toggle between different LLM services
- **Pin Feature**: Keep window always on top

### 🔌 Integrated Architecture
```
┌─────────────────────────────────────┐
│     Floating UI (User Interface)    │
└────────────┬────────────────────────┘
             │
             ↓
┌────────────────────────────────────┐
│   Integrated Service                │
│   • Smart Memory Judgment           │
│   • Auto Memory Retrieval           │
│   • Auto Memory Storage             │
└──────┬──────────────┬───────────────┘
       │              │
       ↓              ↓
┌─────────────┐  ┌──────────────┐
│  LLM Service │  │ Memory Service│
│  (Online/    │  │ (Smart Weight)│
│   Local)     │  │               │
└─────────────┘  └──────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- 16GB+ RAM recommended
- GPU with 16GB+ VRAM (for local models, optional)
- ~50GB disk space for local models (optional)

**Software:**
- Python 3.9+ (3.12 recommended)
- CUDA 11.8+ (for local GPU models, optional)
- Windows/Linux/WSL2

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ContextAutoFeedAgent-CAFA

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Launch

**Windows Users:**
```cmd
start_cafa.bat
```

**All Platforms:**
```bash
python start_cafa.py
```

The unified launcher will guide you through:
1. **System Startup** - Launch services for daily use
2. **Testing** - Test memory tool functionality

### Recommended Quick Start

**Option 1: Floating UI with Memory (Recommended) ⭐**
```bash
python start_cafa.py
# Select: 1 (System Startup) → 1 (Floating UI with Memory)
```
This starts:
- Memory API Server (port 8000)
- Floating UI

**Option 2: Full System with Online API**
```bash
# Set API key first
export OPENAI_API_KEY="your-api-key"
# or create api_config.json

python start_cafa.py
# Select: 1 (System Startup) → 2 (Full System with Online API)
```
This starts:
- Memory API Server (port 8000)
- Online API Server (port 5001)
- Floating UI

---

## 📁 Project Structure

```
ContextAutoFeedAgent-CAFA/
│
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
├── LICENSE                   # MIT License
│
├── start_cafa.py             # Unified launcher ⭐
├── start_cafa.bat            # Windows quick start
├── run_memory_api.py         # Memory API server
├── api_config.json.example   # API configuration example
│
├── src/                      # Source code
│   ├── main.py                      # Local model core
│   ├── model_server.py              # Local model server
│   ├── model_client.py              # Model client
│   ├── online_model_server.py       # Online API server
│   ├── advanced_floating_ui.py      # Floating UI ⭐
│   ├── integrated_llm_memory.py     # Integrated service
│   │
│   └── memory_tool/                 # Memory system 🧠
│       ├── __init__.py
│       ├── memory_store.py          # Basic memory storage
│       ├── enhanced_memory_store.py # Enhanced storage
│       ├── smart_weight.py          # Smart weight evaluation ⭐
│       ├── embeddings.py            # Text vectorization
│       ├── decay.py                 # Time decay logic
│       │
│       └── api/                     # API interfaces
│           ├── __init__.py
│           ├── memory_manager.py    # Memory coordinator
│           └── memory_api.py        # FastAPI endpoints
│
├── tests/                    # Tests
│   ├── integration/
│   │   └── test_integrated_system.py
│   ├── test_memory_unit.py          # Unit tests
│   ├── test_smart_memory.py         # Smart weight tests
│   ├── auto_retrieval_test.py       # Auto retrieval tests
│   ├── interactive_memory_test.py   # Interactive tests
│   ├── import_chatgpt_history.py    # Import ChatGPT data
│   └── README_IMPORT_TEST.md
│
├── data/                     # Data directory
│   ├── test_outputs/                # Test outputs
│   │   ├── auto_retrieval_memory.json
│   │   ├── auto_retrieval_report.json
│   │   └── interactive_memory.json
│   └── README.md
│
├── examples/                 # Examples
│   ├── data/
│   │   └── chatgpt_export_example.json
│   └── README.md
│
├── docs/                     # Documentation
│   ├── guides/                      # User guides
│   │   ├── online-llm-guide.md
│   │   ├── server-setup.md
│   │   └── (more guides...)
│   │
│   ├── development/                 # Development docs
│   │   ├── architecture.md
│   │   └── memory-weight-system.md
│   │
│   ├── api/                        # API documentation
│   │   └── memory-tool.md
│   │
│   ├── PROJECT_SUMMARY.md          # Project summary
│   └── OBSIDIAN_PLUGIN_DEVELOPMENT.md
│
├── plan/                     # Project planning
│   ├── PROJECT_BOOK.md
│   ├── PROJECT_BOOK_EN.md
│   └── ROADMAP_2025.md
│
├── scripts/                  # Utility scripts
│   └── README.md
│
└── tools/                    # Tools
    └── README.md
```

---

## 💡 Core Innovations

### 1. Smart Weight Evaluation System ⭐

**Problem**: Traditional memory systems use the same decay rate for all memories, leading to:
- Important information forgotten too quickly
- Unimportant information taking up space
- No priority differentiation

**Solution**:
- ✅ Automatic importance analysis (10+ dimensions)
- ✅ 5-level classification management
- ✅ Differential decay (permanent memories decay 50% in 1 year vs 3 days for low priority)
- ✅ User prompting mechanism

**Evaluation Dimensions**:
- Explicit memory markers ("remember", "important", "don't forget")
- Question vs statement
- Personal information (names, dates, preferences)
- Technical details (code, commands, configurations)
- Emotional content
- Length and detail level
- Temporal indicators (deadlines, schedules)

### 2. Integrated Architecture ✅

**User Mode**:
- Automatically judges if memory retrieval is needed
- Smart context enhancement
- Transparent memory usage

**Update Memory Mode**:
- Automatically stores important conversations
- Smart weight evaluation
- Differential decay strategy

### 3. Multi-LLM Support ⭐

No GPU required! Support for:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Google (Gemini)
- Chinese LLMs (Qwen, ERNIE)
- Local models (with GPU)
- Custom API endpoints

---

## 📖 Usage Examples

### Python API - Memory Tool

```python
from src.memory_tool.enhanced_memory_store import EnhancedMemoryStore

# Create enhanced memory store
store = EnhancedMemoryStore()

# Add memories (auto weight evaluation)
store.add_memory("I learned Python programming today")
# Auto-evaluated weight: ~0.6 (Regular memory, 30-day half-life)

store.add_memory("Remember: My birthday is March 15th")
# Auto-evaluated weight: 1.0 (Permanent memory, 365-day half-life)

# Search memories
results = store.search("Python learning", top_k=3)
for result in results:
    print(f"Memory: {result['text']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Weight: {result['importance']}")

# Time decay (differential based on weight)
store.decay()
```

### REST API - Memory Service

```bash
# Store memory
curl -X POST "http://localhost:8000/store?text=I%20learned%20Python%20today"

# Retrieve memory
curl "http://localhost:8000/recall?query=Python%20learning"

# Trigger decay
curl -X POST "http://localhost:8000/decay"
```

### Python API - LLM Client

```python
from src.model_client import GemmaClient

# Connect to running server
client = GemmaClient()

# Generate response
response = client.generate("Explain quantum computing")
print(response)

# Clear history
client.clear_history()
```

---

## 🔧 Configuration

### Online API Configuration

**Method 1: Environment Variables**
```bash
export OPENAI_API_KEY="your-api-key"
export LLM_PROVIDER="openai"  # openai, anthropic, google, qwen, ernie
```

**Method 2: Configuration File**
```bash
# Copy example config
cp api_config.json.example api_config.json

# Edit api_config.json
{
  "provider": "openai",
  "api_key": "your-api-key",
  "model": "gpt-3.5-turbo",
  "base_url": "https://api.openai.com/v1"  # optional
}
```

### Local Model Configuration

Models are cached to save space:
```bash
# Set HuggingFace cache directory
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

---

## 🧪 Testing

### Quick Test - Floating UI Retrieval Test (Recommended) ⭐

```bash
python start_cafa.py
# Select: 2 (Testing) → 1 (Floating UI Retrieval Test)
```

This will:
1. Import ChatGPT history to memory system
2. Start Memory API server (background)
3. Open floating UI for visual retrieval testing

### Automated Retrieval Test

```bash
python tests/auto_retrieval_test.py --conversations 5 --messages 20
```

### Interactive Memory Test

```bash
python tests/interactive_memory_test.py
```

### Unit Tests

```bash
python tests/test_memory_unit.py
```

---

## 📊 Performance Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Vector Dimension** | 384 | Semantic vectors |
| **Search Speed** | <100ms | Within 1000 memories |
| **Weight Evaluation** | <50ms | Per memory |
| **Memory Usage** | ~2GB | Including embedding model |
| **Storage Efficiency** | ~1KB/memory | JSON format |
| **Retrieval Accuracy** | ≥95% | Semantic search |

---

## 🎯 Use Cases

### 1. Personal AI Assistant
- Remember user preferences
- Track project progress
- Remind important matters

### 2. Knowledge Management
- Learning notes management
- Automatic categorization
- Smart review reminders

### 3. Project Development
- Tech stack recording
- Bug tracking
- Decision history

### 4. Obsidian Integration (Planned)
- Automatic note indexing
- Related content recommendations
- Smart review system

---

## 🗺️ Roadmap

### Q4 2025 (October - December)

**Phase 1: Obsidian Plugin Development** (October)
- Week 1-2: Plugin MVP and chat interface
- Week 3-4: Smart note features and optimization

**Phase 2: System Optimization** (November)
- Week 5-6: Memory system and performance optimization
- Week 7-8: UI improvements and integration testing

**Phase 3: Release Preparation** (December)
- Week 9-10: Documentation and open source release
- Week 11-12: Community feedback and iteration

See [ROADMAP_2025.md](plan/ROADMAP_2025.md) for details.

---

## 📚 Documentation

### User Guides
- [Getting Started](docs/guides/getting-started-testing.md)
- [Online LLM Guide](docs/guides/online-llm-guide.md)
- [Server Setup](docs/guides/server-setup.md)
- [Floating UI Testing Guide](docs/悬浮窗口检索测试指南.md)

### Development Docs
- [Architecture](docs/development/architecture.md)
- [Memory Weight System](docs/development/memory-weight-system.md)
- [Project Summary](docs/PROJECT_SUMMARY.md)

### API Reference
- [Memory Tool API](docs/api/memory-tool.md)
- Swagger UI: `http://localhost:8000/docs` (when Memory API is running)
- ReDoc: `http://localhost:8000/redoc`

---

## 🛠️ Technology Stack

- **Models**: 
  - Local: Google Gemma-3-27B-IT, Gemma-3-12B-IT
  - Online: OpenAI, Anthropic, Google, Qwen, ERNIE
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Quantization**: BitsAndBytes (4-bit/8-bit)
- **Framework**: HuggingFace Transformers
- **Backend**: Flask, FastAPI
- **UI**: Tkinter with custom markdown renderer
- **GPU**: CUDA 12.1 with bfloat16 optimization
- **Python**: 3.12.3

---

## 🐛 Troubleshooting

**Server won't start:**
```bash
# Check if port is in use
# Windows:
netstat -ano | findstr :8000
# Linux/Mac:
lsof -i :8000

# Kill process if needed
# Windows:
taskkill /PID <PID> /F
# Linux/Mac:
kill -9 <PID>
```

**Import errors:**
```bash
# Always run from project root
python src/model_server.py  ✅
cd src && python model_server.py  ❌
```

**UI won't open (WSL/Linux):**
```bash
# Install tkinter
sudo apt-get install -y python3-tk

# Test tkinter
python -c "import tkinter"
```

**Model download fails:**
```bash
# Set HuggingFace mirror
export HF_ENDPOINT=https://hf-mirror.com
```

---

## 🌟 Recent Updates

- ✅ **October 2025**: Project reorganization (GitHub standard structure)
- ✅ Smart memory weight evaluation system
- ✅ Integrated LLM memory service
- ✅ Online API support (OpenAI, Claude, Gemini, etc.)
- ✅ Unified launcher (start_cafa.py)
- ✅ Advanced floating UI with memory management
- ✅ Comprehensive testing framework

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit Issues and Pull Requests.

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd ContextAutoFeedAgent-CAFA

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_memory_unit.py
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Resources

- [Google Gemma Documentation](https://ai.google.dev/gemma)
- [BitsAndBytes Quantization](https://github.com/TimDettmers/bitsandbytes)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [Sentence-Transformers](https://www.sbert.net/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## 📞 Support

- Check [docs/](docs/) for detailed documentation
- Open an issue for bugs or feature requests
- Review server logs for debugging
- See [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) for complete project overview

---

<div align="center">
  <strong>Built with ❤️ for intelligent context-aware AI assistance</strong>
  <br><br>
  <em>ContextAutoFeedAgent-CAFA - Your Personal AI with Human-like Memory</em>
</div>
