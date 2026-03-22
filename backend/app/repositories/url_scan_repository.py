from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date
from typing import List, Optional
from app.models.url_scan import URLScan

class URLScanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_count(self, user_id: str) -> int:
        today = date.today()
        query = select(func.count(URLScan.id)).where(
            and_(
                URLScan.user_id == user_id,
                func.date(URLScan.scanned_at) == today
            )
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def create_url_scan(self, user_id: str, url: str, verdict: str, confidence: float) -> URLScan:
        scan_record = URLScan(
            user_id=user_id,
            url=url,
            verdict=verdict,
            confidence=float(confidence)
        )
        self.db.add(scan_record)
        await self.db.flush()
        return scan_record

    async def get_history_by_user_id(self, user_id: int) -> List[URLScan]:
        stmt = select(URLScan).where(URLScan.user_id == user_id).order_by(URLScan.scanned_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all_scans(self, limit: int = 200) -> List[dict]:
        """Fetch scans with user email information."""
        from sqlalchemy import text
        stmt = text("""
            SELECT u.email as user_email, u.clerk_user_id, s.url, s.verdict, s.confidence, s.scanned_at, s.id
            FROM url_scans s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.scanned_at DESC
            LIMIT :limit
        """)
        result = await self.db.execute(stmt, {"limit": limit})
        return result.mappings().all()

    async def delete_scan(self, scan_id: str) -> bool:
        from sqlalchemy import delete
        from uuid import UUID
        try:
            # Handle both string and UUID types safely
            target_id = UUID(scan_id) if isinstance(scan_id, str) else scan_id
            stmt = delete(URLScan).where(URLScan.id == target_id)
            result = await self.db.execute(stmt)
            return result.rowcount > 0
        except ValueError:
            return False

    async def get_overall_stats(self) -> dict:
        from sqlalchemy import func
        from app.models.user import User
        
        total_users = await self.db.scalar(select(func.count(User.id))) or 0
        total_scans = await self.db.scalar(select(func.count(URLScan.id))) or 0
        
        # Result of grouping
        stmt = select(URLScan.verdict, func.count(URLScan.id)).group_by(URLScan.verdict)
        rows = (await self.db.execute(stmt)).all()
        dist = {row[0]: row[1] for row in rows}
        
        return {
            "total_users": int(total_users),
            "total_scans": int(total_scans),
            "safe_scans": int(dist.get("safe", 0)),
            "malicious_scans": int(dist.get("malicious", 0)),
        }

    async def get_volume_stats(self) -> List[dict]:
        from sqlalchemy import text
        stmt = text("""
            SELECT DATE(scanned_at) as date, verdict, COUNT(*) as count
            FROM url_scans
            GROUP BY DATE(scanned_at), verdict
            ORDER BY date
        """)
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        return [
            {"date": str(r[0]), "verdict": r[1], "count": int(r[2])}
            for r in rows
        ]
