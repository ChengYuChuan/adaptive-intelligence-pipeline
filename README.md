# Adaptive Intelligence Pipeline (AIP)

A production-ready, switchable-component AI information integration system supporting multiple LLM services, data sources, and output formats.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Project Features

### 🔌 Switchable Components
- **LLM Services**: 
  - ✅ Claude API (Development & Demo)
  - ✅ AWS Bedrock (Enterprise Production)
  - 🔄 Azure OpenAI (Week 4)
  - 📅 SageMaker (Week 4)
  
- **Data Sources**: 
  - ✅ arXiv (Academic Papers)
  - ✅ NewsAPI (Financial News)
  - 📅 Internal Database (Week 3)
  
- **Output Formats**: 
  - ✅ Console (Development)
  - ✅ Notion (Knowledge Management)
  - ✅ Email (Automated Delivery)
  - 🔄 Slack (Week 2+)

### 🎯 Real-World Use Cases
1. **Academic Research Tracking**: Daily digest of ML/AI papers from arXiv
2. **Investment Analysis**: Real-time semiconductor industry news monitoring
3. **Enterprise Intelligence**: Automated weekly reports delivered via email

---

## 🏗️ Architecture Design

```
                    User Request
                         ↓
                    FastAPI API
                         ↓
                 PipelineService
                  (Orchestrator)
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   LLM Adapter     Source Adapter    Output Adapter
        │                │                │
   ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
   │ Claude  │      │  arXiv  │      │ Console │
   │ Bedrock │      │ NewsAPI │      │  Notion │
   │  Azure  │      │Internal │      │  Email  │
   └─────────┘      └─────────┘      └─────────┘
   
   All adapters implement abstract interfaces → Hot-swappable via .env
```

**Design Principles**:
- **Dependency Inversion**: All adapters implement abstract base classes
- **Factory Pattern**: Runtime selection based on configuration
- **Single Responsibility**: Each adapter handles one specific task
- **Open/Closed**: Easy to extend without modifying existing code

---

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/ChengYuChuan/adaptive-intelligence-pipeline.git
cd adaptive-intelligence-pipeline

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
```

**Minimum Configuration (Week 1)**:
```env
# LLM Provider
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Data Source
SOURCE_PROVIDER=arxiv

# Output
OUTPUT_PROVIDER=console
```

**Full Configuration (Week 2)**:
```env
# LLM Provider
LLM_PROVIDER=bedrock
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Data Source
SOURCE_PROVIDER=newsapi
NEWSAPI_KEY=your-newsapi-key

# Output
OUTPUT_PROVIDER=email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-digit-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
```

### 3. Run Service

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API documentation will be available at: http://localhost:8000/docs

### 4. Test the Pipeline

**Option A: Using cURL**
```bash
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "template": "academic",
    "max_results": 5,
    "date_range": "last_week"
  }'
```

**Option B: Using Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/pipeline/run",
    json={
        "query": "TSMC OR NVIDIA",
        "template": "financial",
        "max_results": 10,
        "date_range": "today"
    }
)

print(response.json())
```

---

## 📦 Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

---

## 🔧 Configuration Examples

### Example 1: Academic Research (arXiv → Claude → Notion)

```env
LLM_PROVIDER=claude
SOURCE_PROVIDER=arxiv
OUTPUT_PROVIDER=notion

ANTHROPIC_API_KEY=your-key
NOTION_API_KEY=your-notion-key
NOTION_DATABASE_ID=your-database-id
```

**API Request**:
```json
{
  "query": "transformer OR attention mechanism",
  "template": "academic",
  "max_results": 10,
  "date_range": "last_week",
  "output_title": "Weekly ML Research Digest"
}
```

---

### Example 2: Investment Analysis (NewsAPI → Bedrock → Email)

```env
LLM_PROVIDER=bedrock
SOURCE_PROVIDER=newsapi
OUTPUT_PROVIDER=email

AWS_REGION=us-west-2
NEWSAPI_KEY=your-key
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
EMAIL_TO=investor@example.com
```

