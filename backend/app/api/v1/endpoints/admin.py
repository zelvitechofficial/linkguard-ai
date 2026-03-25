import json
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.auth import get_admin_user
from app.repositories.url_scan_repository import URLScanRepository
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(dependencies=[Depends(get_admin_user)])

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Return high-level KPI counts."""
    try:
        repo = URLScanRepository(db)
        return await repo.get_overall_stats()
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
    
    # Get the directory of the current file (app/api/v1/endpoints)
    current_dir = pathlib.Path(__file__).resolve().parent
    
    # Go up to the 'app' directory (3 levels up from endpoints)
    # endpoints -> v1 -> api -> app
    app_dir = current_dir.parent.parent.parent
    
    # Path to metrics.json: app/ml_models/metrics.json
    metrics_path = app_dir / "ml_models" / "metrics.json"
    
    logger.info(f"Attempting to load ML metrics from: {metrics_path}")
    
    try:
        if metrics_path.exists():
            with open(metrics_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("Successfully loaded ML metrics.")
                return data
        else:
            logger.warning(f"ML metrics file NOT found at {metrics_path}")
            
            # Fallback for different working directories
            alternative_path = pathlib.Path("app/ml_models/metrics.json").resolve()
            if alternative_path.exists():
                 logger.info(f"Found ML metrics at alternative path: {alternative_path}")
                 with open(alternative_path, "r", encoding="utf-8") as f:
                     return json.load(f)
                     
    except Exception as e:
        logger.error(f"Error reading metrics file {metrics_path}: {e}")
        
    return {}

@router.get("/users")
async def get_users():
    """Fetch user list from Clerk Backend API."""
    secret_key = settings.CLERK_SECRET_KEY_ROBUST
    if not secret_key:
        logger.warning("CLERK_SECRET_KEY missing. Cannot fetch user list.")
        return []

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.clerk.com/v1/users", headers=headers)
            if response.status_code != 200:
                logger.error(f"Clerk API returned {response.status_code}: {response.text}")
                return []
            users = response.json()
            
            return [
                {
                    "id": u.get("id"),
                    "email": u.get("email_addresses", [{}])[0].get("email_address"),
                    "first_name": u.get("first_name") or "",
                    "last_name": u.get("last_name") or "",
                    "image_url": u.get("image_url"),
                    "last_sign_in_at": u.get("last_sign_in_at"),
                    "created_at": u.get("created_at"),
                }
                for u in users
            ]
    except Exception as e:
        logger.error(f"Error fetching users from Clerk: {e}")
        return []
