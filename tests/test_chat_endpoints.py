# Data manipulation
import numpy as np

# Testing
import pytest
from fastapi.testclient import TestClient

# Testing package
from app.main import app
from app.dependencies import get_db_conn


@pytest.fixture
def load_articles(db_connection):
    cur = db_connection.cursor()

    dimmensions = 512
    # Create test data with random vectors
    test_rows = [
        (
            "Paragraph A",
            np.array(np.random.rand(dimmensions), dtype=np.float32).tobytes(),
        ),
        (
            "Paragraph B",
            np.array(np.random.rand(dimmensions), dtype=np.float32).tobytes(),
        ),
        (
            "Paragraph C",
            np.array(np.random.rand(dimmensions), dtype=np.float32).tobytes(),
        ),
    ]

    cur.executemany(
        """    
        INSERT INTO articles (filename, title, paragraph, vector_provider, vector)
        VALUES ('mock.txt', 'Mock Article', ?, 'mock', ?)
    """,
        test_rows,
    )

    db_connection.commit()

    return db_connection


@pytest.fixture
def client(load_articles):
    def override_get_db_conn():
        return load_articles

    app.dependency_overrides[get_db_conn] = override_get_db_conn
    with TestClient(app=app) as client:
        yield client
        app.dependency_overrides.clear()


def test_api_ask_endpoint_returns_valid_response(client):
    payload = {"content": "Hi there!"}

    response = client.post("/api/chat/ask", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert {"role", "content", "timestamp"} <= data.keys()
    assert data["role"] == "assistant"
