# Basic
import sqlite3

# Testing
import pytest


@pytest.fixture
def db_connection():
    # Create a mock database
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    # Set up the database schema
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE articles (
            filename TEXT,
            title TEXT,
            paragraph TEXT,
            vector_provider TEXT,
            vector BLOB
        )
    """)
    cur.execute("""
        CREATE TABLE messages (
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()

    try:
        yield conn
    finally:
        conn.close()
