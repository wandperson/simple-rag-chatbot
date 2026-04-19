# Basic
from pathlib import Path

# Data manupulation
import pandas as pd
import numpy as np

# LLM
from openai import OpenAI


MAIN_DIR = Path(__file__).parent

OPENAI_KEY = ""
client = OpenAI(api_key=OPENAI_KEY)


def main():

    df = pd.DataFrame(columns=["filename", "title", "paragraph", "vector"])

    for file in (MAIN_DIR / "data").rglob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            article = f.read()

        # Create an embedding with OpenAI
        # or just pretend we created relevant
        # if we don't have an API key
        if OPENAI_KEY:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                dimensions=512,
                input=article,
            )
            embedding = response.data[0].embedding
        else:
            embedding = np.random.rand(512).tolist()

        df.loc[len(df)] = [file.name, file.stem, article, embedding]

    df.to_json(MAIN_DIR / "context_data.json", orient="records")


if __name__ == "__main__":
    main()
