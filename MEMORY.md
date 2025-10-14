# MEMORY.md - Internal Project Knowledge Base

**Last Updated**: October 2025  
**Primary Model**: Qwen2-VL-7B-Instruct with 4-bit quantization (agent-enabled)  
**Legacy Model**: Gemma-3-27B-IT with 4-bit quantization (no tool support)  
**Development Mode**: Server/Client architecture for rapid iteration  
**New Feature**: Autonomous tool usage with qwen-agent framework

## 🎯 Purpose

This file contains internal working knowledge, troubleshooting details, and development-specific information for maintaining and debugging this project. For user-facing documentation, see README.md.

---

## 🖥️ Hardware & Environment

### Hardware Setup
- **GPU**: NVIDIA RTX 5090 (34.2GB VRAM)
- **Compute Capability**: 12.0 (supports bfloat16)
- **OS**: Windows 11 with WSL2
- **Shell**: Fish shell
- **Python**: 3.12.3 (WSL Python, NOT Microsoft Store Python)

### Environment Configuration

**Virtual Environment:**
- Location: `venv/` in project root
- Activation: `source venv/bin/activate.fish`
- **Critical**: Use WSL Python (`python3.12 -m venv venv`), not Microsoft Store Python

**Cache Configuration (in `venv/bin/activate.fish`):**
```fish
set -gx TRANSFORMERS_CACHE /mnt/g/huggingface
set -gx HF_HOME /mnt/g/huggingface
set -gx HF_DATASETS_CACHE /mnt/g/huggingface
```
*Models cached to G drive to save SSD space. Ensure G drive is mounted at `/mnt/g/`*

**Project Path:**
```bash
cd "/mnt/p/Work/Personal/Person"
```

---

## 🔧 Model Technical Details

### Qwen2-VL-7B-Instruct Q4 Configuration (Primary - Agent System)
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
```
- **Model**: `Qwen/Qwen2-VL-7B-Instruct`
- **VRAM usage**: ~8-10GB (4-bit quantization)
- **Loading time**: 2-4 minutes
- **Token speed**: ~20-30 tokens/sec (estimated)
- **Max tokens**: 2000 tokens configured
- **Special features**: 
  - Vision-language model (supports images)
  - Native structured output for tool calling
  - Compatible with qwen-agent framework
- **Upgrade path**: Can switch to Qwen2-VL-30B-Instruct (~16-20GB VRAM)

### Agent Framework: qwen-agent
- **Purpose**: Structured function calling and tool orchestration
- **Architecture**: Cursor-style autonomous tool usage
- **Features**:
  - Multi-turn reasoning
  - Parallel tool execution support
  - JSON-based function calling
  - Built-in tool registration system

### Tools Implemented
1. **google_search**: Web search via scraping
   - Returns: Top 10 results with titles, URLs, snippets
   - Rate limiting: 1-second delay between requests
2. **read_webpage**: HTML content extraction
   - Uses BeautifulSoup4 for parsing
   - Removes ads, navigation, scripts
   - Max content: 5000 chars (configurable)
3. **read_local_file**: Local file reader
   - Supports: .md and .txt files only
   - Security: Path validation, no directory traversal
   - Max content: 10000 chars (configurable)

### Legacy: Gemma-3-27B Q4 Configuration
- **VRAM usage**: ~16.3GB
- **Loading time**: 2-6 minutes
- **Token speed**: ~15-25 tokens/sec
- **Max tokens**: 1000 tokens
- **Limitation**: No structured output, no tool support
- **Status**: Still available via `model_server.py` for non-agent use

### Legacy: Gemma-3-12B 8-bit Configuration
- **VRAM usage**: ~6-8GB
- **Loading time**: ~2 minutes
- **Max tokens**: 200 tokens
- **Use case**: Quick testing (legacy only)

### Critical Configuration Notes
- **Always use**: `dtype=torch.bfloat16` (NOT `torch_dtype` - deprecated)
- **RTX 5090 supports bfloat16** natively (Compute Capability 12.0)
- **qwen-agent requirements**: Structured output support in model
- **Tool security**: All file paths validated, only .md/.txt allowed

---

## 🐛 Troubleshooting Guide

### Memory & Performance Issues

**8-bit quantization fails on 27B:**
```python
# Requires CPU offload (not recommended)
llm_int8_enable_fp32_cpu_offload=True
```
**Solution**: Use 4-bit instead - more reliable and faster.

**Post-generation delay (30-50 seconds):**
- **Cause**: PyTorch thread cleanup after streaming
- **Normal behavior**: Not a bug
- **Workaround**: None needed, inherent to transformers library

**Loading time varies (2-6 minutes):**
- **Cause**: Disk I/O to G drive, system load
- **Normal**: First load is slower, subsequent loads may be cached
- **Tip**: Use server/client mode to avoid reloading

**Token speed slow (<10 tokens/sec):**
- Check GPU utilization with `nvidia-smi`
- Ensure no other processes using GPU
- Verify bfloat16 is being used (not float32)

### Environment Issues

**bfloat16 errors despite GPU support:**
```python
# Wrong (deprecated):
torch_dtype=torch.bfloat16

