from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.frete import FreteCreate, FreteUpdate, FreteResponse
from app.schemas.user import UserResponse
from app.crud.frete import (
    create_frete,
    get_frete,
    list_fretes,
    update_frete,
    delete_frete,
    get_motorista_fretes
)
from app.api.auth import get_current_user
from app.models.user import UserType

router = APIRouter(prefix="/api/fretes", tags=["fretes"])

@router.post("", response_model=FreteResponse, status_code=201)
def post_frete(
    frete: FreteCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new frete (only shippers can post)
    """
    # Check if user is a shipper
    if current_user.tipo != "shipper":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas clientes podem postar fretes. Você está cadastrado como motorista — entre como cliente para postar."
        )

    # Create frete
    db_frete = create_frete(db, current_user.id, frete)
    return db_frete

@router.get("/meus-fretes", response_model=List[FreteResponse])
def get_meus_fretes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's fretes (only motoristas)
    """
    # Check if user is a motorista
    if current_user.tipo != UserType.motorista.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o autor pode listar seus fretes"
        )

    fretes = get_motorista_fretes(db, current_user.id, skip=skip, limit=limit)
    return fretes

@router.get("", response_model=List[FreteResponse])
def list_available_fretes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    destino: str = Query(None, description="Filter by destination"),
    db: Session = Depends(get_db)
):
    """
    Get all available fretes (status = "disponível")
    """
    fretes = list_fretes(
        db,
        skip=skip,
        limit=limit,
        destino=destino,
        status="disponível"
    )
    return fretes

@router.get("/{frete_id}", response_model=FreteResponse)
def get_frete_details(
    frete_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a single frete
    """
    frete = get_frete(db, frete_id)
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )
    return frete

@router.put("/{frete_id}", response_model=FreteResponse)
def update_frete_details(
    frete_id: int,
    frete_update: FreteUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a frete (only motorista who posted can update)
    """
    # Check if user is a motorista
    if current_user.tipo != UserType.motorista.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o autor pode editar fretes"
        )

    # Get the frete
    frete = get_frete(db, frete_id)
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )

    # Check if current user owns the frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode editar seus próprios fretes"
        )

    # Check if frete is still available for updates
    if frete.status != "disponível":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível editar fretes com status 'disponível'"
        )

    # Update frete
    updated_frete = update_frete(db, frete_id, frete_update)
    return updated_frete

@router.delete("/{frete_id}", status_code=204)
def delete_frete_details(
    frete_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a frete (only motorista who posted can delete)
    """
    # Check if user is a motorista
    if current_user.tipo != UserType.motorista.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o autor pode excluir fretes"
        )

    # Get the frete
    frete = get_frete(db, frete_id)
    if not frete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frete não encontrado"
        )

    # Check if current user owns the frete
    if frete.motorista_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode excluir seus próprios fretes"
        )

    # Delete frete
    delete_frete(db, frete_id)
    return None
