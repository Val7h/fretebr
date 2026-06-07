"""
Rating and Review System Models
Permite que motoristas e shippers avaliem uns aos outros
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class RatingMotorista(Base):
    """Rating dado a um motorista por um shipper"""
    __tablename__ = "rating_motorista"

    id = Column(Integer, primary_key=True, index=True)

    # Relações
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    shipper_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    frete_id = Column(Integer, ForeignKey("fretes.id", ondelete="SET NULL"), nullable=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)

    # Avaliação
    stars = Column(Numeric(3, 1), nullable=False)  # 1.0 a 5.0, pode ser 4.5, 3.5, etc
    review_text = Column(Text, nullable=True)  # Comentário opcional

    # Categoria de avaliação (opcional, para mais granularidade)
    categoria = Column(String(50), nullable=True)  # "cumprimento", "profissionalismo", "seguranca"

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    motorista = relationship("User", foreign_keys=[motorista_id], backref="ratings_received_motorista")
    shipper = relationship("User", foreign_keys=[shipper_id], backref="ratings_given_motorista")
    frete = relationship("Frete", backref="ratings_motorista")
    match = relationship("Match", backref="rating_motorista")

    __table_args__ = (
        Index("idx_rating_motorista_motorista_id", "motorista_id"),
        Index("idx_rating_motorista_shipper_id", "shipper_id"),
        Index("idx_rating_motorista_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<RatingMotorista {self.id}: {self.stars} stars>"


class RatingShipper(Base):
    """Rating dado a um shipper por um motorista"""
    __tablename__ = "rating_shipper"

    id = Column(Integer, primary_key=True, index=True)

    # Relações
    shipper_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    motorista_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    frete_id = Column(Integer, ForeignKey("fretes.id", ondelete="SET NULL"), nullable=True)
    match_id = Column(Integer, ForeignKey("matches.id", ondelete="SET NULL"), nullable=True)

    # Avaliação
    stars = Column(Numeric(3, 1), nullable=False)  # 1.0 a 5.0
    review_text = Column(Text, nullable=True)  # Comentário opcional

    # Categoria
    categoria = Column(String(50), nullable=True)  # "comunicacao", "pagamento", "profissionalismo"

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    shipper = relationship("User", foreign_keys=[shipper_id], backref="ratings_received_shipper")
    motorista = relationship("User", foreign_keys=[motorista_id], backref="ratings_given_shipper")
    frete = relationship("Frete", backref="ratings_shipper")
    match = relationship("Match", backref="rating_shipper")

    __table_args__ = (
        Index("idx_rating_shipper_shipper_id", "shipper_id"),
        Index("idx_rating_shipper_motorista_id", "motorista_id"),
        Index("idx_rating_shipper_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<RatingShipper {self.id}: {self.stars} stars>"


class UserReputation(Base):
    """Cache de reputação do usuário (calculado periodicamente)"""
    __tablename__ = "user_reputation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    # Scores
    average_rating = Column(Numeric(3, 2), default=5.0)  # 0.00 a 5.00
    total_ratings = Column(Integer, default=0)

    # Breakdowns
    five_stars = Column(Integer, default=0)
    four_stars = Column(Integer, default=0)
    three_stars = Column(Integer, default=0)
    two_stars = Column(Integer, default=0)
    one_star = Column(Integer, default=0)

    # Badges
    is_verified = Column(String(20), default="pending")  # pending, approved, rejected
    badges = Column(String(500), nullable=True)  # JSON: ["⭐ Expert", "🔥 Streak", "💯 Perfect"]

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    user = relationship("User", backref="reputation", uselist=False)

    def __repr__(self):
        return f"<UserReputation {self.user_id}: {self.average_rating}>"
