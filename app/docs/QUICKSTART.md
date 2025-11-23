# 快速開始指南

## 第一次使用

### 1. 安裝依賴

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安裝套件
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
# 複製範例檔案
cp .env.example .env

# 編輯 .env，至少設定：
# ANTHROPIC_API_KEY=你的_claude_api_key
```

### 3. 啟動服務

```bash
# 開發模式（自動重載）
uvicorn app.main:app --reload

# 或使用 Python 直接執行
python -m app.main
```

服務會在 http://localhost:8000 啟動

### 4. 測試 API

打開瀏覽器訪問：
- API 文件：http://localhost:8000/docs
- 健康檢查：http://localhost:8000/health

或使用 curl：

```bash
# 健康檢查
curl http://localhost:8000/health

# 執行 pipeline（學術場景）
curl -X POST "http://localhost:8000/pipeline/run" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "template": "academic",
    "max_results": 5,
    "date_range": "last_week"
  }'
```

---

## 使用 Docker

```bash
# 建立並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止
docker-compose down
```

---

## 切換 Provider

只需修改 `.env` 檔案：

```env
# 改用 AWS Bedrock
LLM_PROVIDER=bedrock

# 改用 NewsAPI
SOURCE_PROVIDER=newsapi

# 改輸出到 Notion
OUTPUT_PROVIDER=notion
```

重啟服務後生效。

---

## 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/test_api.py

# 顯示覆蓋率
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 常見問題

### Q: 為什麼 pipeline 失敗？
A: 檢查：
1. `.env` 是否正確設定 API keys
2. 網路連線是否正常
3. 查看詳細錯誤訊息

### Q: 如何加入新的 LLM provider？
A: 參考 `app/adapters/llm/claude_api.py`，實作 `BaseLLMAdapter` 介面

### Q: 如何客製化 prompt？
A: 修改 `app/adapters/llm/claude_api.py` 中的 system_prompt

---

## 下一步

- 閱讀 [架構文件](docs/architecture.md)
- 查看 [部署指南](docs/deployment_guide.md)
- 探索 Week 2 的擴充功能
