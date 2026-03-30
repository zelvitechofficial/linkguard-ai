import httpx
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class ClerkService:
    @staticmethod
    async def get_user_count() -> int:
        """Fetch the total number of users from Clerk Backend API."""
        secret_key = settings.CLERK_SECRET_KEY_ROBUST
        if not secret_key:
            logger.warning("CLERK_SECRET_KEY missing. Cannot fetch user count.")
            return 0

        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.clerk.com/v1/users/count", headers=headers)
                if response.status_code == 200:
                    return response.json().get("total_count", 0)
                else:
                    logger.warning(f"Clerk user count API returned {response.status_code}")
                    return 0
        except Exception as e:
            logger.error(f"Error fetching user count from Clerk: {e}")
            return 0

    @staticmethod
    async def get_users() -> list:
        """Fetch the list of users from Clerk Backend API."""
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

    @staticmethod
    async def fetch_user_email(sub: str) -> str:
        """Fetch the user's primary email directly from Clerk backend API."""
        secret_key = settings.CLERK_SECRET_KEY_ROBUST
        if not secret_key:
            logger.warning("CLERK_SECRET_KEY_ROBUST is not set. Cannot fetch email from Clerk API.")
            return None
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {secret_key}"}
                resp = await client.get(f"https://api.clerk.com/v1/users/{sub}", headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    primary_id = data.get("primary_email_address_id")
                    emails = data.get("email_addresses", [])
                    for em in emails:
                        if em.get("id") == primary_id:
                            return em.get("email_address")
                    if emails:
                        return emails[0].get("email_address")
        except Exception as e:
            logger.error(f"Failed to fetch user email from Clerk API for sub {sub}: {e}")
        return None
