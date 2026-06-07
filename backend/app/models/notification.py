from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Tipo de notificação
    tipo = Column(String, nullable=False)  # "proposta", "aceito", "mensagem", "avaliacao", "system"
    titulo = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)

    # Contexto (IDs relacionados)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    frete_id = Column(Integer, ForeignKey("fretes.id"), nullable=True)
    user_from_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Quem enviou

    # Status
    is_read = Column(Boolean, default=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    user_from = relationship("User", foreign_keys=[user_from_id])
    match = relationship("Match")
    frete = relationship("Frete")

    def __repr__(self):
        return f"<Notification {self.id} - {self.tipo} - {self.user_id}>"
