# Data manipulation
import numpy as np
import pandas as pd

# Testing
import pytest

# Testing module
from app.database import DatabaseOperations


@pytest.fixture
def mock_database():
    database = DatabaseOperations()

    database.df_context_table = pd.DataFrame(
        {
            "vector": [
                np.array([1.0, 0.0]),
                np.array([0.0, 1.0]),
                np.array([0.5, 0.5]),
            ],
            "paragraph": ["Paragraph A", "Paragraph B", "Paragraph C"],
        }
    )
    return database


def test_retrieve_context_with_vector_A(mock_database):
    test_vector = [1.0, 0.0]
    result = mock_database.retrieve_context(vector=test_vector)
    assert "Paragraph A" in result
    assert "Paragraph C" in result
    assert result.index("Paragraph A") < result.index("Paragraph C")


def test_retrieve_context_with_vector_B(mock_database):
    test_vector = [0.0, 1.0]
    result = mock_database.retrieve_context(vector=test_vector)
    assert "Paragraph B" in result
    assert "Paragraph C" in result
    assert result.index("Paragraph B") < result.index("Paragraph C")
