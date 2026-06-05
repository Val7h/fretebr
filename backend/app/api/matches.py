from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.match import MatchCreate, MatchResponse, MatchUpdate, MatchWithMessages
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.crud import match as match_crud
from app.crud import message as message_crud
from app.models import Match, MatchStatus, Frete, User
from app.services.notifications import send_whatsapp_notification
import logging

router = APIRouter(prefix="/api/matches", tags=["matches"])
logger = logging.getLogger(__name__)

@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(
    match_data: MatchCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Shipper accepts a frete and creates a match.

    Only shippers can create matches. Requires auth.

    Args:
        match_data: { frete_id }
        current_user: Current authenticated user
        db: Database session

    Returns:
        MatchResponse with match details
    """
    # Only shippers can accept fretes
    if current_user.tipo != "shipper":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only shippers can accept fretes"
        )

    # Check if frete exists
    frete = db.query(Frete).filter(Frete.id == match_data.frete_id).first()
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete not found"
        )

    # Check if frete is available
    if frete.status != "disponível":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Frete is not available for acceptance"
        )

    # Shipper cannot accept their own frete (if they are also a motorista)
    if frete.motorista_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot accept your own frete"
        )

    # Check if match already exists for this shipper and frete
    existing_match = (
        db.query(Match)
        .filter(
            Match.frete_id == match_data.frete_id,
            Match.shipper_id == current_user.id
        )
        .first()
    )
    if existing_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already accepted this frete"
        )

    # Create match
    db_match = match_crud.create_match(
        db,
        shipper_id=current_user.id,
        frete_id=match_data.frete_id,
        valor_final=frete.valor_r
    )

    # Send WhatsApp notification to motorista
    motorista = db.query(User).filter(User.id == frete.motorista_id).first()
    if motorista and motorista.telefone:
        try:
            message = f"🚚 Você recebeu uma solicitação em FreteBR! {frete.origem} → {frete.destino}. Peso: {frete.peso_kg}kg. Valor: R$ {frete.valor_r:.2f}. Acesse o app para detalhes."
            send_whatsapp_notification(motorista.telefone, message)
        except Exception as e:
            logger.error(f"Failed to send WhatsApp notification: {str(e)}")
            # Don't fail the request if WhatsApp fails

    # Refresh to get relationships
    db.refresh(db_match)
    return db_match

@router.get("", response_model=list[MatchResponse])
def list_matches(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all matches for the current user.

    If motorista: returns matches on their fretes
    If shipper: returns matches they accepted

    Requires auth.

    Returns:
        List of matches for the current user
    """
    matches = match_crud.list_matches(db, current_user.id, current_user.tipo)
    return matches

@router.get("/{match_id}", response_model=MatchWithMessages)
def get_match(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single match with full details and messages.

    Requires auth. User must be part of the match.

    Args:
        match_id: ID of the match
        current_user: Current authenticated user
        db: Database session

    Returns:
        MatchWithMessages with full details
    """
    db_match = match_crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Check if user is part of the match
    frete = db_match.frete
    is_motorista = frete.motorista_id == current_user.id
    is_shipper = db_match.shipper_id == current_user.id

    if not is_motorista and not is_shipper:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this match"
        )

    return db_match

@router.put("/{match_id}/status", response_model=MatchResponse)
def update_match_status(
    match_id: int,
    match_update: MatchUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update match status.

    Only the motorista can update the status.
    Valid transitions: pendente → aceito → em_entrega → finalizado

    Requires auth.

    Args:
        match_id: ID of the match
        match_update: { status }
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated MatchResponse
    """
    db_match = match_crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Only motorista can update status
    frete = db_match.frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the motorista can update match status"
        )

    # Validate new status
    if not match_update.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )

    valid_statuses = [s.value for s in MatchStatus]
    if match_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Update status
    updated_match = match_crud.update_match_status(db, match_id, match_update.status)
    return updated_match

@router.get("/{match_id}/messages", response_model=list[MessageResponse])
def get_messages(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages in a match's chat.

    Requires auth. User must be part of the match.

    Args:
        match_id: ID of the match
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of messages in the match chat
    """
    # Check if match exists
    db_match = match_crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Check if user is part of the match
    frete = db_match.frete
    is_motorista = frete.motorista_id == current_user.id
    is_shipper = db_match.shipper_id == current_user.id

    if not is_motorista and not is_shipper:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this match's messages"
        )

    messages = message_crud.get_messages_by_match(db, match_id)
    return messages

@router.post("/{match_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    match_id: int,
    message_data: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in a match's chat.

    Requires auth. User must be part of the match.

    Args:
        match_id: ID of the match
        message_data: { conteudo }
        current_user: Current authenticated user
        db: Database session

    Returns:
        MessageResponse with message details
    """
    # Check if match exists
    db_match = match_crud.get_match(db, match_id)
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Check if user is part of the match
    frete = db_match.frete
    is_motorista = frete.motorista_id == current_user.id
    is_shipper = db_match.shipper_id == current_user.id

    if not is_motorista and not is_shipper:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this match"
        )

    # Create message
    db_message = message_crud.create_message(
        db,
        match_id=match_id,
        sender_id=current_user.id,
        conteudo=message_data.conteudo
    )

    # Refresh to get sender relationship
    db.refresh(db_message)
    return db_message
