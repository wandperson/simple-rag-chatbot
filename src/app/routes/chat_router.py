# Backend
from fastapi import APIRouter

# Custom modules
from app.schemas import Message, MessageCreate
from app.services import ChatService


API_PREFIX = "/api/chat"

router = APIRouter()

service = ChatService()


@router.post("/ask", response_model=Message)
def ask_assistant(message: MessageCreate, include_history: bool = False):
    print(f"Received message: {message.content}, include_history: {include_history}")
    answer = service.get_answer(message.content, include_history)
    msg_answer = Message.model_validate(answer)
    return msg_answer


@router.get("/history", response_model=list[Message])
def get_history():
    history = service.get_user_history()
    messages = [Message.model_validate(row) for row in history]
    return messages
