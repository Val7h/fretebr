from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class ReferralCreateRequest(BaseModel):
    """Indicar outro motorista para um frete"""
    referred_motorista_id: UUID = Field(..., description="ID do motorista a ser indicado")
    frete_id: UUID = Field(..., description="ID do frete")

    @validator('referred_motorista_id', 'frete_id')
    def validate_uuids(cls, v):
        if not v:
            raise ValueError('IDs obrigatórios')
        return v


class ReferralResponse(BaseModel):
    """Resposta de uma referência"""
    id: UUID
    referrer_motorista_id: UUID
    referred_motorista_id: UUID
    frete_id: Optional[UUID]
    comissao_valor: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReferralEarningsResponse(BaseModel):
    """Ganhos totais de referências"""
    total_earned: Decimal
    referrals_completed: int
    referrals_pending: int
    referrals_rejected: int
    recent_referrals: List[ReferralResponse]


class ReferralHistoryItem(BaseModel):
    """Item do histórico de referências"""
    id: UUID
    referred_motorista_name: str
    frete_id: Optional[UUID]
    status: str
    comissao_valor: Decimal
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class WithdrawalRequest(BaseModel):
    """Requisição para sacar ganhos"""
    amount: Decimal = Field(..., gt=0, decimal_places=2)


class WithdrawalResponse(BaseModel):
    """Resposta de saque"""
    id: UUID
    motorista_id: UUID
    amount: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
