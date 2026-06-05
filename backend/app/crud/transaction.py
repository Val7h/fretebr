from sqlalchemy.orm import Session
from app.models import Transaction, Match, TransactionStatus
from datetime import datetime, timedelta
from typing import Optional, List


def create_transaction(
    db: Session,
    match_id: int,
    motorista_id: int,
    shipper_id: int,
    amount: float,
    mp_payment_id: Optional[str] = None,
    qr_code_data: Optional[str] = None,
    expires_at: Optional[datetime] = None
) -> Transaction:
    """Create a new transaction"""
    db_transaction = Transaction(
        match_id=match_id,
        motorista_id=motorista_id,
        shipper_id=shipper_id,
        amount=amount,
        status=TransactionStatus.pendente,
        mp_payment_id=mp_payment_id,
        qr_code_data=qr_code_data,
        expires_at=expires_at
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Get a transaction by ID"""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_transaction_by_match(db: Session, match_id: int) -> Optional[Transaction]:
    """Get the active transaction for a match"""
    return (
        db.query(Transaction)
        .filter(Transaction.match_id == match_id)
        .filter(Transaction.status.in_([TransactionStatus.pendente, TransactionStatus.pago]))
        .first()
    )


def get_transaction_by_mp_id(db: Session, mp_payment_id: str) -> Optional[Transaction]:
    """Get transaction by Mercado Pago payment ID"""
    return db.query(Transaction).filter(Transaction.mp_payment_id == mp_payment_id).first()


def list_transactions(
    db: Session,
    user_id: int,
    user_type: str,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Transaction]:
    """
    List transactions for a user.

    If motorista: list transactions where they are the motorista
    If shipper: list transactions where they are the shipper
    """
    query = db.query(Transaction)

    if user_type == "motorista":
        query = query.filter(Transaction.motorista_id == user_id)
    else:  # shipper
        query = query.filter(Transaction.shipper_id == user_id)

    if status:
        query = query.filter(Transaction.status == status)

    return query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()


def update_transaction_status(
    db: Session,
    transaction_id: int,
    status: str
) -> Optional[Transaction]:
    """Update transaction status"""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db_transaction.status = status
        db_transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def update_transaction(
    db: Session,
    transaction_id: int,
    **kwargs
) -> Optional[Transaction]:
    """Update transaction with arbitrary fields"""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        for key, value in kwargs.items():
            if hasattr(db_transaction, key):
                setattr(db_transaction, key, value)
        db_transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int) -> bool:
    """Delete a transaction (soft delete via status)"""
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction:
        db_transaction.status = TransactionStatus.cancelado
        db.commit()
        return True
    return False
