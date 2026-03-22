import json
from fastapi import APIRouter, Request, HTTPException, status, Depends
from svix.webhooks import Webhook, WebhookVerificationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import setup_logger
from app.db.session import get_db
from app.repositories.user_repository import UserRepository

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/clerk", status_code=status.HTTP_200_OK)
async def clerk_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receives Clerk webhook events, verifies the Svix signature,
    and syncs user records into the local database.
    """
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing svix headers")

    body = await request.body()

    if not settings.CLERK_WEBHOOK_SECRET:
        if settings.DEBUG:
            logger.warning("CLERK_WEBHOOK_SECRET not set — skipping verification in DEBUG mode")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook secret not configured",
            )
    else:
        try:
            Webhook(settings.CLERK_WEBHOOK_SECRET).verify(body, request.headers)
        except WebhookVerificationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid signature: {e}")

    payload = json.loads(body)
    event_type = payload.get("type")
    data = payload.get("data", {})

    logger.info(f"Received Clerk webhook event: {event_type}")

    if event_type in ("user.created", "user.updated"):
        clerk_id = data.get("id")
        email_addresses = data.get("email_addresses", [])
        email = email_addresses[0].get("email_address") if email_addresses else "unset@example.com"

        user_repo = UserRepository(db)
        user = await user_repo.get_user_by_clerk_id(clerk_id)

        if user:
            await user_repo.update_user_email(clerk_id, email)
            logger.info(f"Updated user in DB: {clerk_id}")
        else:
            await user_repo.create_user(clerk_id, email)
            logger.info(f"Created new user in DB: {clerk_id}")

        await db.commit()

    return {"message": "Webhook processed successfully"}
