"""
Real-Time Tracking Routes
Endpoints para rastreamento de fretes com Google Maps
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, Frete, Match, FreteTracking, FreteCurrentLocation, TrackingSession
from app.schemas.user import UserResponse
from app.schemas.tracking import (
    LocationUpdate,
    TrackingPointResponse,
    CurrentLocationResponse,
    TrackingHistoryResponse,
    LiveTrackingResponse
)

router = APIRouter(prefix="/api/tracking", tags=["tracking"])


# ===== ENVIAR LOCALIZAÇÃO (Motorista) =====

@router.post("/update/{frete_id}", status_code=status.HTTP_200_OK)
def update_location(
    frete_id: int,
    location: LocationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Motorista envia sua localização em tempo real
    Deve ser chamado a cada 10-30 segundos
    """

    # Validar que é motorista
    if current_user.tipo != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem enviar localização"
        )

    # Validar que frete existe e está em progresso
    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(status_code=404, detail="Frete não encontrado")

    if frete.status not in ["aceito", "em_entrega", "entregue"]:
        raise HTTPException(
            status_code=400,
            detail=f"Frete status={frete.status}, não pode ser rastreado"
        )

    # Validar que motorista é o responsável
    match = db.query(Match).filter(Match.frete_id == frete_id).first()
    if not match or match.frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não é o motorista deste frete"
        )

    # Criar ponto de rastreamento
    tracking_point = FreteTracking(
        frete_id=frete_id,
        match_id=match.id,
        motorista_id=current_user.id,
        latitude=location.latitude,
        longitude=location.longitude,
        address=location.address,
        accuracy=location.accuracy,
        status=location.status,
        description=location.description
    )

    db.add(tracking_point)
    db.flush()

    # Atualizar localização atual (upsert)
    current = db.query(FreteCurrentLocation).filter(
        FreteCurrentLocation.frete_id == frete_id
    ).first()

    if current:
        # Marcar anterior como not latest
        current.is_latest = False

        # Criar novo
        new_location = FreteCurrentLocation(
            frete_id=frete_id,
            match_id=match.id,
            motorista_id=current_user.id,
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            status=location.status,
            last_update=datetime.utcnow(),
            is_online=True
        )
        db.add(new_location)
    else:
        current = FreteCurrentLocation(
            frete_id=frete_id,
            match_id=match.id,
            motorista_id=current_user.id,
            latitude=location.latitude,
            longitude=location.longitude,
            address=location.address,
            status=location.status,
            last_update=datetime.utcnow(),
            is_online=True
        )
        db.add(current)

    # Atualizar sessão de rastreamento
    session = db.query(TrackingSession).filter(
        TrackingSession.frete_id == frete_id,
        TrackingSession.is_active == True
    ).first()

    if session:
        session.total_locations += 1
    else:
        session = TrackingSession(
            frete_id=frete_id,
            motorista_id=current_user.id,
            started_at=datetime.utcnow(),
            is_active=True,
            total_locations=1
        )
        db.add(session)

    db.commit()

    return {"status": "ok", "message": "Localização atualizada"}


# ===== CONSULTAR RASTREAMENTO =====

