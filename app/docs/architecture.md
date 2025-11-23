# 架構文件

## 系統概覽

Adaptive Intelligence Pipeline (AIP) 採用**適配器模式（Adapter Pattern）**設計，讓每個元件都可以獨立抽換，而不影響其他部分。

```
使用者請求
    ↓
FastAPI (main.py)
    ↓
PipelineService (協調層)
    ↓
┌───────────┬───────────┬───────────┐
│    LLM    │  Source   │  Output   │
│  Adapter  │  Adapter  │  Adapter  │
└─────┬─────┴─────┬─────┴─────┬─────┘
      │           │           │
    Claude      arXiv      Console
   Bedrock    NewsAPI     Notion
    Azure     Internal    Email
  SageMaker              Slack
```

---

## 核心設計原則

### 1. 依賴反轉原則 (DIP)

所有 adapter 都實作抽象介面，不依賴具體實作：

```python
# 定義介面
class BaseLLMAdapter(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass

# 具體實作
class ClaudeAPIAdapter(BaseLLMAdapter):
    async def summarize(self, text: str) -> str:
        # 實際呼叫 Claude API
        ...
```

### 2. 工廠模式

透過工廠函數根據設定選擇實作：

```python
def get_llm_adapter() -> BaseLLMAdapter:
    if settings.LLM_PROVIDER == "claude":
        return ClaudeAPIAdapter()
    elif settings.LLM_PROVIDER == "bedrock":
        return AWSBedrockAdapter()
    # ...
```

### 3. 單一職責原則 (SRP)

每個 adapter 只負責一件事：
- LLM Adapter: 呼叫 LLM 服務
- Source Adapter: 獲取資料
- Output Adapter: 輸出結果

---

## 目錄結構解析

```
app/
├── main.py              # FastAPI 應用程式入口
│                        # 定義 API 端點、middleware、事件處理
│
├── config.py            # 環境設定
│                        # 使用 Pydantic Settings 管理所有設定
│
├── adapters/            # 適配器層（可抽換的元件）
│   ├── llm/            # LLM 服務適配器
│   │   ├── base.py     # 抽象介面
│   │   ├── __init__.py # 工廠函數
│   │   └── claude_api.py
│   │
│   ├── source/         # 資料來源適配器
│   │   ├── base.py
│   │   ├── __init__.py
│   │   └── arxiv.py
│   │
│   └── output/         # 輸出適配器
│       ├── base.py
│       ├── __init__.py
│       ├── console.py
│       └── notion.py
│
├── services/           # 業務邏輯層
│   └── pipeline.py     # 協調各個 adapter 完成完整流程
│
└── schemas/            # 資料模型（Pydantic）
    └── pipeline.py     # API 請求/回應的資料結構
```

---

## 資料流程

### 完整 Pipeline 流程

```
1. 使用者發送 POST /pipeline/run
   ↓
2. FastAPI 驗證請求 (Pydantic)
   ↓
3. PipelineService.run()
   ├─ 3.1 SourceAdapter.fetch()     → 獲取原始資料
   ├─ 3.2 LLMAdapter.generate_report() → 分析並生成報告
   └─ 3.3 OutputAdapter.send()      → 發送到目標
   ↓
4. 返回結果給使用者
```

### 錯誤處理

每個階段都有錯誤處理：

```python
try:
    raw_data = await source.fetch(...)
except Exception as e:
    # 記錄錯誤並返回失敗狀態
    logger.error(f"Source fetch failed: {e}")
    return PipelineResponse(status="failed", ...)
```

---

## 擴展指南

### 如何加入新的 LLM Provider

1. 建立新檔案 `app/adapters/llm/your_provider.py`

```python
from app.adapters.llm.base import BaseLLMAdapter

class YourProviderAdapter(BaseLLMAdapter):
    def __init__(self):
        # 初始化你的 client
        self.client = YourClient(api_key=settings.YOUR_API_KEY)
    
    async def summarize(self, text: str) -> str:
        # 實作摘要邏輯
        response = await self.client.summarize(text)
        return response.text
    
    # ... 實作其他必要方法
```

2. 在 `app/adapters/llm/__init__.py` 加入：

```python
elif provider == "your_provider":
    return YourProviderAdapter()
```

3. 在 `app/config.py` 加入設定：

```python
YOUR_PROVIDER_API_KEY: str = ""
```

4. 更新 `.env.example`

### 如何加入新的資料來源

流程類似，實作 `BaseSourceAdapter` 介面。

### 如何加入新的輸出目標

流程類似，實作 `BaseOutputAdapter` 介面。

---

## 安全考量

### API Keys 管理

- ✅ 使用 `.env` 檔案管理 (不 commit 到 git)
- ✅ Pydantic Settings 驗證
- ✅ Docker secrets (生產環境)

### 資料隱私

- **開發環境**: 使用公開 API (Claude, OpenAI)
- **企業環境**: 使用 Bedrock/Azure (企業合約)
- **高安全性**: 自己部署模型 (SageMaker)

### Rate Limiting

TODO: Week 3 加入 rate limiting middleware

---

## 效能優化

### 非同步處理

所有 I/O 操作都使用 `async/await`：

```python
async def fetch(self, query: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

### 快取策略

TODO: Week 3 加入 Redis 快取

### 批次處理

TODO: Week 3 支援批次請求

---

## 測試策略

### 單元測試

測試每個 adapter 的獨立功能：

```python
@pytest.mark.asyncio
async def test_claude_summarize(mock_client):
    adapter = ClaudeAPIAdapter()
    result = await adapter.summarize("text")
    assert isinstance(result, str)
```

### 整合測試

測試完整 pipeline：

```python
def test_full_pipeline():
    response = client.post("/pipeline/run", json={...})
    assert response.status_code == 200
```

### Mock 策略

使用 `unittest.mock` 模擬外部 API：

```python
@patch('app.adapters.llm.claude_api.anthropic.Anthropic')
def test_with_mock(mock_anthropic):
    # 設定 mock 行為
    mock_anthropic.return_value.messages.create.return_value = ...
```

---

## 部署架構

### 開發環境

```
本地 (localhost:8000)
└── uvicorn --reload
```

### 生產環境

```
                    ┌─────────────┐
                    │   Nginx     │ (反向代理、SSL)
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │  Uvicorn    │ (多 worker)
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
     AWS Bedrock      arXiv API      Notion API
```

詳見 [部署指南](deployment_guide.md)

---

## 效能指標

預期效能（取決於 LLM provider）：

- **資料獲取**: 1-3 秒
- **LLM 分析**: 5-15 秒
- **輸出**: 1-2 秒
- **總計**: 約 10-20 秒 per request

---

## 後續規劃

- **Week 2**: 加入更多 adapters (Bedrock, NewsAPI, Email)
- **Week 3**: 排程系統、快取、監控
- **Week 4**: 進階功能、效能優化
