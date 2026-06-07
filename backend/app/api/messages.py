from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.message import Message
from app.models.match import Match
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/messages", tags=["messages"])

# ============= SCHEMAS =============

class MessageCreate(BaseModel):
    conteudo: str

class MessageResponse(BaseModel):
    id: int
    match_id: int
    sender_id: int
    conteudo: str
    created_at: datetime
    sender: dict  # {id, nome, email}

    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    mensagens: List[MessageResponse]
    total: int

# ============= ENDPOINTS =============

@router.get("/match/{match_id}", response_model=MessageListResponse)
def get_match_messages(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar todas as mensagens de um match.
    Apenas usuários envolvidos no match podem ver as mensagens.
    """
    # Verificar se o match existe
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match não encontrado")

    # Verificar se o usuário é shipper ou motorista do match
    frete = match.frete
    is_shipper = current_user.id == frete.motorista_id
    is_motorista = current_user.id == match.motorista_id

    if not (is_shipper or is_motorista):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para ver as mensagens deste match"
        )

    # Buscar mensagens ordenadas por data
    mensagens = db.query(Message).filter(
        Message.match_id == match_id
    ).order_by(Message.created_at.asc()).all()

    # Serializar com dados do sender
    response_data = []
    for msg in mensagens:
        response_data.append({
            "id": msg.id,
            "match_id": msg.match_id,
            "sender_id": msg.sender_id,
            "conteudo": msg.conteudo,
            "created_at": msg.created_at,
            "sender": {
                "id": msg.sender.id,
                "nome": msg.sender.nome,
                "email": msg.sender.email
            }
        })

    return {
        "mensagens": response_data,
        "total": len(response_data)
    }

@router.post("/match/{match_id}")
def create_message(
    match_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enviar uma mensagem em um match.
    Apenas usuários envolvidos no match podem enviar mensagens.
    """
    # Validar conteúdo
    if not message_data.conteudo.strip():
        raise HTTPException(status_code=400, detail="Mensagem não pode estar vazia")

    if len(message_data.conteudo) > 2000:
        raise HTTPException(status_code=400, detail="Mensagem muito longa (máx 2000 caracteres)")

    # Verificar se o match existe
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match não encontrado")

    # Verificar se o match está aceito
    if match.status != "aceito":
        raise HTTPException(status_code=400, detail="Chat disponível apenas após aceitar a proposta")

    # Verificar se o usuário é shipper ou motorista do match
    frete = match.frete
    is_shipper = current_user.id == frete.motorista_id
    is_motorista = current_user.id == match.motorista_id

    if not (is_shipper or is_motorista):
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para enviar mensagens neste match"
        )

    # Criar mensagem
    message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        conteudo=message_data.conteudo.strip()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "id": message.id,
        "match_id": message.match_id,
        "sender_id": message.sender_id,
        "conteudo": message.conteudo,
        "created_at": message.created_at,
        "sender": {
            "id": current_user.id,
            "nome": current_user.nome,
            "email": current_user.email
        },
        "message": "Mensagem enviada com sucesso"
    }

@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar uma mensagem.
    Apenas o autor da mensagem pode deletá-la.
    """
    # Buscar a mensagem
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")

    # Verificar se o usuário é o autor
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Você só pode deletar suas próprias mensagens"
        )

    # Deletar
    db.delete(message)
    db.commit()

    return {"message": "Mensagem deletada com sucesso"}
