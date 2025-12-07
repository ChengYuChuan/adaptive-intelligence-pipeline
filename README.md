# Adaptive Intelligence Pipeline (AIP)

A production-ready, switchable-component AI information integration system with **RAG (Retrieval-Augmented Generation)** capabilities for enterprise document Q&A.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Project Overview

AIP is designed to solve two core enterprise needs:

1. **Information Integration Pipeline**: Aggregate data from multiple sources (arXiv, NewsAPI), analyze with LLM, and deliver reports to various destinations (Email, Notion, Slack)

2. **Enterprise Document Q&A (RAG)**: Upload internal documents and ask questions with source citations - perfect for company policies, technical docs, and knowledge bases

### Key Features

| Feature | Description |
|---------|-------------|
| 🔌 **Switchable Components** | Swap LLM/Source/Output providers via environment variables |
| 🔍 **RAG System** | Upload documents, ask questions, get answers with citations |
| 🏢 **Enterprise Ready** | AWS Bedrock & Azure support for data privacy |
| 📊 **Multi-format Support** | PDF, Word, Markdown document processing |

---

## 🏗️ Architecture
```
                         ┌─────────────────────────────────────┐
                         │            FastAPI                  │
                         │         (REST API Layer)            │
                         └───────────────┬─────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
     ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
     │    Pipeline     │      │   RAG Service   │      │    Document     │
     │    Service      │      │   (Q&A)         │      │   Processor     │
     └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
              │                        │                        │
              ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Adapter Layer                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │
│  │  LLM Adapter  │  │Source Adapter │  │Output Adapter │  │Vector Store   │ │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤  ├───────────────┤ │
│  │ • Claude API  │  │ • arXiv       │  │ • Console     │  │ • Chroma      │ │
│  │ • AWS Bedrock │  │ • NewsAPI     │  │ • Notion      │  │ • PgVector    │ │
│  │ • Azure OpenAI│  │ • Internal DB │  │ • Email       │  │ • Azure AI    │ │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘ │
│                                                                              │
│  ┌───────────────┐                                                          │
│  │   Embedding   │                                                          │
│  ├───────────────┤                                                          │
│  │ • OpenAI      │                                                          │
│  │ • Bedrock     │                                                          │
│  └───────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Dependency Inversion**: All adapters implement abstract interfaces
- **Factory Pattern**: Runtime provider selection via configuration
- **Single Responsibility**: Each adapter handles one specific task

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- API Keys: Anthropic (Claude) and/or OpenAI

### Installation
```bash
# Clone repository
git clone https://github.com/ChengYuChuan/adaptive-intelligence-pipeline.git
cd adaptive-intelligence-pipeline

# Install with uv (recommended)
uv sync

# Or with pip
pip install -r requirements.txt
```

### Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
```

**Minimum configuration:**
```env
# LLM
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# RAG (for document Q&A)
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
VECTORSTORE_PROVIDER=chroma
```

### Run the Server
```bash
# With uv
uv run uvicorn app.main:app --reload

# Or directly
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI.

---

## 📖 Usage Guide

### 1. Pipeline: Information Integration

Fetch data from sources, analyze with LLM, and output reports.
```bash
# Academic paper tracking
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning transformers",
    "template": "academic",
    "max_results": 10,
    "date_range": "last_week"
  }'

# Financial news analysis
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "TSMC NVIDIA semiconductor",
    "template": "financial",
    "max_results": 20,
    "date_range": "today"
  }'
```

### 2. RAG: Document Q&A

Upload documents and ask questions with source citations.

#### Step 1: Upload Documents
```bash
# Upload a PDF
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@company_policy.pdf" \
  -F "tags=policy,hr" \
  -F "description=Employee handbook 2024" \
  -F "collection_name=default"

# Upload Markdown
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@technical_guide.md" \
  -F "tags=technical,engineering" \
  -F "collection_name=default"
