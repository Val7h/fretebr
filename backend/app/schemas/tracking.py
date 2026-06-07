"""
Real-Time Tracking Schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class LocationUpdate(BaseModel):
    """Atualização de localização (recebida do motorista)"""
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    accuracy: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field("em_transito", description="em_transito, parado, entregue, problema")
    description: Optional[str] = Field(None, max_length=200)


class TrackingPointResponse(BaseModel):
    """Ponto de rastreamento individual"""
    id: int
    latitude: Decimal
    longitude: Decimal
    address: Optional[str]
    accuracy: Optional[Decimal]
    status: str
    description: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class CurrentLocationResponse(BaseModel):
    """Localização atual do frete"""
    frete_id: int
    motorista_id: Optional[int]
    latitude: Decimal
    longitude: Decimal
    address: Optional[str]
    status: str
    eta_minutes: Optional[int]
    distance_km: Optional[Decimal]
    last_update: datetime
    is_online: bool

    class Config:
        from_attributes = True


class TrackingHistoryResponse(BaseModel):
    """Histórico de rastreamento"""
    frete_id: int
    total_points: int
    total_distance_km: Optional[Decimal]
    duration_minutes: Optional[int]
    started_at: datetime
    ended_at: Optional[datetime]
    points: list[TrackingPointResponse]


class LiveTrackingResponse(BaseModel):
    """Dados para visualização em tempo real (mapa)"""
    frete_id: int
    motorista_id: Optional[int]
    motorista_nome: Optional[str]
    origem: str
    destino: str
    current_location: CurrentLocationResponse
    estimated_arrival: Optional[datetime]
    status: str
    progress_percentage: int  # 0-100
