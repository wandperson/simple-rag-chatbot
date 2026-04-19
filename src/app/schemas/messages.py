# Basic
from enum import Enum
from typing import Optional

# Data Validation
from pydantic import BaseModel, Field


class Role(str, Enum):
    user = "user"
    assistant = "assistant"


class MessageBase(BaseModel):
    content: str = Field(..., description="Text content of the message")


class Message(MessageBase):
    role: Role = Field(..., description="Sender of the message")
    timestamp: Optional[str] = Field(
        default=None, description="When the message was sended in ISO 8601 format"
    )


class MessageCreate(MessageBase):
    pass