# Correct:
dtype=torch.bfloat16
```

**Cache location errors:**
```bash
# Verify G drive is mounted
ls /mnt/g/huggingface
# If not mounted, check Windows disk management
```

**Python venv broken (import errors, missing packages):**
```bash
# Nuclear option - recreate venv with WSL Python
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate.fish
pip install --upgrade pip
pip install -r requirements.txt
```

**Module import errors:**
- **Cause**: Running from inside `src/` directory
- **Solution**: Always run from project root
```bash
# Correct:
python src/model_server.py

# Wrong:
cd src && python model_server.py
```

### Server/Client Issues

**Server won't start - port already in use:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Alternative: Use different port
# Edit model_server.py: app.run(port=5001)
```

**Client can't connect:**
```bash
# 1. Verify server is running
curl http://localhost:5000/health

# 2. Check server terminal for errors

# 3. Restart server if frozen
```

**Model stays loaded after server shutdown:**
```bash
# GPU memory not cleared
python -c "import torch; torch.cuda.empty_cache()"

# Or restart WSL terminal
```

**Server crashes during generation:**
- Check GPU memory with `nvidia-smi`
- May be OOM - try 12B model instead
- Check server logs for Python errors

### UI Issues

**Floating UI won't start - ModuleNotFoundError: No module named 'tkinter':**
```bash
# tkinter is NOT available via pip - it's a system package
# Install on WSL/Linux (REQUIRED):
sudo apt-get update
sudo apt-get install -y python3-tk

# Verify installation:
python3 -c "import tkinter; print('✅ tkinter working!')"
```
**Note**: tkinter cannot be installed via pip. It's a system-level package that must be installed with apt-get on WSL/Linux.

**UI connects but no responses:**
- Verify server is running: `curl http://localhost:5000/health`
- Check server terminal for generation errors
- Try clearing history in UI

**Markdown not rendering:**
- Expected behavior for complex markdown
- Supports: bold, italic, code, code blocks, headings, lists, quotes
- Doesn't support: tables, nested formatting, LaTeX

---

## 💡 Development Workflow & Tips

### Recommended Development Pattern

**Daily workflow:**
```bash
# Morning: Start server once
python src/model_server.py  # 3-6 min initial load

# Then use client/UI all day without reloading
python src/model_client.py  # <1 sec startup
python src/floating_ui.py   # <1 sec startup
```

**File modification workflow:**
- Modify `model_client.py` → restart instantly
- Modify `floating_ui.py` → restart instantly  
- Modify `model_server.py` → must restart server (3-6 min reload)

### User Preferences (from past conversations)

- **Primary model**: Qwen2-VL (agent-enabled, tool support)
- **Secondary model**: Gemma-3-27B Q4 (legacy, quality over speed)
- **Output length**: Long-form responses (2000 tokens for Qwen)
- **Tool philosophy**: Cursor-style autonomous usage
- **Vision capability**: Important for future (human-like agent)
- **Structured output**: Critical for reliable tool calling
- **No comparison files**: Don't create side-by-side comparisons
- **Stick to requested implementations**: Don't add extra features
- **Development approach**: Implement first, iterate based on testing

### Git Workflow

- **Branch**: master
- **Don't commit** without explicit request
- **Never force push** to master
- **Never skip hooks** (--no-verify)

---

## 📊 Performance Benchmarks

| Model | VRAM (Actual) | Load Time | Quality | Tokens/sec | Streaming | Use Case |
|-------|---------------|-----------|---------|------------|-----------|----------|
| 27B Q4 | ~16GB | 3-6 min | Highest | 15-25 | ✅ Real-time | Primary |
| 12B 8-bit | ~6-8GB | ~2 min | High | 20-30 | ✅ Real-time | Quick tests |

**Streaming Performance:**
- **Real-time token display**: Tokens appear instantly as generated (no delay!)
- **UI responsiveness**: Floating UI updates token-by-token via Server-Sent Events
- **Fixed 20-second delay**: ✅ SOLVED! Custom StoppingCriteria + removed torch.compile()
  - Model now stops at natural EOS token (11 tokens for "hi", not 1001!)
  - KV cache cleanup is instant with small token counts
  - Response completes in ~0.04s/token, no post-generation delays

**Comparison:**
- 27B full precision would use ~54GB (impossible on RTX 5090)
- 4-bit quantization gives 70% memory savings with minimal quality loss
- Server/client mode saves 6-18 minutes per development cycle

---

## 🗂️ File Structure Details

