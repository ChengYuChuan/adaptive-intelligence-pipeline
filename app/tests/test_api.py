import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """測試根路徑"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Adaptive Intelligence Pipeline"


def test_health_check():
    """測試健康檢查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data
    assert "llm" in data["providers"]
    assert "source" in data["providers"]
    assert "output" in data["providers"]


def test_get_config():
    """測試取得設定"""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "source_provider" in data
    assert "output_provider" in data


def test_openapi_docs():
    """測試 OpenAPI 文件"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_pipeline_validation():
    """測試 pipeline 請求驗證"""
    # 缺少必要欄位
    response = client.post("/pipeline/run", json={})
    assert response.status_code == 422  # Validation error
    
    # 無效的 template
    response = client.post("/pipeline/run", json={
        "query": "test",
        "template": "invalid_template"
    })
    assert response.status_code == 422


@pytest.mark.skip(reason="需要實際的 API keys，在有設定時才執行")
def test_pipeline_run():
    """測試完整 pipeline（需要實際 API keys）"""
    response = client.post("/pipeline/run", json={
        "query": "machine learning",
        "template": "academic",
        "max_results": 2,
        "date_range": "last_week"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["success", "partial", "failed"]
    assert "data_fetched" in data
    assert "providers" in data
