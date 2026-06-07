from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from uuid import UUID
from datetime import datetime, timedelta
import random
import string

from app.database import get_db
from app.auth import get_current_user
from app.models import User, FuelStation, FuelStationAttendant, FuelReferralCode, FuelStationReferral, FuelDiscount, FuelAttendantWithdrawal
from app.schemas.fuel_station import (
    FuelStationRegisterRequest,
    FuelStationResponse,
    FuelReferralCodeCreateRequest,
    FuelReferralCodeResponse,
    FuelReferralResponse,
    FuelAttendantRegisterRequest,
    FuelAttendantEarningsResponse,
    FuelAttendantWithdrawalRequest,
    FuelAttendantWithdrawalResponse,
    FuelDiscountResponse,
)

router = APIRouter(prefix="/api/fuel-stations", tags=["Fuel Stations"])

# ===== GERADOR DE CÓDIGO ÚNICO =====

def generate_fuel_code(station_name: str, state: str) -> str:
    """Gera código único tipo: SHELL-SP-123-ABC"""
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    random_number = random.randint(100, 999)
    return f"{station_name[:4].upper()}-{state}-{random_number}-{random_suffix}"


# ===== ENDPOINTS DE POSTO =====

@router.post("/register", response_model=FuelStationResponse, status_code=status.HTTP_201_CREATED)
async def register_fuel_station(
    request: FuelStationRegisterRequest,
    db: Session = Depends(get_db),
):
    """Registrar novo posto de combustível"""

    # Validar CNPJ único
    existing = db.query(FuelStation).filter(FuelStation.cnpj == request.cnpj).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já registrado"
        )

    # Criar posto
    station = FuelStation(
        nome=request.nome,
        cnpj=request.cnpj,
        endereco=request.endereco,
        cidade=request.cidade,
        estado=request.estado,
        telefone=request.telefone,
        email=request.email,
        dono_nome=request.dono_nome,
        dono_email=request.dono_email,
        status="pendente"  # Aguarda aprovação
    )

    db.add(station)
    db.commit()
    db.refresh(station)

    # TODO: Enviar email ao dono confirmando registro

    return FuelStationResponse.from_orm(station)


