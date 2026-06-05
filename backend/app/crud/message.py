from sqlalchemy.orm import Session
from app.models import Message
from typing import List, Optional
from datetime import datetime

def create_message(db: Session, match_id: int, sender_id: int, conteudo: str) -> Message:
    """
    Create a new message in a match's chat.

    Args:
        db: Database session
        match_id: ID of the match
        sender_id: ID of the user sending the message
        conteudo: Content of the message

    Returns:
        Message: The created Message object
    """
    db_message = Message(
        match_id=match_id,
        sender_id=sender_id,
        conteudo=conteudo,
        created_at=datetime.now()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: int) -> Optional[Message]:
    """
    Get a message by ID.

    Args:
        db: Database session
        message_id: ID of the message

    Returns:
        Message or None if not found
    """
    return db.query(Message).filter(Message.id == message_id).first()

def get_messages_by_match(db: Session, match_id: int) -> List[Message]:
    """
    Get all messages in a match's chat, ordered by creation date.

    Args:
        db: Database session
        match_id: ID of the match

    Returns:
        List of messages for the match, ordered by created_at ascending
    """
    return (
        db.query(Message)
        .filter(Message.match_id == match_id)
        .order_by(Message.created_at.asc())
        .all()
    )

def delete_message(db: Session, message_id: int) -> bool:
    """
    Delete a message.

    Args:
        db: Database session
        message_id: ID of the message

    Returns:
        True if deleted, False if not found
    """
    db_message = get_message(db, message_id)
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False
