from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class MessageCreate(BaseModel):
    """Schema para criar uma nova mensagem no chat"""
    conteudo: str = Field(..., min_length=1, max_length=5000, description="Conteúdo da mensagem")

class MessageResponse(BaseModel):
    """Schema para responder informações de uma mensagem"""
    id: int
    match_id: int
    sender_id: int
    conteudo: str
    created_at: datetime
    sender: Optional[UserResponse] = None

    class Config:
        from_attributes = True
