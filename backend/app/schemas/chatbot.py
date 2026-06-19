from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    locale: str = Field(default="en", pattern="^(en|ta)$")


class ChatResponse(BaseModel):
    reply: str
    disclaimer: str
    suggestions: list[str] = []
