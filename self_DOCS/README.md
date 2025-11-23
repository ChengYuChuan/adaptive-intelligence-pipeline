# Adaptive Intelligence Pipeline (AIP)

一個可抽換元件的 AI 資訊整合系統，支援多種 LLM 服務、資料來源和輸出格式。

## 🎯 專案特色

- **LLM 服務可抽換**：Claude API → AWS Bedrock → Azure OpenAI → 自訂模型
- **資料來源可抽換**：arXiv、新聞 API、內部資料庫
- **輸出格式可抽換**：Email、Notion、Slack、PDF
- **雙場景應用**：學術論文追蹤 + 金融投資分析

## 🏗️ 架構設計

```
n8n/Airflow (排程)
        ↓
    FastAPI
        ↓
┌───────┴────────┐
│  Adapters      │ ← 可熱插拔
│  - LLM         │
│  - Source      │
│  - Output      │
└────────────────┘
```

## 🚀 快速開始

### 1. 環境設置

```bash
# Clone 專案
git clone https://github.com/你的用戶名/adaptive-intelligence-pipeline.git
cd adaptive-intelligence-pipeline

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 環境變數設定

複製 `.env.example` 到 `.env` 並填入你的 API keys：

```bash
cp .env.example .env
```

編輯 `.env`：

```env
# LLM 設定
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here

# 資料來源
SOURCE_PROVIDER=arxiv

# 輸出設定
OUTPUT_PROVIDER=notion
NOTION_API_KEY=your_key_here
NOTION_DATABASE_ID=your_database_id
```

### 3. 運行服務

```bash
# 開發模式
uvicorn app.main:app --reload

# 生產模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API 文件會在：http://localhost:8000/docs

### 4. 測試 Pipeline

```bash
# 運行測試
pytest tests/

# 測試單個場景
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "template": "academic",
    "date_range": "last_week"
  }'
```

## 📦 Docker 部署

```bash
# 建立並運行
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

## 🔌 切換 LLM Provider

只需修改 `.env` 檔案：

```env
# 使用 Claude API（開發/Demo）
LLM_PROVIDER=claude

# 使用 AWS Bedrock（企業級）
LLM_PROVIDER=bedrock
AWS_REGION=us-west-2

# 使用 Azure OpenAI（企業級）
LLM_PROVIDER=azure
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_KEY=your_key

# 使用自己的模型（SageMaker）
LLM_PROVIDER=sagemaker
SAGEMAKER_ENDPOINT=your_endpoint_name
```

## 📊 使用場景

### 場景 1：學術論文追蹤

每日自動彙整 arXiv 上的 ML/數學領域新論文，生成摘要報告。

```python
POST /pipeline/run
{
  "query": "diffusion models OR transformers",
  "template": "academic",
  "date_range": "yesterday"
}
```

### 場景 2：投資新聞分析

追蹤特定公司新聞，分析情緒和產業鏈影響。

```python
POST /pipeline/run
{
  "query": "TSMC OR NVIDIA OR ASML",
  "template": "financial",
  "date_range": "today"
}
```

## 🛠️ 技術棧

- **Backend**: FastAPI, Pydantic
- **LLM**: Anthropic Claude, AWS Bedrock, Azure OpenAI
- **資料來源**: arXiv API, NewsAPI
- **輸出**: Notion API, Email (SMTP), Slack
- **測試**: pytest
- **部署**: Docker, GitHub Actions

## 📁 專案結構

```
adaptive-intelligence-pipeline/
├── app/
│   ├── main.py                 # FastAPI 主程式
│   ├── config.py               # 環境設定
│   ├── adapters/               # 可抽換元件
│   │   ├── llm/               # LLM 服務 adapters
│   │   ├── source/            # 資料來源 adapters
│   │   └── output/            # 輸出 adapters
│   ├── services/              # 業務邏輯
│   ├── schemas/               # 資料模型
│   └── prompts/               # Prompt 模板
├── tests/                     # 測試
├── workflows/                 # n8n workflows
├── docs/                      # 文件
└── docker-compose.yml
```

## 🔐 資料安全考量

- **開發階段**：使用 Claude API（資料會傳到 Anthropic）
- **企業部署**：
  - 選項 1: AWS Bedrock / Azure OpenAI（企業合約、資料隔離）
  - 選項 2: 自己在 SageMaker 部署模型（完全掌控）

## 📝 開發進度

- [x] 週 1：基礎架構 + Claude API
- [ ] 週 2：擴充更多 Adapters（Bedrock, NewsAPI）
- [ ] 週 3：自動化排程 + 部署
- [ ] 週 4：進階功能（Azure, SageMaker）

## 🤝 貢獻

歡迎 Issue 和 Pull Request！

## 📄 授權

MIT License

## 👤 作者

[你的名字] - Scientific Computing, Heidelberg University

專攻機器學習與生成式 AI
