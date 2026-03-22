from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.user import User
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        stmt = select(User).where(User.clerk_user_id == clerk_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, clerk_id: str, email: str) -> User:
        user = User(clerk_user_id=clerk_id, email=email)
        self.db.add(user)
        try:
            await self.db.flush()
        except Exception:
            # Handle potential race conditions (e.g. concurrent creation)
            self.db.rollback()
            raise
        return user

    async def get_or_create_user(self, clerk_id: str, email: str = "unset@example.com") -> User:
        """
        Robustly fetch or create a user. Handles:
        1. Find by Clerk ID (Primary identity).
        2. Find by Email (Fallback for re-linking or duplicate avoidance).
        3. Race conditions during concurrent creation attempts.
        """
        # 1. Try finding by clerk_id first
        user = await self.get_user_by_clerk_id(clerk_id)
        if user:
            # Always keep local email in sync with Clerk's primary email
            if email and email != "unset@example.com" and user.email != email:
                logger.info(f"Syncing email for user {clerk_id}: {user.email} -> {email}")
                user.email = email
                await self.db.flush()
            return user

        # 2. Try finding by email (if not Clerk ID found)
        if email and email != "unset@example.com":
            user = await self.get_user_by_email(email)
            if user:
                # User exists but with a different Clerk ID (re-linked account or environment reset)
                # Link their current Clerk ID to this email
                logger.warning(f"Relinking Clerk ID {clerk_id} to existing email {email}")
                user.clerk_user_id = clerk_id
                await self.db.flush()
                return user

        # 3. Create if truly not found
        from sqlalchemy.exc import IntegrityError
        try:
            return await self.create_user(clerk_id, email)
        except IntegrityError:
            # Another request likely created the user between our SELECT and INSERT
            # Rollback the failed flush and try one last time to fetch
            await self.db.rollback()
            user = await self.get_user_by_clerk_id(clerk_id)
            if not user and email:
                user = await self.get_user_by_email(email)
            
            if user:
                return user
            raise # Something else went wrong

    async def update_user_email(self, clerk_id: str, email: str) -> Optional[User]:
        user = await self.get_user_by_clerk_id(clerk_id)
        if user:
            user.email = email
            await self.db.flush()
        return user
