import json
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.auth import get_admin_user
from app.repositories.url_scan_repository import URLScanRepository
from app.services.clerk_service import ClerkService
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(dependencies=[Depends(get_admin_user)])

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Return high-level KPI counts."""
    try:
        # 1. Fetch scan stats from local database
        repo = URLScanRepository(db)
        stats = await repo.get_overall_stats()
        
        # 2. Fetch real-time user count from Clerk
        clerk_count = await ClerkService.get_user_count()
        if clerk_count > 0:
            stats["total_users"] = clerk_count
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard statistics.")

@router.get("/scans")
async def get_scans(limit: int = 200, db: AsyncSession = Depends(get_db)):
    """Return the most recent URL scans with user email."""
    try:
        repo = URLScanRepository(db)
        rows = await repo.get_all_scans(limit=limit)
        
        result = []
        for r in rows:
            # Prefer the joined user_email from the database
            r_dict = dict(r)
            email = r_dict.get("user_email") or "Unknown User"
                
            result.append({
                "id": str(r_dict["id"]),
                "email": email,
                "clerk_user_id": r_dict.get("clerk_user_id"),
                "url": r_dict["url"],
                "verdict": r_dict["verdict"],
                "confidence": float(r_dict["confidence"]) if r_dict["confidence"] is not None else None,
                "scanned_at": r_dict["scanned_at"].isoformat() if r_dict["scanned_at"] else None,
            })
            
        return result
    except Exception as e:
        logger.error(f"Error fetching scans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch scan database.")

@router.delete("/scans/{scan_id}")
async def delete_scan(scan_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a scan record from the database."""
    try:
        repo = URLScanRepository(db)
        success = await repo.delete_scan(scan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Scan record not found.")
        return {"message": "Scan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan {scan_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete scan record.")

@router.get("/scan-volume")
async def get_scan_volume(db: AsyncSession = Depends(get_db)):
    """Return daily scan counts grouped by verdict."""
    try:
        repo = URLScanRepository(db)
        return await repo.get_volume_stats()
    except Exception as e:
        logger.error(f"Error fetching volume stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch time-series data.")

@router.get("/ml-metrics")
async def get_ml_metrics():
    """Return model metrics from the training artifact JSON file."""
    import pathlib
    import json
    
    # Try multiple paths for metrics.json
    paths = [
        pathlib.Path(__file__).resolve().parent.parent.parent.parent / "ml_models" / "metrics.json",
        pathlib.Path(__file__).resolve().parent.parent.parent / "ml_models" / "metrics.json",
        pathlib.Path("app/ml_models/metrics.json").resolve(),
        pathlib.Path("ml_models/metrics.json").resolve(),
    ]
    
    for metrics_path in paths:
        try:
            if metrics_path.exists():
                with open(metrics_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded ML metrics from: {metrics_path}")
                    return data
        except Exception as e:
            logger.debug(f"Could not load metrics from {metrics_path}: {e}")
            
    logger.warning("ML metrics file NOT found in any known locations.")
    return {}

@router.get("/users")
async def get_users():
    """Fetch user list from Clerk Backend API."""
    return await ClerkService.get_users()
