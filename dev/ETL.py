# Basic
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from contextlib import contextmanager
import sqlite3

# Data manupulation
import numpy as np

# LLM
from openai import OpenAI


MAIN_DIR = Path(__file__).parent
DB_PATH = MAIN_DIR / "datastore.db"

OPENAI_KEY = ""


@dataclass
class EmbeddingResult:
    vector: list[float]
    provider: str


class EmbeddingService(ABC):
    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        pass


class OpenAIES(EmbeddingService):
    def __init__(self, api_key: str, dimensions: int = 512):
        self.client = OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
        self.dimensions = dimensions

    def embed(self, text: str) -> EmbeddingResult:
        response = self.client.embeddings.create(
            model=self.model,
            dimensions=self.dimensions,
            input=text,
        )
        embedding = response.data[0].embedding
        return EmbeddingResult(vector=embedding, provider="openai")


class MockES(EmbeddingService):
    def __init__(self, dimensions: int = 512):
        self.dimensions = dimensions

    def embed(self, text: str) -> EmbeddingResult:
        embedding = np.random.rand(self.dimensions).tolist()
        return EmbeddingResult(vector=embedding, provider="mock")


def build_embedding_service() -> EmbeddingService:
    # Create an embedding with OpenAI
    # or just pretend we created relevant
    # if we don't have an API key
    if OPENAI_KEY:
        return OpenAIES(OPENAI_KEY)
    return MockES()


@contextmanager
def db():
    connection = sqlite3.connect(DB_PATH)
    try:
        yield connection
    finally:
        connection.close()


def create_datastore() -> None:
    # Rewrite the DB every run
    DB_PATH.unlink()

    # Create the tables
    with db() as conn:
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

    print(f"Created new datastore at {DB_PATH} with tables 'articles' and 'messages'.")


def load_articles_to_db(
    embedding_service: EmbeddingService = build_embedding_service(),
) -> None:
    with db() as conn:
        cur = conn.cursor()

        for file in (MAIN_DIR / "data" / "articles").rglob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                article = f.read()

            embedding_result = embedding_service.embed(article)
            embedding = np.array(embedding_result.vector, dtype=np.float32)

            cur.execute(
                """    
                INSERT INTO articles (filename, title, paragraph, vector_provider, vector)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    file.name,
                    file.stem,
                    article,
                    embedding_result.provider,
                    embedding.tobytes(),
                ),
            )

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM articles")
        count = cur.fetchone()[0]
        print(f"Loaded {count} articles into the database.")


def load_messages_to_db() -> None:
    with db() as conn:
        cur = conn.cursor()

        with open(
            MAIN_DIR / "data" / "user_messages.json", "r", encoding="utf-8"
        ) as file:
            data = json.load(file)

        messages = [(item["role"], item["content"], item["timestamp"]) for item in data]

        cur.executemany(
            """
            INSERT INTO messages (role, content, timestamp)
            VALUES (?, ?, ?)
        """,
            messages,
        )

        conn.commit()

        cur.execute("SELECT COUNT(*) FROM messages")
        count = cur.fetchone()[0]
        print(f"Loaded {count} messages into the database.")


def main():
    create_datastore()
    load_articles_to_db()
    load_messages_to_db()


if __name__ == "__main__":
    main()
