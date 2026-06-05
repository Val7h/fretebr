from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum
from datetime import datetime

class UserType(str, Enum):
    motorista = "motorista"
    shipper = "shipper"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    tipo = Column(SQLEnum(UserType), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    cpf = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False, server_default=func.now())

    # Relationships
    fretes = relationship("Frete", back_populates="motorista")
    matches_as_shipper = relationship("Match", back_populates="shipper", foreign_keys="Match.shipper_id")
    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")

    def __repr__(self):
        return f"<User {self.email}>"
