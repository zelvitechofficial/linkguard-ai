from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": "1.0.0"
    }

@router.get("/limits")
async def get_usage_limits():
    return {
        "daily_scan_limit": settings.DAILY_SCAN_LIMIT,
        "daily_chatbot_limit": settings.DAILY_CHATBOT_LIMIT
    }
