"""Automated tests for request validation and error handling.

Verifies:
- Empty questions are rejected.
- Whitespace-only questions are rejected.
- Missing question fields are rejected.
- Questions exceeding the maximum permitted length are rejected.
- Valid questions pass request validation.
- Missing Groq configuration produces a controlled 503 error for /ask.
- Mocked timeouts and upstream failures produce safe, secret-free error responses.
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.schemas import AskRequest
from app.agents.research_team import ResearchTimeoutError, UpstreamServiceError
from app.config import get_settings


@pytest.fixture
def client():
    """Create test client for FastAPI application."""
    return TestClient(app)


def test_empty_question_rejected(client):
    """Empty questions are rejected with HTTP 422."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert "empty" in data["message"].lower() or "whitespace" in data["message"].lower()


def test_whitespace_only_question_rejected(client):
    """Whitespace-only questions are rejected with HTTP 422."""
    response = client.post("/ask", json={"question": "   \n\t  \r  "})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert "whitespace" in data["message"].lower() or "empty" in data["message"].lower()


def test_missing_question_field_rejected(client):
    """Missing question fields are rejected with HTTP 422."""
    response = client.post("/ask", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"


def test_exceeding_max_length_rejected(client):
    """Questions exceeding the maximum permitted length are rejected with HTTP 422."""
    settings = get_settings()
    excessive_length = settings.MAX_QUESTION_LENGTH + 50
    long_question = "A" * excessive_length

    response = client.post("/ask", json={"question": long_question})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert "exceeds" in data["message"].lower()


def test_valid_question_passes_schema_validation():
    """Valid questions pass Pydantic schema validation and are normalized."""
    raw_question = "  What is Retrieval-Augmented Generation?  \n"
    validated = AskRequest(question=raw_question)
    assert validated.question == "What is Retrieval-Augmented Generation?"


def test_missing_groq_configuration_produces_503(client, monkeypatch):
    """Missing Groq configuration produces a clear, controlled HTTP 503 error for /ask."""
    # Force settings to report unconfigured
    monkeypatch.setenv("GROQ_API_KEY", "")
    get_settings.cache_clear()

    response = client.post(
        "/ask",
        json={"question": "Explain the architecture of Retrieval-Augmented Generation."}
    )
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert "groq api key is not configured" in data["message"].lower()

    get_settings.cache_clear()


def test_mocked_timeout_returns_safe_504(client, monkeypatch):
    """Mocked timeouts produce a safe HTTP 504 error response without disclosing internals."""
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key_12345")
    get_settings.cache_clear()

    async def mock_timeout(*args, **kwargs):
        raise ResearchTimeoutError("Research workflow timed out after 60 seconds.")

    with patch("app.main.run_research_workflow", new=mock_timeout):
        response = client.post(
            "/ask",
            json={"question": "Explain the architecture of Retrieval-Augmented Generation."}
        )
        assert response.status_code == 504
        data = response.json()
        assert data["status"] == "error"
        assert "timed out" in data["message"].lower()
        # Verify no traceback is in response
        assert "traceback" not in response.text.lower()

    get_settings.cache_clear()


def test_mocked_upstream_failure_returns_safe_502(client, monkeypatch):
    """Mocked upstream model failures produce safe HTTP 502 error responses."""
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_mock_key_12345")
    get_settings.cache_clear()

    async def mock_upstream_err(*args, **kwargs):
        raise UpstreamServiceError("Groq API rate limit exceeded. Please retry after a brief pause.")

    with patch("app.main.run_research_workflow", new=mock_upstream_err):
        response = client.post(
            "/ask",
            json={"question": "Explain the architecture of Retrieval-Augmented Generation."}
        )
        assert response.status_code == 502
        data = response.json()
        assert data["status"] == "error"
        assert "rate limit" in data["message"].lower()
        # Ensure secret keys are not leaked in the error
        assert "gsk_test" not in response.text

    get_settings.cache_clear()
