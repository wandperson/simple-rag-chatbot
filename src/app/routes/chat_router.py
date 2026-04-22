# Backend
from fastapi import APIRouter, Depends

# Custom modules
from app.schemas import Message, MessageCreate
from app.dependencies import get_chat_service
from app.services import ChatService


API_PREFIX = "/api/chat"

router = APIRouter()


@router.post("/ask", response_model=Message)
def ask_assistant(
    message: MessageCreate,
    include_history: bool = False,
    chat_service: ChatService = Depends(get_chat_service),
):
    print(f"Received message: {message.content}, include_history: {include_history}")
    answer = chat_service.get_answer(message.content, include_history)
    msg_answer = Message.model_validate(answer)
    return msg_answer


@router.get("/history", response_model=list[Message])
def get_history(chat_service: ChatService = Depends(get_chat_service)):
    history = chat_service.get_user_history()
    messages = [Message.model_validate(row) for row in history]
    return messages
