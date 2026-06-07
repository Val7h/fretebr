from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ===== FUEL STATION SCHEMAS =====

class FuelStationRegisterRequest(BaseModel):
    """Registrar novo posto de combustível"""
    nome: str = Field(..., min_length=3, max_length=255)
    cnpj: str = Field(..., regex=r"^\d{14}$")
    endereco: str = Field(..., min_length=5)
    cidade: str
    estado: str = Field(..., regex=r"^[A-Z]{2}$")
    telefone: str
    email: str
    dono_nome: str
    dono_email: str


class FuelStationResponse(BaseModel):
    """Resposta de dados do posto"""
    id: UUID
    nome: str
    cnpj: str
    endereco: str
    cidade: str
    estado: str
    comissao_percentual: Decimal
    desconto_motorista: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== REFERRAL CODE SCHEMAS =====

class FuelReferralCodeCreateRequest(BaseModel):
    """Criar código de referência para frentista"""
    attendant_id: UUID
    descricao: Optional[str] = None


class FuelReferralCodeResponse(BaseModel):
    """Resposta com código de referência"""
    id: UUID
    codigo: str
    descricao: Optional[str]
    status: str
    station_id: UUID
    attendant_id: Optional[UUID]

    class Config:
        from_attributes = True


# ===== FUEL REFERRAL SCHEMAS =====

class FuelReferralResponse(BaseModel):
    """Indicação de motorista via posto"""
    id: UUID
    station_id: UUID
    attendant_id: Optional[UUID]
    motorista_id: Optional[UUID]
    comissao_valor: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===== ATTENDANT SCHEMAS =====

class FuelAttendantRegisterRequest(BaseModel):
    """Registrar novo frentista"""
    station_id: UUID
    nome: str
    email: str
    telefone: str
    pix_key: str


class FuelAttendantEarningsResponse(BaseModel):
    """Ganhos do frentista"""
    total_earned: Decimal
    referrals_completed: int
    referrals_pending: int
    referrals_total: int
    pix_key: Optional[str]
    recent_referrals: List[FuelReferralResponse]


class FuelAttendantWithdrawalRequest(BaseModel):
    """Solicitação de saque"""
    amount: Decimal = Field(..., gt=0)


class FuelAttendantWithdrawalResponse(BaseModel):
    """Resposta de saque"""
    id: UUID
    attendant_id: UUID
    amount: Decimal
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===== FUEL DISCOUNT SCHEMAS =====

class FuelDiscountResponse(BaseModel):
    """Desconto de combustível ativo para motorista"""
    id: UUID
    motorista_id: UUID
    station_id: Optional[UUID]
    percentual_desconto: Decimal
    status: str
    data_inicio: datetime
    data_expiracao: Optional[datetime]

    class Config:
        from_attributes = True
