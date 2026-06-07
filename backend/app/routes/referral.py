from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Referral, ReferralWithdrawal, Frete, Match
from app.schemas.referral import (
    ReferralCreateRequest,
    ReferralResponse,
    ReferralEarningsResponse,
    ReferralHistoryItem,
    WithdrawalRequest,
    WithdrawalResponse,
)

router = APIRouter(prefix="/api/referrals", tags=["Referrals"])

# Configuração
REFERRAL_COMMISSION_PERCENTAGE = Decimal("0.20")  # 20% da comissão FreteBR
MIN_COMMISSION = Decimal("5.00")
MAX_COMMISSION = Decimal("100.00")
FRETE_COMMISSION_PERCENTAGE = Decimal("0.10")  # 10% da valor do frete vai para FreteBR


@router.post("/indicate", response_model=ReferralResponse, status_code=status.HTTP_201_CREATED)
async def indicate_motorista(
    request: ReferralCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Motorista A indica Motorista B para um frete específico.

    Regras:
    - Motorista A não pode indicar a si mesmo
    - Motorista B deve existir e estar ativo
    - Frete deve existir
    - Motorista A deve ser motorista (role = 'motorista')
    """

    # Validar que current_user é motorista
    if current_user.tipo_usuario != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem fazer indicações"
        )

    # Validar que não é auto-indicação
    if current_user.id == request.referred_motorista_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode se indicar a si mesmo"
        )

    # Validar que motorista indicado existe e é ativo
    referred_motorista = db.query(User).filter(
        User.id == request.referred_motorista_id,
        User.tipo_usuario == "motorista",
        User.is_active == True
    ).first()

    if not referred_motorista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Motorista não encontrado ou inativo"
        )

    # Validar que frete existe
    frete = db.query(Frete).filter(Frete.id == request.frete_id).first()
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )

    # Criar referência
    referral = Referral(
        referrer_motorista_id=current_user.id,
        referred_motorista_id=request.referred_motorista_id,
        frete_id=request.frete_id,
        status="pending"
    )

    db.add(referral)
    db.commit()
    db.refresh(referral)

    # TODO: Enviar notificação WhatsApp ao motorista indicado
    # f"João indicou você para um frete de R$ {frete.valor_frete}. Ver detalhes: [link]"

    return ReferralResponse.from_orm(referral)


@router.get("/earnings", response_model=ReferralEarningsResponse)
async def get_earnings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna ganhos totais de referências do motorista.
    """

    if current_user.tipo_usuario != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver ganhos de referências"
        )

    # Calcular ganhos
    earnings_result = db.query(
        func.sum(Referral.comissao_valor).label("total")
    ).filter(
        Referral.referrer_motorista_id == current_user.id,
        Referral.status == "completed"
    ).first()

    total_earned = earnings_result[0] or Decimal("0.00")

    # Contar referências por status
    referrals_completed = db.query(func.count(Referral.id)).filter(
        Referral.referrer_motorista_id == current_user.id,
        Referral.status == "completed"
    ).scalar() or 0

    referrals_pending = db.query(func.count(Referral.id)).filter(
        Referral.referrer_motorista_id == current_user.id,
        Referral.status == "pending"
    ).scalar() or 0

    referrals_rejected = db.query(func.count(Referral.id)).filter(
        Referral.referrer_motorista_id == current_user.id,
        Referral.status == "rejected"
    ).scalar() or 0

    # Últimas 5 referências
    recent_referrals = db.query(Referral).filter(
        Referral.referrer_motorista_id == current_user.id
    ).order_by(Referral.created_at.desc()).limit(5).all()

    return ReferralEarningsResponse(
        total_earned=total_earned,
        referrals_completed=referrals_completed,
        referrals_pending=referrals_pending,
        referrals_rejected=referrals_rejected,
        recent_referrals=[ReferralResponse.from_orm(r) for r in recent_referrals]
    )


@router.get("/history", response_model=list[ReferralHistoryItem])
async def get_history(
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna histórico de indicações feitas pelo motorista.
    """

    if current_user.tipo_usuario != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver histórico"
        )

    query = db.query(Referral).filter(
        Referral.referrer_motorista_id == current_user.id
    )

    if status_filter:
        query = query.filter(Referral.status == status_filter)

    referrals = query.order_by(Referral.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for ref in referrals:
        result.append(ReferralHistoryItem(
            id=ref.id,
            referred_motorista_name=ref.referred.nome_completo if ref.referred else "Unknown",
            frete_id=ref.frete_id,
            status=ref.status,
            comissao_valor=ref.comissao_valor,
            created_at=ref.created_at,
            completed_at=ref.completed_at
        ))

    return result


@router.post("/withdraw", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def withdraw_earnings(
    request: WithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Motorista solicita saque de ganhos de referências.
    """

    if current_user.tipo_usuario != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem sacar"
        )

    # Calcular saldo disponível
    earnings_result = db.query(
        func.sum(Referral.comissao_valor).label("total")
    ).filter(
        Referral.referrer_motorista_id == current_user.id,
        Referral.status == "completed"
    ).first()

    available_balance = earnings_result[0] or Decimal("0.00")

    # Subtrair saques pendentes/completados
    pending_withdrawals = db.query(func.sum(ReferralWithdrawal.amount)).filter(
        ReferralWithdrawal.motorista_id == current_user.id,
        ReferralWithdrawal.status.in_(["pending", "completed"])
    ).first()

    pending_amount = pending_withdrawals[0] or Decimal("0.00")
    available_balance -= pending_amount

    # Validar saldo suficiente
    if request.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Disponível: R$ {available_balance}"
        )

    # Validar montante mínimo
    if request.amount < Decimal("10.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor mínimo para saque: R$ 10.00"
        )

    # Criar solicitação de saque
    withdrawal = ReferralWithdrawal(
        motorista_id=current_user.id,
        amount=request.amount,
        status="pending"
    )

    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)

    # TODO: Integrar com Mercado Pago para processar transferência

    return WithdrawalResponse.from_orm(withdrawal)


# ===== FUNÇÃO AUXILIAR (chamada internamente ao completar frete) =====

def calculate_and_apply_referral_commission(
    match_id: UUID,
    frete_comissao: Decimal,
    db: Session
):
    """
    Calcula e aplica comissão de referência quando um frete é completado.

    Chamada após um match ser concluído com sucesso.
    """

    # Pegar o match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        return

    # Procurar se existe referral para este frete
    referral = db.query(Referral).filter(
        Referral.frete_id == match.frete_id,
        Referral.referred_motorista_id == match.motorista_id,
        Referral.status == "pending"
    ).first()

    if not referral:
        return

    # Calcular comissão
    comissao = frete_comissao * REFERRAL_COMMISSION_PERCENTAGE
    comissao = max(comissao, MIN_COMMISSION)
    comissao = min(comissao, MAX_COMMISSION)

    # Aplicar comissão
    referral.comissao_valor = comissao
    referral.status = "completed"
    referral.completed_at = datetime.utcnow()

    db.commit()
