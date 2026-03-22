from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Text
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class ChatbotLog(Base):
    __tablename__ = "chatbot_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
