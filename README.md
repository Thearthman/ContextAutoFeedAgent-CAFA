# LLM Playground: Advanced Memory & Multi-Format Processing

A comprehensive playground for experimenting with Large Language Models, focusing on long-term memory systems, RAG (Retrieval-Augmented Generation), and multi-format document processing capabilities.

## 🎯 Project Overview

This playground is designed for developing and testing advanced LLM capabilities, specifically:

- **Long-term Memory Systems**: Persistent memory management and retrieval
- **RAG Implementation**: Retrieval-Augmented Generation with various data sources
- **Multi-format Document Processing**: Support for Word, PDF, and other document formats
- **Model Integration**: Built around Google's Gemma-3-27B-IT model

## 🚀 Features

### Core Capabilities
- [x] Google Gemma-3-27B-IT model integration
- [ ] Long-term memory storage and retrieval
- [ ] Vector database integration for RAG
- [ ] Document processing pipeline
- [ ] Conversation context management

### Document Processing
- [ ] PDF text extraction and processing
- [ ] Microsoft Word document handling
- [ ] Text chunking and embedding generation
- [ ] Metadata extraction and indexing

### Memory Systems
- [ ] Episodic memory for conversation history
- [ ] Semantic memory for knowledge storage
- [ ] Working memory for active context
- [ ] Memory consolidation and retrieval mechanisms

### RAG Components
- [ ] Document ingestion pipeline
- [ ] Vector similarity search
- [ ] Context-aware retrieval
- [ ] Source attribution and citation

## 🛠️ Technology Stack

- **LLM Model**: Google Gemma-3-27B-IT
- **Vector Database**: ChromaDB / Pinecone (TBD)
- **Document Processing**: PyPDF2, python-docx, Unstructured
- **Embeddings**: sentence-transformers
- **Framework**: Python with FastAPI/Streamlit for UI
- **Storage**: SQLite for metadata, Vector DB for embeddings

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

1. **Model Setup**:
```bash
python src/models/setup_gemma.py
```

2. **Initialize Memory System**:
```bash
python src/memory/initialize.py
```

3. **Start the Playground**:
```bash
python src/main.py
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