@router.get("/current/{frete_id}", response_model=CurrentLocationResponse)
def get_current_location(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter localização atual de um frete
    Shipper pode ver, motorista também
    """

    # Validar acesso
    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(status_code=404, detail="Frete não encontrado")

    match = db.query(Match).filter(Match.frete_id == frete_id).first()

    # Shipper pode ver o frete, motorista deve ser o dele
    is_shipper = current_user.tipo == "shipper" and match and match.shipper_id == current_user.id
    is_motorista = current_user.tipo == "motorista" and frete.motorista_id == current_user.id

    if not (is_shipper or is_motorista):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a este rastreamento"
        )

    location = db.query(FreteCurrentLocation).filter(
        FreteCurrentLocation.frete_id == frete_id
    ).first()

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma localização encontrada para este frete"
        )

    return CurrentLocationResponse.from_orm(location)


@router.get("/history/{frete_id}", response_model=TrackingHistoryResponse)
def get_tracking_history(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter histórico completo de rastreamento de um frete
    """

    # Validar acesso (mesmo que get_current_location)
    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(status_code=404, detail="Frete não encontrado")

    match = db.query(Match).filter(Match.frete_id == frete_id).first()

    is_shipper = current_user.tipo == "shipper" and match and match.shipper_id == current_user.id
    is_motorista = current_user.tipo == "motorista" and frete.motorista_id == current_user.id

    if not (is_shipper or is_motorista):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    # Obter pontos
    points = db.query(FreteTracking).filter(
        FreteTracking.frete_id == frete_id
    ).order_by(FreteTracking.timestamp.asc()).all()

    if not points:
        raise HTTPException(status_code=404, detail="Sem dados de rastreamento")

    # Calcular distância total (simplificado, ideal seria usar haversine formula)
    total_distance = 0  # TODO: implementar cálculo de distância

    # Calcular duração
    started_at = points[0].timestamp
    ended_at = points[-1].timestamp
    duration_minutes = int((ended_at - started_at).total_seconds() / 60)

    return TrackingHistoryResponse(
        frete_id=frete_id,
        total_points=len(points),
        total_distance_km=None,  # TODO
        duration_minutes=duration_minutes,
        started_at=started_at,
        ended_at=ended_at,
        points=[TrackingPointResponse.from_orm(p) for p in points]
    )


@router.get("/live/{frete_id}", response_model=LiveTrackingResponse)
def get_live_tracking(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter dados para visualização ao vivo (mapa)
    Contém: localização atual, ETA, progresso
    """

    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(status_code=404, detail="Frete não encontrado")

    match = db.query(Match).filter(Match.frete_id == frete_id).first()

    is_shipper = current_user.tipo == "shipper" and match and match.shipper_id == current_user.id
    is_motorista = current_user.tipo == "motorista" and frete.motorista_id == current_user.id

    if not (is_shipper or is_motorista):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    location = db.query(FreteCurrentLocation).filter(
        FreteCurrentLocation.frete_id == frete_id
    ).first()

    if not location:
        raise HTTPException(status_code=404, detail="Sem localização para este frete")

    motorista = db.query(User).filter(User.id == frete.motorista_id).first()

    # Calcular progresso (simplificado: 0-50% em_entrega, 50-100% entregando)
    if frete.status == "aceito":
        progress = 10
    elif frete.status == "em_entrega":
        progress = 50
    else:
        progress = 100

    return LiveTrackingResponse(
        frete_id=frete_id,
        motorista_id=frete.motorista_id,
        motorista_nome=motorista.nome if motorista else None,
        origem=frete.origem,
        destino=frete.destino,
        current_location=CurrentLocationResponse.from_orm(location),
        estimated_arrival=None,  # TODO: calcular baseado em velocidade média
        status=location.status,
        progress_percentage=progress
    )


# ===== GERENCIAR SESSÃO DE RASTREAMENTO =====

@router.post("/start/{frete_id}", status_code=status.HTTP_201_CREATED)
def start_tracking_session(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Motorista inicia sessão de rastreamento
    Chamado quando motorista sai para delivery
    """

    if current_user.tipo != "motorista":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete or frete.motorista_id != current_user.id:
        raise HTTPException(status_code=404)

    # Criar ou ativar sessão
    session = db.query(TrackingSession).filter(
        TrackingSession.frete_id == frete_id,
        TrackingSession.motorista_id == current_user.id
    ).first()

    if not session:
        session = TrackingSession(
            frete_id=frete_id,
            motorista_id=current_user.id,
            started_at=datetime.utcnow(),
            is_active=True
        )
        db.add(session)
    else:
        session.is_active = True
        session.started_at = datetime.utcnow()

    db.commit()

    return {"status": "tracking_started", "session_id": session.id}


@router.post("/end/{frete_id}", status_code=status.HTTP_200_OK)
def end_tracking_session(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Motorista termina sessão de rastreamento
    """

    if current_user.tipo != "motorista":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    session = db.query(TrackingSession).filter(
        TrackingSession.frete_id == frete_id,
        TrackingSession.motorista_id == current_user.id,
        TrackingSession.is_active == True
    ).first()

    if session:
        session.is_active = False
        session.ended_at = datetime.utcnow()
        db.commit()

    return {"status": "tracking_ended"}
