from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base

class FuelStationStatus(str, enum.Enum):
    PENDENTE = "pendente"
    ATIVO = "ativo"
    INATIVO = "inativo"

class FuelStation(Base):
    __tablename__ = "fuel_stations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(255), nullable=False)
    cnpj = Column(String(20), unique=True, nullable=False)
    endereco = Column(String(500))
    cidade = Column(String(100))
    estado = Column(String(2))
    telefone = Column(String(20))
    email = Column(String(255))
    dono_nome = Column(String(255))
    dono_email = Column(String(255))

    comissao_percentual = Column(Numeric(5, 2), default=0.50)  # 0.50% por indicação
    desconto_motorista = Column(Numeric(5, 2), default=3.00)   # 3% desconto
    status = Column(String(20), default="pendente")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendants = relationship("FuelStationAttendant", backref="station", cascade="all, delete-orphan")
    referral_codes = relationship("FuelReferralCode", backref="station", cascade="all, delete-orphan")
    referrals = relationship("FuelStationReferral", backref="station", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_fuel_stations_cidade", "cidade"),
        Index("idx_fuel_stations_estado", "estado"),
        Index("idx_fuel_stations_status", "status"),
    )


class FuelStationAttendant(Base):
    __tablename__ = "fuel_station_attendants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("fuel_stations.id", ondelete="CASCADE"), nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255))
    telefone = Column(String(20))
    pix_key = Column(String(255))  # Para saques
    status = Column(String(20), default="ativo")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    referral_codes = relationship("FuelReferralCode", backref="attendant")
    referrals = relationship("FuelStationReferral", backref="attendant")
    withdrawals = relationship("FuelAttendantWithdrawal", backref="attendant", cascade="all, delete-orphan")


class FuelReferralCode(Base):
    __tablename__ = "fuel_referral_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("fuel_stations.id", ondelete="CASCADE"), nullable=False)
    attendant_id = Column(UUID(as_uuid=True), ForeignKey("fuel_station_attendants.id", ondelete="SET NULL"), nullable=True)
    codigo = Column(String(50), unique=True, nullable=False)  # Ex: SHELL-SP-123-ABC
    descricao = Column(String(255))
    status = Column(String(20), default="ativo")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    referrals = relationship("FuelStationReferral", backref="referral_code")
    fuel_discounts = relationship("FuelDiscount", backref="referral_code")

    __table_args__ = (
        Index("idx_fuel_referral_codes_codigo", "codigo"),
    )


class FuelStationReferral(Base):
    __tablename__ = "fuel_station_referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(UUID(as_uuid=True), ForeignKey("fuel_stations.id", ondelete="CASCADE"), nullable=False)
    attendant_id = Column(UUID(as_uuid=True), ForeignKey("fuel_station_attendants.id", ondelete="SET NULL"), nullable=True)
    referral_code_id = Column(UUID(as_uuid=True), ForeignKey("fuel_referral_codes.id", ondelete="SET NULL"), nullable=True)
    motorista_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    comissao_valor = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="pendente")  # pendente, ativo, pago

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationship to user
    motorista = relationship("User", foreign_keys=[motorista_id], backref="fuel_station_referrals")

    __table_args__ = (
        Index("idx_fuel_referrals_station", "station_id"),
        Index("idx_fuel_referrals_attendant", "attendant_id"),
        Index("idx_fuel_referrals_motorista", "motorista_id"),
        Index("idx_fuel_referrals_status", "status"),
    )


class FuelDiscount(Base):
    __tablename__ = "fuel_discounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    motorista_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    station_id = Column(UUID(as_uuid=True), ForeignKey("fuel_stations.id", ondelete="SET NULL"), nullable=True)
    referral_code_id = Column(UUID(as_uuid=True), ForeignKey("fuel_referral_codes.id", ondelete="SET NULL"), nullable=True)

    percentual_desconto = Column(Numeric(5, 2), default=3.00)
    status = Column(String(20), default="ativo")  # ativo, inativo, expirado

    data_inicio = Column(DateTime, default=datetime.utcnow)
    data_expiracao = Column(DateTime)  # 12 meses depois

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    motorista = relationship("User", foreign_keys=[motorista_id], backref="fuel_discounts")

    __table_args__ = (
        Index("idx_fuel_discounts_motorista", "motorista_id"),
        Index("idx_fuel_discounts_station", "station_id"),
    )


class FuelAttendantWithdrawal(Base):
    __tablename__ = "fuel_attendant_withdrawals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attendant_id = Column(UUID(as_uuid=True), ForeignKey("fuel_station_attendants.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="pendente")  # pendente, processando, concluido, falhou

    pix_key_used = Column(String(255))
    transaction_id = Column(UUID(as_uuid=True))

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    __table_args__ = (
        Index("idx_fuel_withdrawals_attendant", "attendant_id"),
        Index("idx_fuel_withdrawals_status", "status"),
    )
