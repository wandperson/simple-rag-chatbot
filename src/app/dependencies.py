# Backend
from fastapi import Depends

# Custom modules
from app.database import DatabaseOperations
from app.infrastructure.llm_provider import LLMProvider, build_llm_provider
from app.services import ChatService


def get_db():
    db = DatabaseOperations()
    try:
        yield db
    finally:
        pass


def get_chat_service(
    db: DatabaseOperations = Depends(get_db),
    provider: LLMProvider = Depends(build_llm_provider),
) -> ChatService:
    return ChatService(database=db, provider=provider)
