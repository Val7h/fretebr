from sqlalchemy.orm import Session
from app.models.frete import Frete, FreteStatus
from app.schemas.frete import FreteCreate, FreteUpdate
from typing import List, Optional

def create_frete(db: Session, motorista_id: int, frete: FreteCreate) -> Frete:
    """
    Create a new frete in the database
    """
    db_frete = Frete(
        motorista_id=motorista_id,
        origem=frete.origem,
        destino=frete.destino,
        peso_kg=frete.peso_kg,
        valor_r=frete.valor_r,
        descricao=frete.descricao
    )
    db.add(db_frete)
    db.commit()
    db.refresh(db_frete)
    return db_frete

def get_frete(db: Session, frete_id: int) -> Optional[Frete]:
    """
    Get a frete by ID
    """
    return db.query(Frete).filter(Frete.id == frete_id).first()

def list_fretes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    destino: Optional[str] = None
) -> List[Frete]:
    """
    List fretes with optional filters
    """
    query = db.query(Frete)

    # Filter by status if provided
    if status:
        query = query.filter(Frete.status == status)
    else:
        # Default: return only available fretes
        query = query.filter(Frete.status == FreteStatus.disponivel)

    # Filter by destination if provided
    if destino:
        query = query.filter(Frete.destino.ilike(f"%{destino}%"))

    return query.offset(skip).limit(limit).all()

def update_frete(db: Session, frete_id: int, frete_update: FreteUpdate) -> Optional[Frete]:
    """
    Update a frete
    """
    db_frete = get_frete(db, frete_id)
    if not db_frete:
        return None

    # Update only provided fields
    update_data = frete_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_frete, key, value)

    db.commit()
    db.refresh(db_frete)
    return db_frete

def delete_frete(db: Session, frete_id: int) -> bool:
    """
    Delete a frete
    """
    db_frete = get_frete(db, frete_id)
    if not db_frete:
        return False

    db.delete(db_frete)
    db.commit()
    return True

def get_motorista_fretes(
    db: Session,
    motorista_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Frete]:
    """
    Get all fretes for a specific motorista
    """
    return db.query(Frete).filter(
        Frete.motorista_id == motorista_id
    ).offset(skip).limit(limit).all()
