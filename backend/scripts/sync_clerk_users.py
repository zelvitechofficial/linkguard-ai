import asyncio
import sys
import os
import httpx

sys.path.append(os.getcwd())

from sqlalchemy import text, select
from app.db.session import engine, SessionLocal
from app.core.config import settings
from app.models.user import User

async def sync_users():
    secret_key = settings.CLERK_SECRET_KEY_ROBUST
    if not secret_key:
        print("Error: Clerk Secret Key not configured.")
        return

    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }

    async with SessionLocal() as db:
        # 1. Fetch all users with 'unset@example.com'
        stmt = select(User).where(User.email == "unset@example.com")
        result = await db.execute(stmt)
        users_to_fix = result.scalars().all()
        
        if not users_to_fix:
            print("No users with 'unset@example.com' found.")
            return

        print(f"Found {len(users_to_fix)} users to fix.")

        async with httpx.AsyncClient() as client:
            for user in users_to_fix:
                print(f"Fetching data for Clerk ID: {user.clerk_user_id}...")
                try:
                    response = await client.get(
                        f"https://api.clerk.com/v1/users/{user.clerk_user_id}", 
                        headers=headers
                    )
                    if response.status_code == 200:
                        clerk_data = response.json()
                        emails = clerk_data.get("email_addresses", [])
                        if emails:
                            real_email = emails[0].get("email_address")
                            print(f"  Found email: {real_email}")
                            user.email = real_email
                        else:
                            print("  No email found in Clerk for this user.")
                    else:
                        print(f"  Failed to fetch from Clerk: {response.status_code}")
                except Exception as e:
                    print(f"  Error fetching: {e}")

        await db.commit()
        print("Sync completed.")

if __name__ == "__main__":
    asyncio.run(sync_users())
