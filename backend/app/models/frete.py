from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime

class FreteStatus(str, Enum):
    disponivel = "disponível"
    aceito = "aceito"
    entregue = "entregue"
    cancelado = "cancelado"

class Frete(Base):
    __tablename__ = "fretes"

    id = Column(Integer, primary_key=True, index=True)
    motorista_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    origem = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    peso_kg = Column(Float, nullable=False)
    valor_r = Column(Float, nullable=False)  # valor_r$ is not valid as column name
    status = Column(SQLEnum(FreteStatus), default=FreteStatus.disponivel, nullable=False)
    descricao = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relationships
    motorista = relationship("User", back_populates="fretes")
    matches = relationship("Match", back_populates="frete", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Frete {self.id} - {self.origem} to {self.destino}>"