**API Request**:
```json
{
  "query": "TSMC OR NVIDIA OR ASML",
  "template": "financial",
  "max_results": 20,
  "date_range": "today",
  "output_title": "Daily Semiconductor Industry Report"
}
```

---

### Example 3: Multi-Provider Comparison

Test different LLM providers on the same data:

```bash
# Test with Claude API
LLM_PROVIDER=claude python test_pipeline.py

# Test with AWS Bedrock
LLM_PROVIDER=bedrock python test_pipeline.py
```

---

## 📊 API Endpoints

### `GET /health`
Health check and current configuration

**Response**:
```json
{
  "status": "healthy",
  "providers": {
    "llm": "AWS Bedrock",
    "source": "NewsAPI",
    "output": "Email"
  },
  "timestamp": "2024-01-15T10:00:00"
}
```

### `POST /pipeline/run`
Execute complete data processing pipeline

**Request Body**:
```json
{
  "query": "string",              // Search keywords
  "template": "academic|financial", // Report template
  "max_results": 10,              // Max items to fetch (1-50)
  "date_range": "last_week",      // Date filter
  "output_title": "string",       // Optional custom title
  "output_tags": ["tag1", "tag2"] // Optional tags
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Pipeline executed successfully",
  "data_fetched": 10,
  "report": "# Generated Report\n...",
  "output_url": "https://notion.so/...",
  "providers": {
    "llm": "AWS Bedrock",
    "source": "NewsAPI",
    "output": "Email"
  },
  "duration_seconds": 15.3
}
```

### `GET /config`
View current configuration (without sensitive data)

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **Validation**: Pydantic 2.10+
- **Async Runtime**: Uvicorn with asyncio

### LLM Integrations
- **Claude API**: anthropic 0.39+
- **AWS Bedrock**: boto3 1.35+
- **Azure OpenAI**: openai (Week 4)

### Data Sources
- **arXiv**: arxiv 2.1+
- **NewsAPI**: newsapi-python 0.2+
- **HTTP Client**: httpx 0.27+

### Output Integrations
- **Email**: aiosmtplib 3.0+
- **Notion**: httpx (REST API)
- **Slack**: (Week 2+)

### Development
- **Testing**: pytest 8.3+, pytest-asyncio 0.24+
- **Linting**: ruff, black, isort
- **Coverage**: pytest-cov 6.0+

---

## 📁 Project Structure

