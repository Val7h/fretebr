from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

# ============= SCHEMAS =============

class TransactionResponse(BaseModel):
    id: int
    match_id: int
    motorista_id: int
    shipper_id: int
    amount: float
    status: str
    mp_payment_id: str | None
    qr_code_data: str | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionDetailResponse(BaseModel):
    id: int
    match_id: int
    motorista_id: int
    motorista_nome: str
    motorista_email: str
    shipper_id: int
    shipper_nome: str
    shipper_email: str
    amount: float
    status: str
    mp_payment_id: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionListResponse(BaseModel):
    transacoes: List[TransactionDetailResponse]
    total: int
    total_amount: float

# ============= ENDPOINTS =============

@router.get("", response_model=TransactionListResponse)
def get_user_transactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar transações do usuário (como motorista ou shipper).
    Pode filtrar por status.
    """
    query = db.query(Transaction).filter(
        (Transaction.motorista_id == current_user.id) |
        (Transaction.shipper_id == current_user.id)
    )

    if status:
        query = query.filter(Transaction.status == status)

    # Contar total e soma
    total = query.count()
    total_amount = sum(t.amount for t in query.all()) if total > 0 else 0

    # Buscar com paginação (mais recentes primeiro)
    transacoes = query.order_by(
        Transaction.created_at.desc()
    ).offset(offset).limit(limit).all()

    # Montar resposta detalhada
    result = []
    for t in transacoes:
        motorista = db.query(User).filter(User.id == t.motorista_id).first()
        shipper = db.query(User).filter(User.id == t.shipper_id).first()

        result.append(TransactionDetailResponse(
            id=t.id,
            match_id=t.match_id,
            motorista_id=t.motorista_id,
            motorista_nome=motorista.nome if motorista else "Deletado",
            motorista_email=motorista.email if motorista else "N/A",
            shipper_id=t.shipper_id,
            shipper_nome=shipper.nome if shipper else "Deletado",
            shipper_email=shipper.email if shipper else "N/A",
            amount=t.amount,
            status=t.status,
            mp_payment_id=t.mp_payment_id,
            created_at=t.created_at,
            updated_at=t.updated_at
        ))

    return {
        "transacoes": result,
        "total": total,
        "total_amount": total_amount
    }

@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter detalhes de uma transação específica.
    Apenas usuários envolvidos podem acessar.
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # Verificar se usuário está envolvido
    if transaction.motorista_id != current_user.id and transaction.shipper_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para acessar esta transação"
        )

    motorista = db.query(User).filter(User.id == transaction.motorista_id).first()
    shipper = db.query(User).filter(User.id == transaction.shipper_id).first()

    return TransactionDetailResponse(
        id=transaction.id,
        match_id=transaction.match_id,
        motorista_id=transaction.motorista_id,
        motorista_nome=motorista.nome if motorista else "Deletado",
        motorista_email=motorista.email if motorista else "N/A",
        shipper_id=transaction.shipper_id,
        shipper_nome=shipper.nome if shipper else "Deletado",
        shipper_email=shipper.email if shipper else "N/A",
        amount=transaction.amount,
        status=transaction.status,
        mp_payment_id=transaction.mp_payment_id,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at
    )

@router.get("/statistics/summary")
def get_transaction_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter resumo de transações (total pago, pendente, etc).
    """
    transacoes = db.query(Transaction).filter(
        (Transaction.motorista_id == current_user.id) |
        (Transaction.shipper_id == current_user.id)
    ).all()

    stats = {
        "total_transacoes": len(transacoes),
        "total_pago": sum(t.amount for t in transacoes if t.status == "pago"),
        "total_pendente": sum(t.amount for t in transacoes if t.status == "pendente"),
        "total_falhou": sum(t.amount for t in transacoes if t.status == "falhou"),
        "transacoes_por_status": {
            "pago": len([t for t in transacoes if t.status == "pago"]),
            "pendente": len([t for t in transacoes if t.status == "pendente"]),
            "falhou": len([t for t in transacoes if t.status == "falhou"]),
            "cancelado": len([t for t in transacoes if t.status == "cancelado"]),
            "expirado": len([t for t in transacoes if t.status == "expirado"]),
        }
    }

    return stats
