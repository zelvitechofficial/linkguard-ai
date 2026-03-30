from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chatbot_service import ChatbotService, get_chatbot_service
from app.api.v1.auth import get_current_user, get_user_with_email
from app.db.session import get_db
from app.repositories.chatbot_repository import ChatbotRepository
from app.repositories.user_repository import UserRepository
from app.core.config import settings

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    request: ChatRequest,
    chatbot: ChatbotService = Depends(get_chatbot_service),
    user: dict = Depends(get_user_with_email),
    db: AsyncSession = Depends(get_db),
):
    """Returns an educational answer to a security-related question with daily limits."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    repo = ChatbotRepository(db)
    user_repo = UserRepository(db)
    local_user = await user_repo.get_or_create_user(
        user.get("sub"), 
        user.get("email") or "unset@example.com"
    )
    
    answer = chatbot.get_response(request.query)
    
    if local_user:
        await repo.create_log(local_user.id, request.query, answer)
        
    return {"answer": answer}


@router.get("/tips", response_model=dict)
async def get_tips(
    count: Optional[int] = Query(None, description="Number of tips to return"),
    chatbot: ChatbotService = Depends(get_chatbot_service),
):
    """Returns a list of curated security awareness tips."""
    return {"tips": chatbot.get_all_tips(count=count)}


@router.get("/tip-of-the-day", response_model=dict)
async def get_tip_of_the_day(chatbot: ChatbotService = Depends(get_chatbot_service)):
    """Returns a single random security tip."""
    return {"tip": chatbot.get_random_tip()}


@router.get("/faqs", response_model=dict)
async def get_faqs(chatbot: ChatbotService = Depends(get_chatbot_service)):
    """Returns a list of curated cybersecurity FAQs."""
    return {"faqs": chatbot.get_faqs()}


