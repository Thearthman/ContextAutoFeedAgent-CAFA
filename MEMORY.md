# MEMORY.md - Essential Project Information

**Last Updated**: October 2025  
**Primary Model**: Gemma-3-27B-IT with 4-bit quantization  
**Development Mode**: Server/Client architecture for rapid iteration

## 🎯 Project Summary

This is an LLM playground focused on Google's Gemma models with optimized quantization for efficient inference on RTX 5090 GPU. Features a persistent model server architecture that loads the model once and keeps it in GPU memory, enabling instant code testing without 2-6 minute reload times.

## 🖥️ Hardware Setup

- **GPU**: NVIDIA RTX 5090 (34.2GB VRAM)
- **Compute Capability**: 12.0 (supports bfloat16)
- **OS**: Windows with WSL
- **Shell**: Fish shell

## 📂 Environment Configuration

### Virtual Environment
- **Location**: `venv/` in project root
- **Activation**: `source venv/bin/activate.fish`
- **Python**: 3.12.3

### Cache Configuration (Fish shell)
```fish
set -gx TRANSFORMERS_CACHE /mnt/g/huggingface
set -gx HF_HOME /mnt/g/huggingface
set -gx HF_DATASETS_CACHE /mnt/g/huggingface
```
*Models are cached to G drive to save space*

## 🤖 Available Models

### Primary: Gemma-3-27B Q4 ⭐
- **File**: `src/streaming_chat_27B_Q4.py`
- **Memory**: ~7-10GB VRAM (16.3GB in practice)
- **Quality**: Highest
- **Features**: 1000 token responses, enhanced system prompt

### Alternative: Gemma-3-12B 8-bit
- **File**: `src/streaming_chat.py`  
- **Memory**: ~6-8GB VRAM
- **Quality**: High
- **Features**: 200 token responses, faster loading

## 🔧 Model Configurations

### 27B 4-bit Configuration
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)
```

### 12B 8-bit Configuration  
```python
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.bfloat16
)
```

## 📦 Key Dependencies

```
torch>=2.8.0 (CUDA 12.1)
transformers>=4.56.0
accelerate>=1.10.0
bitsandbytes>=0.47.0
sentencepiece>=0.2.1
flask>=3.0.0 (for model server)
```

**Installation:**
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start Commands

### Option 1: Direct Chat (Traditional)
```bash
# Navigate to project
cd "/mnt/p/Work/Personal/Person"

# Activate environment
source venv/bin/activate.fish

# Run primary model (27B Q4) - Takes 2-6 min to load
python src/streaming_chat_27B_Q4.py

# Run OOP version with optimizations
python src/main.py
```

### Option 2: Server/Client Mode (Recommended for Development) ⭐
```bash
# Terminal 1: Start model server (load once, keeps running)
source venv/bin/activate.fish
python src/model_server.py  # Takes 2-6 min initially

# Terminal 2: Use fast client (restarts instantly)
source venv/bin/activate.fish
python src/model_client.py  # <1 second startup

# Modify model_client.py and restart instantly!
```

**See `SERVER_SETUP.md` for complete server/client documentation.**

## 🎮 Chat Commands

- Type normally to chat
- `quit` / `exit` / `bye` - Exit chat
- `clear` - Clear conversation history
- `Ctrl+C` - Force quit

## 🐛 Common Issues & Solutions

### Memory Errors
- **8-bit quantization fails**: 27B 8-bit requires `llm_int8_enable_fp32_cpu_offload=True`
- **4-bit works reliably**: Use 27B Q4 as primary (proven stable)

### Performance
- **Loading time**: 2-6 minutes for 27B model (normal)
- **Token speed**: ~15-25 tokens/sec expected
- **Memory usage**: Monitor with GPU memory display
- **Response latency**: Instant after streaming completes (fixed by using daemon threads)

### Environment Issues
- **bfloat16 errors**: RTX 5090 supports it, use `dtype=torch.bfloat16` (not `torch_dtype`)
- **Cache location**: Ensure G drive is mounted at `/mnt/g/`
- **Python venv broken**: Recreate with WSL Python (`python3.12 -m venv venv`)
- **Module import errors**: Run from project root, not inside src/

### Server/Client Issues
- **Server won't start**: Check if port 5000 is in use (`lsof -i :5000`)
- **Client can't connect**: Ensure server is running first
- **Model stays loaded**: Server keeps model in GPU until shutdown

## 📊 Performance Benchmarks

| Model | Memory | Loading Time | Quality | Use Case |
|-------|--------|--------------|---------|----------|
| 27B Q4 | ~16GB | ~6 min | Highest | Primary choice |
| 12B 8-bit | ~6GB | ~2 min | High | Quick testing |

## 🗂️ File Structure

```
src/
├── streaming_chat_27B_Q4.py  # Primary 27B Q4 interface (standalone)
├── streaming_chat.py         # 12B 8-bit interface  
├── main.py                   # OOP version with optimizations ⭐
├── model_server.py           # Persistent model server (Flask API) ⭐
├── model_client.py           # Fast client for server (instant restart) ⭐
├── chat.py                   # Non-streaming version
└── debug_gemma.py            # Debugging tool (deleted)

Root files:
├── requirements.txt          # All dependencies with versions
├── SERVER_SETUP.md           # Server/client documentation
├── MEMORY.md                 # This file - project knowledge
├── README.md                 # Project overview
└── packages_backup.txt       # Backup of installed packages
```

## 🔄 Git Status

- **Current branch**: master
- **Last commit**: Added Gemma implementations with quantization
- **Files tracked**: All essential chat interfaces and configs

## 🎯 User Preferences

- **Primary model**: Gemma-3-27B with 4-bit quantization
- **Focus**: Quality over speed (27B preferred over 12B)
- **Output**: Long-form responses (1000 tokens for 27B)
- **No comparison files**: Stick to requested implementations only

## 💡 Development Workflow

### For Production Use:
```bash
python src/streaming_chat_27B_Q4.py  # Standalone, simple
python src/main.py                    # OOP version
```

### For Development/Testing (Recommended):
```bash
# Terminal 1 (leave running):
python src/model_server.py

# Terminal 2 (modify & restart rapidly):
python src/model_client.py
```

## 📋 Todo List

- [x] Fix Python venv (WSL Python 3.12)
- [x] Create requirements.txt
- [x] Fix torch_dtype deprecation warnings
- [x] Implement model server/client architecture
- [x] Document server setup
- [ ] Add LaTeX rendering support to UI
- [ ] Implement Flash Attention 2 optimization
- [ ] Create floating window UI with markdown rendering

## 🎯 Recent Improvements

- **Server/Client Architecture**: Load model once, test code instantly
- **Fixed venv**: Now uses WSL Python 3.12 (was broken by Microsoft Store Python)
- **Optimized imports**: Fixed deprecation warnings (dtype vs torch_dtype)
- **Better documentation**: Added SERVER_SETUP.md and requirements.txt

---

**Note**: This file should be updated whenever significant changes are made to the project configuration or when new optimizations are discovered.