```

#### Step 2: Ask Questions
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the remote work policy?",
    "collection_name": "default",
    "top_k": 5,
    "include_sources": true
  }'
```

**Response:**
```json
{
  "question": "What is the remote work policy?",
  "answer": "According to the Employee Handbook, employees may work remotely up to 3 days per week with manager approval...",
  "sources": [
    {
      "filename": "company_policy.pdf",
      "content_preview": "Remote Work Guidelines: Employees may...",
      "relevance_score": 0.89,
      "page_number": 15
    }
  ],
  "retrieval_time_ms": 150,
  "generation_time_ms": 2500
}
```

#### Step 3: Manage Collections
```bash
# List collections
curl http://localhost:8000/rag/collections

# Get collection stats
curl http://localhost:8000/rag/collections/default/stats

# Delete collection
curl -X DELETE http://localhost:8000/rag/collections/default
```

---

## 🔧 Configuration Reference

### Provider Options

| Category | Options | Default |
|----------|---------|---------|
| LLM | `claude`, `bedrock`, `azure` | `claude` |
| Source | `arxiv`, `newsapi`, `internal` | `arxiv` |
| Output | `console`, `notion`, `email`, `slack` | `console` |
| Vector Store | `chroma`, `pgvector`, `azure` | `chroma` |
| Embedding | `openai`, `bedrock`, `local` | `openai` |

### Full `.env` Example
```env
# ===== LLM Settings =====
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514

# AWS Bedrock (alternative)
# LLM_PROVIDER=bedrock
# AWS_REGION=us-west-2
# AWS_ACCESS_KEY_ID=xxxxx
# AWS_SECRET_ACCESS_KEY=xxxxx

# ===== Source Settings =====
SOURCE_PROVIDER=arxiv
NEWSAPI_KEY=xxxxx  # For financial analysis

# ===== Output Settings =====
OUTPUT_PROVIDER=console
# Email settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com

# ===== RAG Settings =====
VECTORSTORE_PROVIDER=chroma
CHROMA_PERSIST_DIR=./data/vectorstore

EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50

# ===== General =====
DEBUG=true
LOG_LEVEL=INFO
```

---

## 📊 API Endpoints

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check with provider info |
| GET | `/config` | Current configuration |

### Pipeline
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/pipeline/run` | Execute data pipeline |

### RAG
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload document for processing |
| POST | `/ask` | Ask question about documents |
| GET | `/rag/health` | RAG system health |
| GET | `/rag/collections` | List all collections |
| GET | `/rag/collections/{name}/stats` | Collection statistics |
| DELETE | `/rag/collections/{name}` | Delete collection |

---

## 📁 Project Structure
```
adaptive-intelligence-pipeline/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Environment settings
│   │
│   ├── adapters/                  # Switchable components
│   │   ├── llm/                   # LLM providers
│   │   │   ├── base.py
│   │   │   ├── claude_api.py      # ✅ Implemented
│   │   │   └── bedrock.py         # ✅ Implemented
│   │   │
│   │   ├── source/                # Data sources
│   │   │   ├── base.py
│   │   │   ├── arxiv.py           # ✅ Implemented
│   │   │   └── newsapi.py         # ✅ Implemented
│   │   │
│   │   ├── output/                # Output destinations
│   │   │   ├── base.py
│   │   │   ├── console.py         # ✅ Implemented
│   │   │   ├── notion.py          # ✅ Implemented
│   │   │   └── email.py           # ✅ Implemented
│   │   │
│   │   ├── vectorstore/           # Vector databases
│   │   │   ├── base.py
│   │   │   ├── chroma.py          # ✅ Implemented
│   │   │   └── pgvector.py        # 📅 Week 4
│   │   │
│   │   └── embedding/             # Embedding services
│   │       ├── base.py
│   │       └── openai.py          # ✅ Implemented
│   │
│   ├── services/                  # Business logic
│   │   ├── pipeline.py            # Data pipeline orchestration
│   │   ├── document_processor.py  # Document parsing & chunking
│   │   └── rag.py                 # RAG Q&A service
│   │
│   ├── schemas/                   # Pydantic models
│   │   ├── pipeline.py
│   │   ├── document.py
│   │   └── rag.py
│   │
│   └── prompts/                   # LLM prompt templates
│       ├── academic_summary.py
│       └── financial_analysis.py
│
├── data/
│   ├── documents/                 # Uploaded documents
│   └── vectorstore/               # Chroma persistence
│
├── tests/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## 🛠️ Tech Stack