@router.get("/{station_id}", response_model=FuelStationResponse)
async def get_fuel_station(station_id: UUID, db: Session = Depends(get_db)):
    """Obter dados de um posto"""
    station = db.query(FuelStation).filter(FuelStation.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Posto não encontrado")
    return FuelStationResponse.from_orm(station)


# ===== ENDPOINTS DE FRENTISTA =====

@router.post("/{station_id}/attendants", response_model=FuelReferralCodeResponse, status_code=status.HTTP_201_CREATED)
async def register_fuel_attendant(
    station_id: UUID,
    request: FuelAttendantRegisterRequest,
    db: Session = Depends(get_db),
):
    """Registrar novo frentista e gerar código de referência"""

    # Validar posto existe
    station = db.query(FuelStation).filter(FuelStation.id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Posto não encontrado")

    # Criar frentista
    attendant = FuelStationAttendant(
        station_id=station_id,
        nome=request.nome,
        email=request.email,
        telefone=request.telefone,
        pix_key=request.pix_key,
    )

    db.add(attendant)
    db.flush()

    # Gerar código único
    while True:
        codigo = generate_fuel_code(station.nome, station.estado)
        existing_code = db.query(FuelReferralCode).filter(FuelReferralCode.codigo == codigo).first()
        if not existing_code:
            break

    # Criar código de referência
    referral_code = FuelReferralCode(
        station_id=station_id,
        attendant_id=attendant.id,
        codigo=codigo,
        descricao=f"Código de {request.nome} - {station.nome}",
    )

    db.add(referral_code)
    db.commit()
    db.refresh(referral_code)

    return FuelReferralCodeResponse.from_orm(referral_code)


@router.get("/{station_id}/attendants/{attendant_id}/earnings", response_model=FuelAttendantEarningsResponse)
async def get_attendant_earnings(
    station_id: UUID,
    attendant_id: UUID,
    db: Session = Depends(get_db),
):
    """Ver ganhos do frentista"""

    attendant = db.query(FuelStationAttendant).filter(
        FuelStationAttendant.id == attendant_id,
        FuelStationAttendant.station_id == station_id
    ).first()

    if not attendant:
        raise HTTPException(status_code=404, detail="Frentista não encontrado")

    # Calcular ganhos
    earnings_result = db.query(
        func.sum(FuelStationReferral.comissao_valor).label("total")
    ).filter(
        FuelStationReferral.attendant_id == attendant_id,
        FuelStationReferral.status == "pago"
    ).first()

    total_earned = earnings_result[0] or Decimal("0.00")

    # Contar referências
    completed = db.query(func.count(FuelStationReferral.id)).filter(
        FuelStationReferral.attendant_id == attendant_id,
        FuelStationReferral.status == "pago"
    ).scalar() or 0

    pending = db.query(func.count(FuelStationReferral.id)).filter(
        FuelStationReferral.attendant_id == attendant_id,
        FuelStationReferral.status.in_(["pendente", "ativo"])
    ).scalar() or 0

    total = db.query(func.count(FuelStationReferral.id)).filter(
        FuelStationReferral.attendant_id == attendant_id
    ).scalar() or 0

    # Últimas indicações
    recent = db.query(FuelStationReferral).filter(
        FuelStationReferral.attendant_id == attendant_id
    ).order_by(FuelStationReferral.created_at.desc()).limit(5).all()

    return FuelAttendantEarningsResponse(
        total_earned=total_earned,
        referrals_completed=completed,
        referrals_pending=pending,
        referrals_total=total,
        pix_key=attendant.pix_key,
        recent_referrals=[FuelReferralResponse.from_orm(r) for r in recent]
    )


@router.post("/{station_id}/attendants/{attendant_id}/withdraw", response_model=FuelAttendantWithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def attendant_withdraw(
    station_id: UUID,
    attendant_id: UUID,
    request: FuelAttendantWithdrawalRequest,
    db: Session = Depends(get_db),
):
    """Frentista solicita saque de ganhos"""

    attendant = db.query(FuelStationAttendant).filter(
        FuelStationAttendant.id == attendant_id,
        FuelStationAttendant.station_id == station_id
    ).first()

    if not attendant:
        raise HTTPException(status_code=404, detail="Frentista não encontrado")

    if not attendant.pix_key:
        raise HTTPException(status_code=400, detail="Configure sua chave Pix primeiro")

    # Calcular saldo disponível
    earnings = db.query(
        func.sum(FuelStationReferral.comissao_valor)
    ).filter(
        FuelStationReferral.attendant_id == attendant_id,
        FuelStationReferral.status == "pago"
    ).first()[0] or Decimal("0.00")

    # Subtrair saques pendentes
    pending_withdrawals = db.query(
        func.sum(FuelAttendantWithdrawal.amount)
    ).filter(
        FuelAttendantWithdrawal.attendant_id == attendant_id,
        FuelAttendantWithdrawal.status.in_(["pendente", "processando"])
    ).first()[0] or Decimal("0.00")

    available = earnings - pending_withdrawals

    if request.amount > available:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo insuficiente. Disponível: R$ {available:.2f}"
        )

    if request.amount < Decimal("10.00"):
        raise HTTPException(status_code=400, detail="Valor mínimo: R$ 10.00")

    # Criar solicitação de saque
    withdrawal = FuelAttendantWithdrawal(
        attendant_id=attendant_id,
        amount=request.amount,
        pix_key_used=attendant.pix_key,
        status="pendente"
    )

    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)

    # TODO: Integrar com Mercado Pago para transferência automática

    return FuelAttendantWithdrawalResponse.from_orm(withdrawal)


# ===== ENDPOINTS DE CÓDIGO DE REFERÊNCIA =====

@router.get("/codes/{codigo}")
async def validate_fuel_code(codigo: str, db: Session = Depends(get_db)):
    """Validar código de referência (usado no signup)"""
    code = db.query(FuelReferralCode).filter(
        FuelReferralCode.codigo == codigo,
        FuelReferralCode.status == "ativo"
    ).first()

    if not code:
        raise HTTPException(status_code=404, detail="Código inválido ou expirado")

    station = code.station
    return {
        "codigo": code.codigo,
        "station_name": station.nome,
        "desconto_percentual": station.desconto_motorista,
        "comissao_frentista": station.comissao_percentual,
    }


# ===== FUNÇÃO AUXILIAR: REGISTRAR DESCONTO QUANDO MOTORISTA SE CADASTRA =====

def create_fuel_discount_for_motorista(
    motorista_id: UUID,
    referral_code_id: UUID,
    db: Session
):
    """
    Cria desconto de combustível quando motorista se cadastra com código de posto.
    Chamada durante o signup do motorista.
    """

    # Validar código
    code = db.query(FuelReferralCode).filter(FuelReferralCode.id == referral_code_id).first()
    if not code or code.status != "ativo":
        return None

    station = code.station

    # Criar desconto
    discount = FuelDiscount(
        motorista_id=motorista_id,
        station_id=station.id,
        referral_code_id=referral_code_id,
        percentual_desconto=station.desconto_motorista,
        status="ativo",
        data_expiracao=datetime.utcnow() + timedelta(days=365)  # 1 ano de validade
    )

    db.add(discount)

    # Criar referral
    referral = FuelStationReferral(
        station_id=station.id,
        attendant_id=code.attendant_id,
        referral_code_id=referral_code_id,
        motorista_id=motorista_id,
        status="ativo"  # Motorista se cadastrou com sucesso
    )

    db.add(referral)
    db.commit()
    db.refresh(referral)

    return referral


# ===== FUNÇÃO AUXILIAR: APLICAR COMISSÃO AO COMPLETAR FRETE =====

def apply_fuel_station_commission(
    motorista_id: UUID,
    valor_frete: Decimal,
    db: Session
):
    """
    Aplica comissão ao frentista quando motorista (que se cadastrou via código) completa frete.
    Chamada ao finalizar um frete/match.
    """

    # Buscar desconto ativo do motorista
    discount = db.query(FuelDiscount).filter(
        FuelDiscount.motorista_id == motorista_id,
        FuelDiscount.status == "ativo"
    ).first()

    if not discount or not discount.referral_code_id:
        return None

    # Buscar referral correspondente
    referral = db.query(FuelStationReferral).filter(
        FuelStationReferral.motorista_id == motorista_id,
        FuelStationReferral.referral_code_id == discount.referral_code_id,
        FuelStationReferral.status == "ativo"
    ).first()

    if not referral:
        return None

    station = referral.station

    # Calcular comissão para o frentista
    # Comissão é fixa por indicação bem-sucedida, não percentual do frete
    comissao = Decimal("10.00")  # R$ 10 por frete completado

    referral.comissao_valor = comissao
    referral.status = "pago"
    referral.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(referral)

    return referral
