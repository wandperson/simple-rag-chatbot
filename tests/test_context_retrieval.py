# Data manipulation
import numpy as np

# Testing
import pytest

# Testing package
from app.database import DatabaseOperations


@pytest.fixture
def load_articles(db_connection):
    cur = db_connection.cursor()

    # Insert test data with known vectors for predictable retrieval
    test_rows = [
        ("Paragraph A", np.array([1.0, 0.0], dtype=np.float32).tobytes()),
        ("Paragraph B", np.array([0.0, 1.0], dtype=np.float32).tobytes()),
        ("Paragraph C", np.array([0.5, 0.5], dtype=np.float32).tobytes()),
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
def mock_database(load_articles):
    return DatabaseOperations(load_articles)


def test_retrieve_context_with_vector_A(mock_database):
    test_vector = [1.0, 0.0]
    result = mock_database.retrieve_context(vector=test_vector, limit=2)
    assert "Paragraph A" in result
    assert "Paragraph C" in result
    assert result.index("Paragraph A") < result.index("Paragraph C")


def test_retrieve_context_with_vector_B(mock_database):
    test_vector = [0.0, 1.0]
    result = mock_database.retrieve_context(vector=test_vector, limit=2)
    assert "Paragraph B" in result
    assert "Paragraph C" in result
    assert result.index("Paragraph B") < result.index("Paragraph C")