```
src/
├── qwen_agent_server.py      # ⭐ Qwen agent with tools (PRIMARY)
├── agent_ui.py               # ⭐ Agent UI with tool display (PRIMARY)
├── tools/                    # ⭐ Agent tools (NEW)
│   ├── __init__.py
│   ├── web_search.py         # Google search tool
│   ├── web_reader.py         # Webpage content extraction
│   └── file_reader.py        # Local file reading
├── main.py                   # Gemma core implementation (LEGACY)
├── model_server.py           # Gemma Flask server (LEGACY)
├── model_client.py           # CLI client (LEGACY)
├── floating_ui.py            # Gemma GUI (LEGACY)
├── streaming_chat_27B_Q4.py  # Standalone 27B (LEGACY)
└── streaming_chat.py         # Standalone 12B (LEGACY)

Root:
├── requirements.txt          # All dependencies (including qwen-agent)
├── MEMORY.md                 # This file
├── README.md                 # User-facing docs
└── venv/                     # Virtual environment
```

**Primary Implementation (Agent System):**
- `qwen_agent_server.py`:
  - Loads Qwen2-VL model with 4-bit quantization
  - Registers three custom tools via qwen-agent
  - Endpoints:
    - `/generate` - Complete response with tool usage
    - `/generate_stream` - SSE streaming with tool events
    - `/clear_history` - Clear agent memory
    - `/stats` - Agent statistics
  - Port: 5001 (to avoid conflict with legacy server)
  
- `agent_ui.py`:
  - Tkinter UI with markdown rendering
  - Real-time tool execution display
  - SSE event types:
    - `tool_call`: When agent invokes a tool
    - `tool_result`: When tool returns data
    - `response`: Agent's final response tokens
    - `error`: Error handling
  - Features: Pin, clear history, tool details toggle
  
- `tools/` directory:
  - Each tool implements qwen-agent's `BaseTool` class
  - Includes `TOOL_DEFINITION` dict for agent registration
  - Error handling returns strings (doesn't crash agent)
  - Security: Path validation, rate limiting, content truncation

**Legacy Implementation (Gemma):**
- `main.py` - Core Gemma functionality
- `model_server.py` - Gemma server (port 5000)
- `floating_ui.py` - Gemma UI (no tool support)
- Still functional but no agent capabilities

**Development Workflow:**
- **Agent development**: Modify `qwen_agent_server.py` → restart server (2-4 min)
- **UI development**: Modify `agent_ui.py` → restart instantly
- **Tool development**: Modify `tools/*.py` → restart server (2-4 min)

---

## 📋 Completed & Pending Tasks

### ✅ Completed (October 2025)
- [x] Fixed Python venv (WSL Python 3.12)
- [x] Created requirements.txt with all versions
- [x] Fixed torch_dtype deprecation warnings
- [x] Implemented server/client architecture
- [x] Built floating UI with markdown rendering
- [x] Added always-on-top pin feature to UI
- [x] **Migrated to Qwen2-VL-7B-Instruct**
- [x] **Implemented qwen-agent framework**
- [x] **Built autonomous tool system (Cursor-style)**
- [x] **Created 3 core tools**: web search, web reader, file reader
- [x] **Agent UI with real-time tool display**
- [x] **SSE streaming for agent events**

### 🚧 Next Steps (Agent System)
- [ ] Test with real queries (web search, file reading)
- [ ] Upgrade to Qwen2-VL-30B for better quality
- [ ] Add Google Custom Search API option (vs scraping)
- [ ] Implement vision capabilities (image input)
- [ ] Add more tools:
  - [ ] Calculator tool
  - [ ] Code execution tool (sandboxed)
  - [ ] Database query tool
  - [ ] Obsidian note search tool
- [ ] Add conversation export/import
- [ ] Implement prompt templates for agent
- [ ] Add voice input/output

### 🚧 Future Improvements (General)
- [ ] Flash Attention 2 optimization
- [ ] System tray icon for UI
- [ ] LaTeX rendering (for math)

---

## 🔍 Known Issues & Quirks

### Expected Behaviors (Not Bugs)
2. **High initial load time (2-6 min)**: Large model + quantization - normal
3. **VRAM higher than expected (16GB vs 10GB)**: Quantization overhead - normal
4. **Server keeps GPU memory**: By design - allows instant requests

### Actual Bugs (None currently known)
*Document bugs here as they're discovered*

---

## 📝 Version History

**October 2025 - Agent System Migration:**
- ✅ Migrated from Gemma to Qwen2-VL-7B-Instruct
- ✅ Implemented qwen-agent framework
- ✅ Built autonomous tool calling system (Cursor-style)
- ✅ Created 3 core tools: google_search, read_webpage, read_local_file
- ✅ Agent UI with real-time tool execution display
- ✅ SSE streaming adapted for agent events
- ✅ Updated requirements.txt with agent dependencies
- ✅ Preserved legacy Gemma functionality

**October 2025 - Earlier:**
- ✅ Added floating UI with markdown rendering (`floating_ui.py`)
- ✅ Server/client architecture fully functional
- ✅ Fixed all deprecation warnings
- ✅ Reorganized MEMORY.md vs README.md (no duplication)

---

**Note**: Update this file whenever:
- New bugs are discovered and solved
- Configuration changes are made
- Hardware/environment changes
- New optimization techniques are found
- User preferences change
