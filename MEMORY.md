# MEMORY.md - Essential Project Information

**Last Updated**: September 2024  
**Primary Model**: Gemma-3-27B-IT with 4-bit quantization

## 🎯 Project Summary

This is an LLM playground focused on Google's Gemma models with optimized quantization for efficient inference on RTX 5090 GPU. The primary configuration uses Gemma-3-27B with 4-bit quantization for the best quality/memory balance.

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
torch>=2.1.0
transformers>=4.35.0
accelerate>=0.24.0
bitsandbytes>=0.41.0
sentencepiece>=0.1.99
```

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd "/mnt/p/Work/Personal/Person"

# Activate environment
source venv/bin/activate.fish

# Run primary model (27B Q4)
python src/streaming_chat_27B_Q4.py

# Run alternative (12B 8-bit)
python src/streaming_chat.py

# Debug issues
python src/debug_gemma.py
```

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

### Environment Issues
- **bfloat16 errors**: RTX 5090 supports it, check dtype conversion
- **Cache location**: Ensure G drive is mounted at `/mnt/g/`

## 📊 Performance Benchmarks

| Model | Memory | Loading Time | Quality | Use Case |
|-------|--------|--------------|---------|----------|
| 27B Q4 | ~16GB | ~6 min | Highest | Primary choice |
| 12B 8-bit | ~6GB | ~2 min | High | Quick testing |

## 🗂️ File Structure

```
src/
├── streaming_chat_27B_Q4.py  # Primary 27B Q4 interface ⭐
├── streaming_chat.py         # 12B 8-bit interface
├── debug_gemma.py           # Debugging tool
├── main.py                  # Original HF example
└── chat.py                  # Non-streaming version
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

## 💡 Next Steps

1. Use 27B Q4 as primary interface
2. Test performance with various conversation lengths
3. Monitor memory usage patterns
4. Future: Implement memory systems and RAG (when requested)

---

**Note**: This file should be updated whenever significant changes are made to the project configuration or when new optimizations are discovered.
