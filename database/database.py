# Basic
from pathlib import Path
import json
from typing import Optional

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

    def __init__(self) -> None:
        self.df_context_table = pd.read_json(
            MAIN_DIR / "context_data.json", orient="records"
        )
        try:
            self.df_user_table = pd.read_json(
                MAIN_DIR / "user_data.json", orient="records", lines=True
            )
        except FileNotFoundError:
            df = pd.DataFrame(columns=["role", "content"])
            self.df_user_table = df

    def read_context_table(self) -> list[dict]:
        """
        Reads the context table and returns the data as a list of dictionaries.

        Returns:
            list[dict]: A list of dictionaries representing data used for RAG.
        """
        json_str = self.df_context_table.to_json(orient="records")
        return json.loads(json_str)

    def insert_message(self, row: dict) -> None:
        """
        Inserts a new message into the memory user table and saves it to DB.
        """
        self.df_user_table.loc[len(self.df_user_table)] = row

        # SSD-friendly writes
        with open(MAIN_DIR / "user_data.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        # self.df_user_table.to_json(MAIN_DIR / "user_data.json",
        #                            orient="records",
        #                            lines=True)

    def select_history(self):
        return self.df_user_table.to_dict(orient="records")

    def select_llm_instructions(self) -> list[str]:
        instructions = [
            "You are an artificial intelligence chatbot in company BrewNest. You follow these four instructions below in all your responses:",
            "1. Answer the user's question briefly and politely;",
            "2. Answer in the language of the user's question;",
            "3. You only know the information that is in the CONTEXT, otherwise, tell the user that it is not written in your manual, and that's it;",
            "4. You can use chat history as CONTEXT.",
        ]
        return instructions

    def retrieve_context(self, vector: Optional[list[float]] = None) -> str:
        """
        Retrieve the two most relevant context paragraphs based on cosine similarity.

        Args:
            vector (list[float], optional): A 512-dimensional embedding vector.
                If not provided, a random vector will be generated.

        Returns:
            str: Concatenated string of the top 2 most similar paragraphs.
        """

        emmbedding = vector if vector else np.random.rand(512).tolist()
        emmbedding = np.array(emmbedding).reshape(1, -1)

        df_data = self.df_context_table

        vector_matrix = np.vstack(df_data["vector"].tolist())
        similarities = cosine_similarity(emmbedding, vector_matrix).flatten()

        df_data["similarity"] = similarities

        relevant_context = df_data.sort_values(by="similarity", ascending=False).head(2)

        return "\n".join(relevant_context["paragraph"].astype(str).tolist())
