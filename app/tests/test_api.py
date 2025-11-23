import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root path"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "Adaptive Intelligence Pipeline"


def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "providers" in data
    assert "llm" in data["providers"]
    assert "source" in data["providers"]
    assert "output" in data["providers"]


def test_get_config():
    """Test get configuration"""
    response = client.get("/config")
    assert response.status_code == 200
    data = response.json()
    assert "llm_provider" in data
    assert "source_provider" in data
    assert "output_provider" in data


def test_openapi_docs():
    """Test OpenAPI documentation"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_pipeline_validation():
    """Test pipeline request validation"""
    # Missing required fields
    response = client.post("/pipeline/run", json={})
    assert response.status_code == 422  # Validation error
    
    # Invalid template
    response = client.post("/pipeline/run", json={
        "query": "test",
        "template": "invalid_template"
    })
    assert response.status_code == 422


@pytest.mark.skip(reason="Requires actual API keys, only run when configured")
def test_pipeline_run():
    """Test complete pipeline (requires actual API keys)"""
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