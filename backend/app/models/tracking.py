"""
Real-Time Tracking Models
Armazena localizações de fretes em tempo real
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class FreteTracking(Base):
    """Histórico de localizações de um frete"""
    __tablename__ = "frete_tracking"

    id = Column(Integer, primary_key=True, index=True)

    # Relações
    frete_id = Column(Integer, ForeignKey("fretes.id", ondelete="CASCADE"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Localização
    latitude = Column(Numeric(10, 8), nullable=False)  # -90 a 90
    longitude = Column(Numeric(11, 8), nullable=False)  # -180 a 180
    address = Column(String(500), nullable=True)  # Endereço reverso (opcional)
    accuracy = Column(Numeric(5, 2), nullable=True)  # Precisão em metros

    # Status
    status = Column(String(50), default="em_transito")  # em_transito, parado, entregue, problema
    description = Column(String(200), nullable=True)  # "Entrando na cidade", "Trânsito", etc

    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_latest = Column(Boolean, default=False)  # Flag para localização mais recente

    # Relacionamentos
    frete = relationship("Frete", backref="tracking_history")
    match = relationship("Match", backref="tracking_history")
    motorista = relationship("User", backref="tracking_history")

    __table_args__ = (
        Index("idx_frete_tracking_frete_id_timestamp", "frete_id", "timestamp"),
        Index("idx_frete_tracking_motorista_id", "motorista_id"),
        Index("idx_frete_tracking_is_latest", "is_latest"),
    )

    def __repr__(self):
        return f"<FreteTracking {self.id}: ({self.latitude}, {self.longitude})>"


class FreteCurrentLocation(Base):
    """Localização atual de um frete (para queries rápidas)"""
    __tablename__ = "frete_current_location"

    id = Column(Integer, primary_key=True, index=True)

    # Relações
    frete_id = Column(Integer, ForeignKey("fretes.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Localização atual
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    address = Column(String(500), nullable=True)

    # ETA (Estimated Time of Arrival)
    eta_minutes = Column(Integer, nullable=True)  # Minutos até chegar
    distance_km = Column(Numeric(8, 2), nullable=True)  # Km até o destino

    # Status
    status = Column(String(50), default="em_transito")
    last_update = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_online = Column(Boolean, default=True)  # Motorista está enviando atualizações?

    # Relacionamentos
    frete = relationship("Frete", backref="current_location", uselist=False)
    match = relationship("Match", backref="current_location", uselist=False)
    motorista = relationship("User", backref="current_location", uselist=False)

    __table_args__ = (
        Index("idx_frete_current_location_frete_id", "frete_id"),
        Index("idx_frete_current_location_motorista_id", "motorista_id"),
        Index("idx_frete_current_location_last_update", "last_update"),
    )

    def __repr__(self):
        return f"<FreteCurrentLocation {self.frete_id}: ({self.latitude}, {self.longitude})>"


class TrackingSession(Base):
    """Sessão de rastreamento (para controlar quando motorista liga/desliga tracking)"""
    __tablename__ = "tracking_session"

    id = Column(Integer, primary_key=True, index=True)

    # Relações
    frete_id = Column(Integer, ForeignKey("fretes.id", ondelete="CASCADE"), nullable=False, index=True)
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sessão
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    # Estatísticas
    total_locations = Column(Integer, default=0)  # Quantas atualizações foram recebidas
    total_distance_km = Column(Numeric(8, 2), default=0)

    # Relacionamentos
    frete = relationship("Frete", backref="tracking_sessions")
    motorista = relationship("User", backref="tracking_sessions")

    def __repr__(self):
        return f"<TrackingSession {self.id}: frete={self.frete_id}>"
