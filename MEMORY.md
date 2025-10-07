# MEMORY.md - Internal Project Knowledge Base

**Last Updated**: October 2025  
**Primary Model**: Gemma-3-27B-IT with 4-bit quantization  
**Development Mode**: Server/Client architecture for rapid iteration

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

### Gemma-3-27B Q4 Configuration (Primary, but uses 12B during development for better loading time)
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
```
- **Actual VRAM usage**: ~16.3GB (not 7-10GB as docs claim)
- **Loading time**: 2-6 minutes (varies by system load)
- **Token speed**: ~15-25 tokens/sec
- **Max tokens**: 1000 tokens configured
- **Proven stable**: Use as primary configuration

### Gemma-3-12B 8-bit Configuration (Alternative)
- **VRAM usage**: ~6-8GB
- **Loading time**: ~2 minutes
- **Max tokens**: 200 tokens configured
- **Use case**: Quick testing when 27B is too heavy

### Critical Configuration Notes
- **Always use**: `dtype=torch.bfloat16` (NOT `torch_dtype` - deprecated)
- **8-bit 27B fails** without `llm_int8_enable_fp32_cpu_offload=True`
- **4-bit is more reliable** for 27B than 8-bit
- **RTX 5090 supports bfloat16** natively (Compute Capability 12.0)

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

- **Primary model**: Gemma-3-27B Q4 (quality over speed)
- **Output length**: Long-form responses (1000 tokens)
- **No comparison files**: Don't create side-by-side comparisons
- **Stick to requested implementations**: Don't add extra features

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
├── main.py                   # OOP version, core implementation
├── streaming_chat_27B_Q4.py  # Standalone 27B Q4 (simple)
├── streaming_chat.py         # Standalone 12B 8-bit (simple)
├── model_server.py           # Flask server (persistent model)
├── model_client.py           # CLI client (instant restart)
└── floating_ui.py            # GUI client with markdown ⭐ NEW

Root:
├── requirements.txt          # All dependencies
├── MEMORY.md                 # This file
├── README.md                 # User-facing docs
└── venv/                     # Virtual environment
```

**Implementation notes:**
- `main.py` is the core - server/client/UI all use it
  - `generate_response()` - Returns full response (for CLI client)
  - `generate_response_stream()` - Yields tokens in real-time (for SSE streaming)
  - `StopOnTokens` - Custom stopping criteria to handle Gemma's `<end_of_turn>` token
- `model_server.py` has two endpoints:
  - `/generate` - Returns complete response (blocking)
  - `/generate_stream` - Streams tokens via Server-Sent Events
- `floating_ui.py` uses SSE streaming for real-time token display
- `streaming_chat_*.py` are standalone for simple use
- **NO torch.compile()** - Removed to prevent graph breaks with quantized models
- `model_server.py` keeps model in GPU, serves HTTP API
- `model_client.py` is CLI interface to server
- `floating_ui.py` is GUI interface with tkinter + markdown

---

## 📋 Completed & Pending Tasks

### ✅ Completed
- [x] Fixed Python venv (WSL Python 3.12)
- [x] Created requirements.txt with all versions
- [x] Fixed torch_dtype deprecation warnings
- [x] Implemented server/client architecture
- [x] Created SERVER_SETUP.md documentation
- [x] Built floating UI with markdown rendering
- [x] Added always-on-top pin feature to UI

### 🚧 Future Improvements
- [ ] Add LaTeX rendering to UI (for math formulas)
- [ ] Implement Flash Attention 2 optimization
- [ ] Add streaming token display in UI (SSE)
- [ ] Create system tray icon for UI
- [ ] Add conversation export/import
- [ ] Implement prompt templates
- [ ] Add voice input/output

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

**October 2025:**
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
