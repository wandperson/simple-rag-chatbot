# Basic
from pathlib import Path
import sqlite3

# Data Manipulation
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


MAIN_DIR = Path(__file__).parent.resolve()


class DatabaseOperations:
    """
    Simulates database operations to interact with data.

    Attributes:
        df_context_table (pd.DataFrame): DataFrame of context paragraphs and vectors.
        df_user_table (pd.DataFrame): DataFrame of user message history.
    """

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.conn = connection

    # def read_context_table(self) -> list[dict]:
    #     """
    #     Reads the context table and returns the data as a list of dictionaries.

    #     Returns:
    #         list[dict]: A list of dictionaries representing data used for RAG.
    #     """
    #     json_str = self.df_context_table.to_json(orient="records")
    #     return json.loads(json_str)

    def insert_message(self, row: dict) -> None:
        """
        Inserts a new message into the memory user table and saves it to DB.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (role, content) VALUES (?, ?)",
            (row["role"], row["content"]),
        )
        self.conn.commit()

    def select_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT role, content FROM messages")
        rows = [dict(row) for row in cursor.fetchall()]
        return rows

    def select_llm_instructions(self) -> list[str]:
        instructions = [
            "You are an artificial intelligence chatbot in company BrewNest. You follow these four instructions below in all your responses:",
            "1. Answer the user's question briefly and politely;",
            "2. Answer in the language of the user's question;",
            "3. You only know the information that is in the CONTEXT, otherwise, tell the user that it is not written in your manual, and that's it;",
            "4. You can use chat history as CONTEXT.",
        ]
        return instructions

    def retrieve_context(self, vector: list[float], limit: int = 2) -> str:
        """
        Retrieve the two most relevant context paragraphs based on cosine similarity.

        Args:
            vector (list[float], optional): A 512-dimensional embedding vector.
                If not provided, a random vector will be generated.

        Returns:
            str: Concatenated string of the top 2 most similar paragraphs.
        """
        embedding = np.array(vector).reshape(1, -1)

        df_articles = pd.read_sql_query(
            "SELECT * FROM articles",
            self.conn,
        )
        df_articles["vector_numpy"] = pd.Series(
            [np.frombuffer(x, dtype=np.float32) for x in df_articles["vector"]]
        )

        vector_matrix = np.vstack(df_articles["vector_numpy"].tolist())

        similarities = cosine_similarity(embedding, vector_matrix).flatten()
        df_articles["similarity"] = similarities

        relevant_context = df_articles.sort_values(
            by="similarity", ascending=False
        ).head(limit)

        return "\n".join(relevant_context["paragraph"].astype(str).tolist())
