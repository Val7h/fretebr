from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.database import get_db
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.models import Match, Frete, User

router = APIRouter(prefix="/api/matches", tags=["matches"])

@router.post("/", status_code=201)
def create_match(
    frete_id: int,
    valor_proposta: float = Query(..., gt=0),
    mensagem: str = Query("", max_length=500),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new match/proposal (only motoristas can propose)
    """
    # Validate user is motorista
    if current_user.tipo != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem fazer propostas"
        )

    # Validate frete exists
    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )

    # Check if motorista already proposed to this frete
    existing_match = db.query(Match).filter(
        and_(
            Match.frete_id == frete_id,
            Match.motorista_id == current_user.id,
            Match.status != "rejeitado"
        )
    ).first()

    if existing_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já tem uma proposta ativa neste frete"
        )

    # Create match
    new_match = Match(
        frete_id=frete_id,
        motorista_id=current_user.id,
        valor_proposta=valor_proposta,
        mensagem=mensagem,
        status="pendente"
    )

    db.add(new_match)
    db.commit()
    db.refresh(new_match)

    return {
        "id": new_match.id,
        "frete_id": new_match.frete_id,
        "motorista_id": new_match.motorista_id,
        "valor_proposta": new_match.valor_proposta,
        "status": new_match.status,
        "mensagem": new_match.mensagem,
        "created_at": new_match.created_at.isoformat(),
        "updated_at": new_match.updated_at.isoformat()
    }

@router.get("/frete/{frete_id}")
def get_frete_matches(
    frete_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all proposals for a specific frete (only shipper who posted can see)
    """
    # Get frete
    frete = db.query(Frete).filter(Frete.id == frete_id).first()
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )

    # Validate user is the shipper who posted this frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode ver propostas dos seus próprios fretes"
        )

    # Get matches
    matches = db.query(Match).filter(
        Match.frete_id == frete_id
    ).offset(skip).limit(limit).all()

    result = []
    for match in matches:
        motorista = db.query(User).filter(User.id == match.motorista_id).first()
        result.append({
            "id": match.id,
            "frete_id": match.frete_id,
            "motorista_id": match.motorista_id,
            "motorista_nome": motorista.nome if motorista else "Unknown",
            "motorista_email": motorista.email if motorista else "Unknown",
            "valor_proposta": match.valor_proposta,
            "status": match.status,
            "mensagem": match.mensagem,
            "created_at": match.created_at.isoformat()
        })

    return result

@router.get("/my-proposals")
def get_my_proposals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all proposals made by current motorista
    """
    if current_user.tipo != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem ver suas propostas"
        )

    matches = db.query(Match).filter(
        Match.motorista_id == current_user.id
    ).offset(skip).limit(limit).all()

    result = []
    for match in matches:
        frete = db.query(Frete).filter(Frete.id == match.frete_id).first()
        result.append({
            "id": match.id,
            "frete_id": match.frete_id,
            "frete_origem": frete.origem if frete else "Unknown",
            "frete_destino": frete.destino if frete else "Unknown",
            "valor_proposta": match.valor_proposta,
            "status": match.status,
            "created_at": match.created_at.isoformat()
        })

    return result

@router.put("/{match_id}/accept", status_code=200)
def accept_match(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept a proposal (only shipper can accept)
    """
    # Get match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negociação não encontrada"
        )

    # Get frete
    frete = db.query(Frete).filter(Frete.id == match.frete_id).first()

    # Validate user is the shipper who posted the frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode aceitar propostas dos seus próprios fretes"
        )

    # Validar transicao via state machine (pendente -> aceito)
    from app.state_machine import assert_transition
    assert_transition(match.status, "aceito")

    # Accept match
    match.status = "aceito"
    match.updated_at = datetime.utcnow()

    # Reject all other proposals for this frete
    db.query(Match).filter(
        and_(
            Match.frete_id == match.frete_id,
            Match.id != match_id,
            Match.status == "pendente"
        )
    ).update({"status": "rejeitado", "updated_at": datetime.utcnow()})

    db.commit()
    db.refresh(match)

    motorista = db.query(User).filter(User.id == match.motorista_id).first()

    return {
        "id": match.id,
        "frete_id": match.frete_id,
        "motorista_nome": motorista.nome if motorista else "Unknown",
        "valor_proposta": match.valor_proposta,
        "status": match.status,
        "message": "Proposal accepted! You can now chat with the motorista."
    }

@router.put("/{match_id}/reject", status_code=200)
def reject_match(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a proposal (only shipper can reject)
    """
    # Get match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negociação não encontrada"
        )

    # Get frete
    frete = db.query(Frete).filter(Frete.id == match.frete_id).first()

    # Validate user is the shipper who posted the frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode rejeitar propostas dos seus próprios fretes"
        )

    # Validar transicao via state machine
    from app.state_machine import assert_transition
    assert_transition(match.status, "rejeitado")

    # Reject match
    match.status = "rejeitado"
    match.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(match)

    return {
        "id": match.id,
        "status": match.status,
        "message": "Proposal rejected"
    }

@router.get("/{match_id}")
def get_match(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get match details
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negociação não encontrada"
        )

    frete = db.query(Frete).filter(Frete.id == match.frete_id).first()
    motorista = db.query(User).filter(User.id == match.motorista_id).first()

    # Validate user is involved in this match
    if current_user.id != match.motorista_id and current_user.id != frete.motorista_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode ver negociações em que está envolvido"
        )

    return {
        "id": match.id,
        "frete_id": match.frete_id,
        "frete_origem": frete.origem,
        "frete_destino": frete.destino,
        "frete_peso": frete.peso_kg,
        "motorista_id": match.motorista_id,
        "motorista_nome": motorista.nome,
        "motorista_email": motorista.email,
        "valor_proposta": match.valor_proposta,
        "status": match.status,
        "mensagem": match.mensagem,
        "created_at": match.created_at.isoformat()
    }
