from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime

class MatchStatus(str, Enum):
    pendente = "pendente"
    aceito = "aceito"
    em_entrega = "em_entrega"
    finalizado = "finalizado"
    rejeitado = "rejeitado"
    cancelado = "cancelado"

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    frete_id = Column(Integer, ForeignKey("fretes.id"), nullable=False, index=True)
    motorista_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    valor_proposta = Column(Float, nullable=False)
    mensagem = Column(Text, default="", nullable=True)
    status = Column(String, default="pendente", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relationships
    frete = relationship("Frete", back_populates="matches")
    motorista = relationship("User", back_populates="matches_as_motorista", foreign_keys=[motorista_id])
    messages = relationship("Message", back_populates="match", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match {self.id} - Frete {self.frete_id} - Motorista {self.motorista_id} - {self.status}>"
