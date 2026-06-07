from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_motorista_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    referred_motorista_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    frete_id = Column(UUID(as_uuid=True), ForeignKey("fretes.id", ondelete="SET NULL"), nullable=True)

    comissao_valor = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="pending")  # pending, completed, rejected, expired

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_motorista_id], backref="referrals_made")
    referred = relationship("User", foreign_keys=[referred_motorista_id], backref="referrals_received")
    frete = relationship("Frete", backref="referral")

    __table_args__ = (
        CheckConstraint("referrer_motorista_id != referred_motorista_id", name="no_self_referral"),
        Index("idx_referrals_referrer", "referrer_motorista_id"),
        Index("idx_referrals_referred", "referred_motorista_id"),
        Index("idx_referrals_status", "status"),
    )


class ReferralWithdrawal(Base):
    __tablename__ = "referral_withdrawals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    motorista_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed
    transaction_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    motorista = relationship("User", backref="referral_withdrawals")

    __table_args__ = (
        Index("idx_withdrawals_motorista", "motorista_id"),
        Index("idx_withdrawals_status", "status"),
    )
