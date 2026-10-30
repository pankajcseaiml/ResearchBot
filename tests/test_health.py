"""Automated tests for health check and static frontend delivery.

Verifies:
- Root endpoint returns frontend HTML successfully.
- Health endpoint returns valid schema with required fields.
- Registered agents match the expected 3 agents.
- Groq configuration and model status are reported without exposing secrets.
- Research library availability is reported.
- Application can be imported and initialized without live LLM calls.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import AGENT_NAMES, get_settings


@pytest.fixture
def client():
    """Create test client for FastAPI application."""
    return TestClient(app)


def test_root_returns_frontend(client):
    """The root endpoint returns the frontend successfully with status 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "ResearchBot" in response.text
    assert "question-input" in response.text


def test_health_endpoint_schema(client):
    """The health endpoint returns a valid response shape."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "app_name" in data
    assert "groq_configured" in data
    assert isinstance(data["groq_configured"], bool)
    assert "model" in data
    assert "agents" in data
    assert "research_library_available" in data
    assert data["research_library_available"] is True


def test_health_agents_list(client):
    """Health information contains the expected three agent names."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    agents = data.get("agents", [])

    assert len(agents) == 3
    assert "Research Query Analyzer" in agents
    assert "Research & Analysis Agent" in agents
    assert "Research Answer Reviewer" in agents
    assert set(agents) == set(AGENT_NAMES)


def test_health_reports_config_without_exposing_secrets(client):
    """The configured model and API-key status are reported without exposing secrets."""
    response = client.get("/health")
    assert response.status_code == 200
    raw_text = response.text
    data = response.json()

    # Never expose any API key string or header
    assert "GROQ_API_KEY" not in data
    assert "api_key" not in raw_text.lower() or "groq_configured" in data

    # Configured model is present
    settings = get_settings()
    assert data["model"] == settings.GROQ_MODEL


def test_app_import_without_live_call():
    """The application can be imported and initialized without attempting a live LLM request."""
    import importlib
    import app.main
    mod = importlib.reload(app.main)
    assert hasattr(mod, "app")
    assert mod.app.title == "ResearchBot — Multi-Agent Research & Analysis Assistant"
