# Basic
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Data manupulation
import numpy as np

# LLM
from openai import OpenAI


OPENAI_KEY = ""
DIMENSIONS = 512


@dataclass
class EmbeddingResult:
    vector: list[float]
    provider: str


class LLMProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        pass

    @abstractmethod
    def get_completion(self, messages: list[dict]) -> str | None:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, dimensions: int):
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

    def get_completion(self, messages: list[dict]) -> str | None:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type: ignore
            temperature=0.05,
            max_tokens=512,
        )
        content = completion.choices[0].message.content
        return content


class StubProvider(LLMProvider):
    def __init__(self, dimensions: int = 512):
        self.dimensions = dimensions

    def embed(self, text: str) -> EmbeddingResult:
        embedding = np.random.rand(self.dimensions).tolist()
        return EmbeddingResult(vector=embedding, provider="mock")

    def get_completion(self, messages: list[dict]) -> str | None:
        # Just for demonstration, we will return the context as the answer
        for message in messages:
            if message["role"] == "system" and message["content"].startswith(
                "<CONTEXT>"
            ):
                context = (
                    message["content"]
                    .replace("<CONTEXT>", "")
                    .replace("</CONTEXT>", "")
                )
                break
        # If no context is found, return a default message
        content = (
            f"<b>Assistant would answered your question with CONTEXT:</b><br>{context}"
        )
        return content


def build_llm_provider() -> LLMProvider:
    # Create an embedding with OpenAI
    # or just pretend we created relevant
    # if we don't have an API key
    if OPENAI_KEY:
        return OpenAIProvider(api_key=OPENAI_KEY, dimensions=DIMENSIONS)
    return StubProvider(dimensions=DIMENSIONS)
