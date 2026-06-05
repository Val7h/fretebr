from sqlalchemy.orm import Session
from app.models import Match, MatchStatus, User, UserType, Frete
from app.schemas.match import MatchCreate
from typing import List, Optional
from datetime import datetime

def create_match(db: Session, shipper_id: int, frete_id: int, valor_final: float) -> Match:
    """
    Create a new match when a shipper accepts a frete.

    Args:
        db: Database session
        shipper_id: ID of the shipper accepting the frete
        frete_id: ID of the frete being accepted
        valor_final: Final value of the match (from frete)

    Returns:
        Match: The created Match object
    """
    db_match = Match(
        frete_id=frete_id,
        shipper_id=shipper_id,
        status=MatchStatus.pendente,
        valor_final=valor_final,
        data_match=datetime.now()
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_match(db: Session, match_id: int) -> Optional[Match]:
    """
    Get a match by ID.

    Args:
        db: Database session
        match_id: ID of the match

    Returns:
        Match or None if not found
    """
    return db.query(Match).filter(Match.id == match_id).first()

def list_matches(db: Session, user_id: int, user_type: str) -> List[Match]:
    """
    Get all matches for a user.

    If user is motorista: returns matches where frete.motorista_id == user_id
    If user is shipper: returns matches where shipper_id == user_id

    Args:
        db: Database session
        user_id: ID of the user
        user_type: Type of user (motorista or shipper)

    Returns:
        List of matches for the user
    """
    if user_type == UserType.motorista:
        # Motorista sees matches on their fretes
        return (
            db.query(Match)
            .join(Frete)
            .filter(Frete.motorista_id == user_id)
            .order_by(Match.data_match.desc())
            .all()
        )
    elif user_type == UserType.shipper:
        # Shipper sees matches they accepted
        return (
            db.query(Match)
            .filter(Match.shipper_id == user_id)
            .order_by(Match.data_match.desc())
            .all()
        )
    return []

def update_match_status(db: Session, match_id: int, new_status: str) -> Optional[Match]:
    """
    Update the status of a match.

    Args:
        db: Database session
        match_id: ID of the match
        new_status: New status (must be valid MatchStatus)

    Returns:
        Updated Match or None if not found
    """
    db_match = get_match(db, match_id)
    if db_match:
        # Validate status transition
        valid_statuses = [s.value for s in MatchStatus]
        if new_status in valid_statuses:
            db_match.status = new_status
            db_match.updated_at = datetime.now()
            db.commit()
            db.refresh(db_match)
            return db_match
    return db_match

def cancel_match(db: Session, match_id: int) -> Optional[Match]:
    """
    Cancel a match by setting its status to 'cancelado'.

    Args:
        db: Database session
        match_id: ID of the match

    Returns:
        Updated Match or None if not found
    """
    return update_match_status(db, match_id, MatchStatus.cancelado.value)

def delete_match(db: Session, match_id: int) -> bool:
    """
    Delete a match.

    Args:
        db: Database session
        match_id: ID of the match

    Returns:
        True if deleted, False if not found
    """
    db_match = get_match(db, match_id)
    if db_match:
        db.delete(db_match)
        db.commit()
        return True
    return False
