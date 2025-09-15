# Context Auto Feed Agent - CAFA

## 🎯 Project Overview

This playground provides production-ready implementations for:

- **Gemma Model Integration**: Optimized implementations for Gemma-3-12B and Gemma-3-27B models
- **Advanced Quantization**: 4-bit and 8-bit quantization for memory efficiency
- **Real-time Streaming**: Token-by-token streaming chat interfaces
- **Hardware Optimization**: RTX 5090 optimized with bfloat16 support

## 🚀 Features

### ✅ Implemented
- **Gemma-3-12B with 8-bit quantization** (~6-8GB VRAM)
- **Gemma-3-27B with 4-bit quantization** (~7-10GB VRAM) ⭐ **Primary**
- **Real-time streaming chat** with token-by-token output
- **Conversation history management** with context limits
- **GPU optimization** for RTX 5090 with bfloat16 support
- **Automatic caching** to G drive (`/mnt/g/huggingface`)
- **Debug tools** for troubleshooting model issues

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

## 📋 Prerequisites

- Python 3.9+
- CUDA-compatible GPU (recommended for local inference)
- Sufficient RAM (32GB+ recommended for Gemma-27B)
- Git

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-playground
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
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

1. **Activate virtual environment**:
```bash
source venv/bin/activate.fish  # Fish shell
# or source venv/bin/activate   # Bash shell
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Start primary chat interface** (Gemma-3-27B with 4-bit):
```bash
python src/streaming_chat_27B_Q4.py
```

4. **Alternative: 12B model** (for faster loading):
```bash
python src/streaming_chat.py
```

## 🧪 Usage Examples

### Basic Chat with Memory
```python
from src.models import GemmaModel
from src.memory import LongTermMemory

model = GemmaModel()
memory = LongTermMemory()

response = model.chat("Tell me about machine learning", memory_context=memory.retrieve())
memory.store(response)
```

### Document Processing
```python
from src.processing import DocumentProcessor

processor = DocumentProcessor()
chunks = processor.process_pdf("document.pdf")
embeddings = processor.generate_embeddings(chunks)
```

### RAG Query
```python
from src.rag import RAGSystem

rag = RAGSystem()
rag.ingest_document("research_paper.pdf")
response = rag.query("What are the main findings?")
```

## 🔬 Experiments

This playground supports various experimental setups:

1. **Memory Persistence**: Test different memory architectures
2. **RAG Optimization**: Compare retrieval strategies
3. **Multi-modal Input**: Process various document formats
4. **Context Management**: Experiment with conversation flow

## 📊 Monitoring & Evaluation

- Memory usage tracking
- Response quality metrics
- Retrieval accuracy measurements
- Performance benchmarking

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

## 📞 Support

For questions and support, please open an issue or reach out via [contact method].

---

**Status**: 🚧 In Development | **Last Updated**: $(date +%Y-%m-%d)