```
adaptive-intelligence-pipeline/
├── app/
│   ├── main.py                     # FastAPI application entry
│   ├── config.py                   # Environment configuration
│   │
│   ├── adapters/                   # 🔌 Switchable components
│   │   ├── llm/
│   │   │   ├── base.py            # Abstract interface
│   │   │   ├── claude_api.py      # ✅ Claude API
│   │   │   ├── bedrock.py         # ✅ AWS Bedrock
│   │   │   ├── azure_openai.py    # 📅 Azure (Week 4)
│   │   │   └── sagemaker.py       # 📅 SageMaker (Week 4)
│   │   │
│   │   ├── source/
│   │   │   ├── base.py
│   │   │   ├── arxiv.py           # ✅ Academic papers
│   │   │   ├── newsapi.py         # ✅ Financial news
│   │   │   └── internal_db.py     # 📅 Week 3
│   │   │
│   │   └── output/
│   │       ├── base.py
│   │       ├── console.py         # ✅ Development
│   │       ├── notion.py          # ✅ Knowledge base
│   │       ├── email.py           # ✅ Email delivery
│   │       └── slack.py           # 🔄 Week 2+
│   │
│   ├── services/                   # Business logic
│   │   └── pipeline.py            # Orchestration
│   │
│   ├── schemas/                    # Pydantic models
│   │   └── pipeline.py
│   │
│   └── prompts/                    # LLM prompt templates
│       ├── academic_summary.py
│       └── financial_analysis.py
│
├── tests/
│   ├── test_api.py
│   ├── test_llm_adapters.py
│   ├── test_source_adapters.py
│   └── test_output_adapters.py
│
├── docs/
│   ├── architecture.md
│   ├── QUICKSTART.md
│   └── GITHUB_SETUP.md
│
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI/CD pipeline
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔐 Security & Privacy Considerations

### Development vs Production

| Aspect | Development (Claude API) | Production (AWS Bedrock) |
|--------|-------------------------|--------------------------|
| Data Location | Anthropic servers | Your AWS account |
| Data Retention | Per Anthropic policy | Under your control |
| Compliance | Standard | HIPAA, SOC 2, etc. available |
| Audit Logs | Limited | Full CloudTrail logging |
| Rate Limits | Per API tier | Pay-as-you-go |
| Cost | Per token | Per token (enterprise pricing) |

### API Key Management

**✅ DO**:
- Use environment variables (`.env` file)
- Never commit API keys to Git
- Use AWS Secrets Manager in production
- Rotate credentials regularly
- Use IAM roles instead of access keys when possible

**❌ DON'T**:
- Hardcode API keys in source code
- Share API keys via email/chat
- Use personal API keys in production
- Commit `.env` file to version control

### Gmail App Password Setup

For Email output adapter:
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Copy the 16-digit password
5. Use this password (not your regular password) in `SMTP_PASSWORD`

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_llm_adapters.py -v

# Source adapters
pytest tests/test_source_adapters.py -v

# Output adapters
pytest tests/test_output_adapters.py -v

# Integration tests (requires API keys)
pytest tests/ -v -m integration
```

### Test Individual Components

**Test NewsAPI Adapter**:
```python
python -m pytest tests/test_source_adapters.py::TestNewsAPIAdapter -v
```

**Test AWS Bedrock**:
```python
python -m pytest tests/test_llm_adapters.py::TestBedrockAdapter -v
```

**Test Email Output**:
```python
python -m pytest tests/test_output_adapters.py::TestEmailAdapter -v
```

---

## 🔄 Adding New Adapters

### Example: Adding a New LLM Provider

**Step 1**: Create adapter implementation
```python
# app/adapters/llm/your_provider.py
from app.adapters.llm.base import BaseLLMAdapter

class YourProviderAdapter(BaseLLMAdapter):
    async def summarize(self, text: str) -> str:
        # Implementation
        pass
    
    # Implement all other required methods...
    
    def get_provider_name(self) -> str:
        return "YourProvider"
```

**Step 2**: Register in factory
```python
# app/adapters/llm/__init__.py
def get_llm_adapter() -> BaseLLMAdapter:
    if provider == "your_provider":
        from app.adapters.llm.your_provider import YourProviderAdapter
        return YourProviderAdapter()
```

**Step 3**: Add configuration
```python
# app/config.py
class Settings(BaseSettings):
    LLM_PROVIDER: Literal["claude", "bedrock", "your_provider"]
    YOUR_PROVIDER_API_KEY: str = ""
```

**Step 4**: Update `.env.example`
```env
# Your Provider
YOUR_PROVIDER_API_KEY=your-key-here
```

---

## 📈 Performance Metrics

Expected performance (varies by provider and content):

| Stage | Time | Notes |
|-------|------|-------|
| Data Fetch (arXiv) | 1-3s | Depends on result count |
| Data Fetch (NewsAPI) | 2-4s | API rate limits apply |
| LLM Analysis (Claude) | 5-15s | Depends on content length |
| LLM Analysis (Bedrock) | 5-15s | Similar to Claude |
| Output (Console) | <1s | Instant |
| Output (Email) | 1-3s | SMTP latency |
| Output (Notion) | 2-4s | API latency |
| **Total Pipeline** | **10-30s** | End-to-end |

---

## 🐛 Troubleshooting

### Common Issues

