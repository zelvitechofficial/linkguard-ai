from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.repositories.url_scan_repository import URLScanRepository
from app.repositories.chatbot_repository import ChatbotRepository

router = APIRouter()

@router.get("/")
async def get_usage(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the current user's usage counts and limits for URL scans and chatbot.
    """
    clerk_id = user.get("sub")
    user_repo = UserRepository(db)
    
    local_user = await user_repo.get_user_by_clerk_id(clerk_id)
    if not local_user:
        # If user doesn't exist in DB yet, usage is 0
        return {
            "scans": {"used": 0, "limit": settings.DAILY_SCAN_LIMIT},
            "chatbot": {"used": 0, "limit": settings.DAILY_CHATBOT_LIMIT}
        }
    
    url_repo = URLScanRepository(db)
    chat_repo = ChatbotRepository(db)
    
    scan_count = await url_repo.get_daily_count(local_user.id)
    chat_count = await chat_repo.get_daily_count(local_user.id)
    
    return {
        "scans": {
            "used": scan_count,
            "limit": settings.DAILY_SCAN_LIMIT
        },
        "chatbot": {
            "used": chat_count,
            "limit": settings.DAILY_CHATBOT_LIMIT
        }
    }
