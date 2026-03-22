from sqlalchemy import Column, String, DateTime, UUID, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base

class URLScan(Base):
    __tablename__ = "url_scans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    url = Column(Text, nullable=False)
    verdict = Column(String, nullable=False) # 'safe' or 'malicious'
    confidence = Column(Float, nullable=False)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="scans")