**1. `ModuleNotFoundError: No module named 'anthropic'`**
```bash
pip install -r requirements.txt
```

**2. `ValueError: ANTHROPIC_API_KEY not configured`**
- Check `.env` file exists
- Verify API key is correctly set
- Restart the application

**3. NewsAPI returns empty results**
- Check date range (free tier: last 30 days only)
- Verify query syntax
- Check API quota (100 requests/day for free tier)

**4. AWS Bedrock access denied**
- Enable model access in AWS Console
- Verify IAM permissions
- Check AWS credentials configuration

**5. Email sending fails**
- For Gmail: Use App Password, not regular password
- Check firewall/network allows SMTP ports
- Verify SMTP credentials are correct

### Debug Mode

Enable detailed logging:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## 📝 Development Roadmap

- [x] **Week 1**: Core architecture + Claude API
  - [x] FastAPI backend
  - [x] Adapter pattern implementation
  - [x] arXiv source adapter
  - [x] Console & Notion output
  - [x] Complete pipeline

- [x] **Week 2**: Enterprise adapters
  - [x] NewsAPI source adapter
  - [x] AWS Bedrock LLM adapter
  - [x] Email output adapter
  - [ ] Slack output adapter (in progress)

- [ ] **Week 3**: Automation & scaling
  - [ ] n8n/Airflow integration
  - [ ] Redis caching
  - [ ] Database storage
  - [ ] Monitoring & metrics

- [ ] **Week 4**: Advanced features
  - [ ] Azure OpenAI adapter
  - [ ] SageMaker custom models
  - [ ] Advanced analytics
  - [ ] Web dashboard

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Scientific Computing Graduate, Heidelberg University**
- Specialization: Machine Learning & Generative AI
- LinkedIn: [Yu-Chuan (Louis) Cheng](https://www.linkedin.com/in/yu-chuan-cheng-496069bb/)
- GitHub: [@ChengYuChuan](https://github.com/ChengYuChuan)

---

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude API
- [AWS](https://aws.amazon.com/bedrock/) for Bedrock platform
- [arXiv](https://arxiv.org/) for academic paper API
- [NewsAPI](https://newsapi.org/) for news data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework

---

## 📚 Additional Resources

### External Resources
- [Claude API Documentation](https://docs.anthropic.com/)
- [AWS Bedrock Guide](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Adapter Pattern Explained](https://refactoring.guru/design-patterns/adapter)

---

## 💡 Example Use Cases

### Use Case 1: Daily ML Research Digest
```bash
# Setup cron job for daily execution
0 9 * * * cd /path/to/project && python daily_research.py
```

### Use Case 2: Real-time Market Monitoring
```python
# Monitor specific stocks with custom frequency
COMPANIES = ["TSMC", "NVIDIA", "ASML"]
for company in COMPANIES:
    response = pipeline.run(
        query=company,
        template="financial",
        date_range="today"
    )
```

### Use Case 3: Enterprise Report Automation
```yaml
# n8n workflow (Week 3)
schedule: "0 8 * * 1"  # Every Monday 8 AM
source: newsapi
llm: bedrock
output: email
recipients: ["team@company.com"]
```

---

## ⚡ Quick Reference

### Switching Providers

**Change LLM Provider**:
```bash
# Option 1: Edit .env
LLM_PROVIDER=bedrock

# Option 2: Environment variable
export LLM_PROVIDER=bedrock
uvicorn app.main:app --reload
```

**Change Data Source**:
```bash
SOURCE_PROVIDER=newsapi  # or arxiv
```

**Change Output**:
```bash
OUTPUT_PROVIDER=email  # or console, notion, slack
```

### Health Check
```bash
curl http://localhost:8000/health | jq
```

### Test Specific Configuration
```bash
# Test with specific providers
curl -X POST http://localhost:8000/pipeline/run \
  -H "Content-Type: application/json" \
  -d @test_config.json
```

---

**Built with ❤️ for intelligent automation**
