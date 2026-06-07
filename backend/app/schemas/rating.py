"""
Rating and Review Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class RatingCreateRequest(BaseModel):
    """Request para criar uma avaliação"""
    rated_user_id: int = Field(..., description="ID do usuário sendo avaliado")
    frete_id: Optional[int] = Field(None, description="ID do frete (opcional)")
    match_id: Optional[int] = Field(None, description="ID do match (opcional)")
    stars: Decimal = Field(..., ge=1, le=5, description="Nota de 1 a 5")
    review_text: Optional[str] = Field(None, max_length=500, description="Comentário")
    categoria: Optional[str] = Field(None, description="Categoria da avaliação")


class RatingResponse(BaseModel):
    """Response de uma avaliação"""
    id: int
    motorista_id: Optional[int] = None
    shipper_id: Optional[int] = None
    rated_user_id: Optional[int] = None
    stars: Decimal
    review_text: Optional[str] = None
    categoria: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RatingListItem(BaseModel):
    """Item na lista de avaliações"""
    id: int
    from_user_name: str
    from_user_foto: Optional[str] = None
    stars: Decimal
    review_text: Optional[str] = None
    created_at: datetime


class UserReputationResponse(BaseModel):
    """Reputação/perfil do usuário"""
    user_id: int
    average_rating: Decimal
    total_ratings: int

    # Breakdown
    five_stars: int
    four_stars: int
    three_stars: int
    two_stars: int
    one_star: int

    # Badges
    is_verified: str
    badges: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileWithReputation(BaseModel):
    """Perfil completo do usuário com reputação"""
    id: int
    email: str
    nome: str
    tipo: str
    telefone: Optional[str] = None
    foto: Optional[str] = None

    # Reputação
    reputation: Optional[UserReputationResponse] = None

    # Últimas avaliações
    recent_ratings: list[RatingListItem] = []

    class Config:
        from_attributes = True


class RatingStatistics(BaseModel):
    """Estatísticas de avaliações"""
    average_rating: Decimal
    total_ratings: int
    percentage_5_stars: float
    percentage_4_stars: float
    percentage_3_stars: float
    percentage_2_stars: float
    percentage_1_star: float