### Core
- **Framework**: FastAPI 0.115+
- **Package Manager**: uv (recommended) / pip
- **Validation**: Pydantic 2.10+

### LLM & AI
- **Claude**: anthropic 0.39+
- **AWS Bedrock**: boto3 1.35+
- **OpenAI Embedding**: openai 1.12+

### RAG
- **Vector Store**: chromadb 0.4+
- **PDF Parsing**: PyMuPDF 1.23+
- **Word Parsing**: python-docx 1.1+
- **Tokenization**: tiktoken 0.5+

### Data Sources
- **arXiv**: arxiv 2.1+
- **News**: newsapi-python 0.2+

### Output
- **Email**: aiosmtplib 3.0+
- **HTTP Client**: httpx 0.27+

---

## 📈 Development Roadmap

### Completed

- [x] **Week 1**: Core Architecture
  - [x] FastAPI + Adapter Pattern
  - [x] Claude API LLM adapter
  - [x] arXiv source adapter
  - [x] Console & Notion output adapters

- [x] **Week 2**: Enterprise Adapters
  - [x] AWS Bedrock LLM adapter
  - [x] NewsAPI source adapter
  - [x] Email output adapter

- [x] **Week 3**: RAG System
  - [x] Chroma vector store adapter
  - [x] OpenAI embedding adapter
  - [x] Document processing (PDF/Word/Markdown)
  - [x] Question answering with citations
  - [x] Collection management APIs

### In Progress

- [ ] **Week 4**: Production Ready + Basic Monitoring
  - [ ] PostgreSQL + pgvector adapter (AWS RDS / Azure)
  - [ ] Bedrock Titan Embedding adapter
  - [ ] Structured logging (JSON format)
  - [ ] `/metrics` endpoint (Prometheus format)
  - [ ] Basic monitoring dashboard

### Planned

- [ ] **Week 5+**: Advanced Operations
  - [ ] Full Prometheus + Grafana deployment
  - [ ] Distributed tracing (OpenTelemetry)
  - [ ] Alert configuration
  - [ ] Cost monitoring dashboard
  - [ ] n8n/Airflow scheduling integration
  - [ ] Web dashboard UI

---

## 🔐 Security Considerations

### Data Privacy by Provider

| Provider | Data Location | Best For |
|----------|---------------|----------|
| Claude API | Anthropic servers | Development, demos |
| AWS Bedrock | Your AWS account | Enterprise, regulated industries |
| Azure OpenAI | Your Azure tenant | Enterprise, Azure ecosystem |

### API Key Security

- ✅ Use `.env` files (never commit to git)
- ✅ Use AWS Secrets Manager / Azure Key Vault in production
- ✅ Rotate credentials regularly
- ✅ Use IAM roles instead of access keys when possible

---

## 🧪 Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific tests
uv run pytest app/tests/test_rag.py -v
```

---

## 🐳 Docker Deployment
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Yu-Chuan (Louis) Cheng**
- MSc Scientific Computing, Heidelberg University
- Specialization: Machine Learning & Generative AI
- GitHub: [@ChengYuChuan](https://github.com/ChengYuChuan)
- LinkedIn: [Yu-Chuan Cheng](https://www.linkedin.com/in/yu-chuan-cheng-496069bb/)

---

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) - Claude API
- [OpenAI](https://openai.com/) - Embedding models
- [Chroma](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework