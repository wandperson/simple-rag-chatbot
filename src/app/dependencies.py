# Backend
from fastapi import Depends, Request

# Custom modules
from app.database import DatabaseOperations
from app.infrastructure.llm_provider import LLMProvider, build_llm_provider
from app.services import ChatService


def get_db_conn(request: Request):
    return request.app.state.db_conn


def get_db(conn=Depends(get_db_conn)):
    return DatabaseOperations(conn)


def get_chat_service(
    db: DatabaseOperations = Depends(get_db),
    provider: LLMProvider = Depends(build_llm_provider),
) -> ChatService:
    return ChatService(database=db, provider=provider)
