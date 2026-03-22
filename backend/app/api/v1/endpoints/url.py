from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.core.config import settings
from app.services.url_service import URLService
from app.services.ml_service import MLService, get_ml_service
from app.repositories.user_repository import UserRepository
from app.repositories.url_scan_repository import URLScanRepository
from app.core.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

class URLRequest(BaseModel):
    url: str

@router.post("/analyze")
async def analyze_url(
    request: URLRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service),
):
    """
    Analyzes a URL and returns its threat verdict and ML predictions.
    Saves the scan result linked to the authenticated user.
    """
    url = request.url
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL. Must start with http:// or https://")

    try:
        # Check daily limit
        repo = URLScanRepository(db)
        local_user = await UserRepository(db).get_user_by_clerk_id(user.get("sub"))
        if local_user:
            count = await repo.get_daily_count(local_user.id)
            if count >= settings.DAILY_SCAN_LIMIT:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Daily scan limit reached ({settings.DAILY_SCAN_LIMIT}). Please try again tomorrow."
                )

        # Perform synchronous URL analysis and save to DB
        service = URLService(db, ml_service)
        result = await service.analyze_and_save_url(
            url=url,
            clerk_id=user.get("sub"),
            email=user.get("email") or "unset@example.com"
        )
        return result
    except Exception as e:
        logger.error(f"Error in analyze_url: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during URL analysis.")

@router.get("/history")
async def get_url_history(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the authenticated user's scan history."""
    clerk_id = user.get("sub")
    try:
        local_user = await UserRepository(db).get_user_by_clerk_id(clerk_id)
        if not local_user:
            return []
        return await URLScanRepository(db).get_history_by_user_id(local_user.id)
    except Exception as e:
        logger.error(f"Error fetching history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while fetching history.")
