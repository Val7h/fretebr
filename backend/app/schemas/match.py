from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse
from app.schemas.frete import FreteResponse

class MatchBase(BaseModel):
    """Base schema for Match"""
    frete_id: int = Field(..., description="ID do frete")
    shipper_id: int = Field(..., description="ID do shipper que aceitou o frete")
    valor_final: float = Field(..., gt=0, description="Valor final do frete")

class MatchCreate(BaseModel):
    """Schema para criar um novo match (shipper aceita frete)"""
    frete_id: int = Field(..., description="ID do frete que o shipper deseja aceitar")

class MatchUpdate(BaseModel):
    """Schema para atualizar um match"""
    status: Optional[str] = Field(None, description="Novo status do match")

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

class MatchResponse(MatchBase):
    """Schema para responder informações de um match"""
    id: int
    status: str
    data_match: datetime
    created_at: datetime
    updated_at: datetime
    frete: Optional[FreteResponse] = None
    shipper: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class MatchWithMessages(MatchResponse):
    """Schema para retornar um match com histórico de mensagens"""
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
