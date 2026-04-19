# Backend
from fastapi.testclient import TestClient

# Testing
import pytest

# Testing module
from app.main import app
from app.services import ChatService


client = TestClient(app)


@pytest.fixture
def mock_get_answer(monkeypatch):
    def fake_get_answer(self, content, include_history):
        return {
            "role": "assistant",
            "content": "<dynamic response>",
            "timestamp": "<not implemented>",
        }

    monkeypatch.setattr(ChatService, "get_answer", fake_get_answer)


def test_api_ask_endpoint_returns_valid_response(mock_get_answer):
    payload = {"content": "Hi there!"}

    response = client.post("/api/chat/ask", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == {"role", "content", "timestamp"}
    assert data["role"] == "assistant"
