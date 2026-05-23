from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: uuid.UUID
    title: Optional[str]
    status: str
    created_at: datetime
    messages: List[MessageOut] = []

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str


class IngestLogRequest(BaseModel):
    conversation_id: Optional[str] = None
    model: str
    provider: str
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    status: str = "success"
    error_message: Optional[str] = None
    input_preview: Optional[str] = None
    output_preview: Optional[str] = None
    request_timestamp: Optional[str] = None
    response_timestamp: Optional[str] = None
