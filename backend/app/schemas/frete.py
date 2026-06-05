from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class FreteBase(BaseModel):
    origem: str = Field(..., min_length=1, description="Localidade de origem")
    destino: str = Field(..., min_length=1, description="Localidade de destino")
    peso_kg: float = Field(..., gt=0, description="Peso em quilogramas")
    valor_r: float = Field(..., gt=0, description="Valor da frota em reais")
    descricao: Optional[str] = Field(None, description="Descrição adicional da frota")

class FreteCreate(FreteBase):
    """Schema para criar um novo frete"""
    pass

class FreteUpdate(BaseModel):
    """Schema para atualizar um frete existente"""
    origem: Optional[str] = Field(None, min_length=1, description="Localidade de origem")
    destino: Optional[str] = Field(None, min_length=1, description="Localidade de destino")
    peso_kg: Optional[float] = Field(None, gt=0, description="Peso em quilogramas")
    valor_r: Optional[float] = Field(None, gt=0, description="Valor da frota em reais")
    descricao: Optional[str] = Field(None, description="Descrição adicional da frota")
    status: Optional[str] = Field(None, description="Status do frete")

class FreteResponse(FreteBase):
    """Schema para responder informações de um frete"""
    id: int
    status: str
    motorista_id: int
    motorista: Optional[UserResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
