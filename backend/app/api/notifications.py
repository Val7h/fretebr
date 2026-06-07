from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# ============= SCHEMAS =============

class NotificationResponse(BaseModel):
    id: int
    tipo: str
    titulo: str
    conteudo: str
    is_read: bool
    match_id: int | None
    frete_id: int | None
    user_from_id: int | None
    created_at: datetime
    read_at: datetime | None

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    notificacoes: List[NotificationResponse]
    total: int
    nao_lidas: int

# ============= ENDPOINTS =============

@router.get("", response_model=NotificationListResponse)
def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Listar notificações do usuário.
    Pode filtrar apenas não lidas com unread_only=true
    """
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    # Contar não lidas
    nao_lidas = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    # Buscar com ordenação (mais recentes primeiro)
    notificacoes = query.order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(limit).all()

    total = query.count()

    return {
        "notificacoes": notificacoes,
        "total": total,
        "nao_lidas": nao_lidas
    }

@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marcar notificação como lida.
    Apenas o usuário pode marcar suas próprias notificações.
    """
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")

    notif.is_read = True
    notif.read_at = datetime.utcnow()
    db.commit()

    return {"message": "Notificação marcada como lida"}

@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marcar todas as notificações como lidas.
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        Notification.is_read: True,
        Notification.read_at: datetime.utcnow()
    })
    db.commit()

    return {"message": "Todas as notificações marcadas como lidas"}

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletar uma notificação.
    Apenas o usuário pode deletar suas próprias notificações.
    """
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notif:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")

    db.delete(notif)
    db.commit()

    return {"message": "Notificação deletada"}

@router.get("/count/unread")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obter quantidade de notificações não lidas.
    """
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}

# ============= FUNÇÕES AUXILIARES =============

def create_notification(
    db: Session,
    user_id: int,
    tipo: str,
    titulo: str,
    conteudo: str,
    match_id: int | None = None,
    frete_id: int | None = None,
    user_from_id: int | None = None
):
    """
    Criar uma nova notificação.
    Função auxiliar para ser usada por outros endpoints.
    """
    notif = Notification(
        user_id=user_id,
        tipo=tipo,
        titulo=titulo,
        conteudo=conteudo,
        match_id=match_id,
        frete_id=frete_id,
        user_from_id=user_from_id
    )
    db.add(notif)
    db.commit()
    return notif
