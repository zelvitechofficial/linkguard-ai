from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.sql import extract
from datetime import datetime, date
from app.models.chatbot_log import ChatbotLog

class ChatbotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_count(self, user_id: str) -> int:
        today = date.today()
        query = select(func.count(ChatbotLog.id)).where(
            and_(
                ChatbotLog.user_id == user_id,
                func.date(ChatbotLog.created_at) == today
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create_log(self, user_id: str, query_text: str, response_text: str):
        log = ChatbotLog(user_id=user_id, query=query_text, response=response_text)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
