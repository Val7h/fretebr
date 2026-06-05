from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime


class TransactionStatus(str, Enum):
    pendente = "pendente"
    pago = "pago"
    falhou = "falhou"
    cancelado = "cancelado"
    expirado = "expirado"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    motorista_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    shipper_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.pendente, nullable=False)
    mp_payment_id = Column(String, unique=True, nullable=True, index=True)  # Mercado Pago payment ID
    qr_code_data = Column(String, nullable=True)  # Pix QR code data (text)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Payment expiry time
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relationships
    match = relationship("Match", back_populates="transactions")
    motorista = relationship("User", foreign_keys=[motorista_id])
    shipper = relationship("User", foreign_keys=[shipper_id])

    def __repr__(self):
        return f"<Transaction {self.id} - Match {self.match_id} - {self.status}>"
