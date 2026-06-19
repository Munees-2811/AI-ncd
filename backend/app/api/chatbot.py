from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models import User
from app.schemas.chatbot import ChatMessage, ChatResponse
from app.services.chatbot import get_reply

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatMessage, user: User = Depends(get_current_user)):
    result = get_reply(payload.message)
    return ChatResponse(**result)
