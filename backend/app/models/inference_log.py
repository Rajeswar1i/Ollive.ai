from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

class InferenceLog(Base):
    __tablename__ = "inference_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    model = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    latency_ms = Column(Float, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    status = Column(String, default="success")   # success | error
    error_message = Column(Text, nullable=True)
    input_preview = Column(Text, nullable=True)
    output_preview = Column(Text, nullable=True)
    request_timestamp = Column(DateTime, nullable=True)
    response_timestamp = Column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="inference_logs")
