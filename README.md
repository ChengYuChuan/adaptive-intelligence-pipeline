# Adaptive Intelligence Pipeline (AIP)

A switchable-component AI information integration system supporting multiple LLM services, data sources, and output formats.

## 🎯 Project Features

- **Switchable LLM Services**: Claude API → AWS Bedrock → Azure OpenAI → Custom Model
- **Switchable Data Sources**: arXiv, News API, Internal Database
- **Switchable Output Formats**: Email, Notion, Slack, PDF
- **Dual Scenarios**: Academic Paper Tracking + Financial Investment Analysis

## 🏗️ Architecture Design

```
n8n/Airflow (Scheduling)
        ↓
    FastAPI
        ↓
┌───────┴────────┐
│  Adapters      │ ← Hot-pluggable
│  - LLM         │
│  - Source      │
│  - Output      │
└────────────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/adaptive-intelligence-pipeline.git
cd adaptive-intelligence-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# LLM Settings
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here

# Data Source
SOURCE_PROVIDER=arxiv

# Output Settings
OUTPUT_PROVIDER=console
```

### 3. Run Service

```bash
# Development mode
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API documentation will be available at: http://localhost:8000/docs

### 4. Test Pipeline

```bash
# Run tests
pytest

# Test specific scenario
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "template": "academic",
    "date_range": "last_week"
  }'
```

## 📦 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## 🔌 Switching LLM Provider

Simply modify the `.env` file:

```env
# Use Claude API (Development/Demo)
LLM_PROVIDER=claude

# Use AWS Bedrock (Enterprise-grade)
LLM_PROVIDER=bedrock
AWS_REGION=us-west-2

# Use Azure OpenAI (Enterprise-grade)
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key

# Use your own model (SageMaker)
LLM_PROVIDER=sagemaker
SAGEMAKER_ENDPOINT=your_endpoint_name
```

## 📊 Use Cases

### Scenario 1: Academic Paper Tracking

Daily aggregation of new ML/Math papers from arXiv, generating summary reports.

```python
POST /pipeline/run
{
  "query": "diffusion models OR transformers",
  "template": "academic",
  "date_range": "yesterday"
}
```

### Scenario 2: Investment News Analysis

Track specific company news, analyze sentiment and industry chain impacts.

```python
POST /pipeline/run
{
  "query": "TSMC OR NVIDIA OR ASML",
  "template": "financial",
  "date_range": "today"
}
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Pydantic
- **LLM**: Anthropic Claude, AWS Bedrock, Azure OpenAI
- **Data Sources**: arXiv API, NewsAPI
- **Output**: Notion API, Email (SMTP), Slack
- **Testing**: pytest
- **Deployment**: Docker, GitHub Actions

## 📁 Project Structure

```
adaptive-intelligence-pipeline/
├── app/
│   ├── main.py                 # FastAPI main application
│   ├── config.py               # Environment settings
│   ├── adapters/               # Switchable components
│   │   ├── llm/               # LLM service adapters
│   │   ├── source/            # Data source adapters
│   │   └── output/            # Output adapters
│   ├── services/              # Business logic
│   ├── schemas/               # Data models
│   └── tests/                 # Tests
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔐 Data Security Considerations

- **Development Phase**: Using Claude API (data goes to Anthropic)
- **Enterprise Deployment**:
  - Option 1: AWS Bedrock / Azure OpenAI (Enterprise contract, data isolation)
  - Option 2: Deploy your own model on SageMaker (Full control)

## 📝 Development Progress

- [x] Week 1: Basic architecture + Claude API
- [ ] Week 2: More Adapters (Bedrock, NewsAPI)
- [ ] Week 3: Automated scheduling + Deployment
- [ ] Week 4: Advanced features (Azure, SageMaker)

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 👤 Author

Scientific Computing Graduate, Heidelberg University

Specializing in Machine Learning and Generative AI