"""
Rating and Review Routes
Endpoints para criar e consultar avaliações
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.database import get_db
from app.api.auth import get_current_user
from app.models import User, Match, Frete, RatingMotorista, RatingShipper, UserReputation
from app.schemas.user import UserResponse
from app.schemas.rating import (
    RatingCreateRequest,
    RatingResponse,
    RatingListItem,
    UserReputationResponse,
    UserProfileWithReputation,
    RatingStatistics
)

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


# ===== CRIAR AVALIAÇÃO =====

@router.post("/motorista", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def rate_motorista(
    request: RatingCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Shipper avalia um motorista
    Só pode avaliar após frete ser completado
    """

    # Validar que só shipper avalia motorista
    if current_user.tipo != "shipper":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas shippers podem avaliar motoristas"
        )

    # Validar que motorista existe
    motorista = db.query(User).filter(
        User.id == request.rated_user_id,
        User.tipo == "motorista"
    ).first()

    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    # Validar que frete foi completado (se fornecido)
    if request.frete_id:
        frete = db.query(Frete).filter(Frete.id == request.frete_id).first()
        if not frete or frete.status != "concluído":
            raise HTTPException(status_code=400, detail="Frete não foi completado")

    # Validar que match foi finalizado (se fornecido)
    if request.match_id:
        match = db.query(Match).filter(
            Match.id == request.match_id,
            Match.status == "finalizado"
        ).first()
        if not match:
            raise HTTPException(status_code=400, detail="Match não foi finalizado")

    # Validar que não foi avaliado já
    existing = db.query(RatingMotorista).filter(
        RatingMotorista.motorista_id == request.rated_user_id,
        RatingMotorista.shipper_id == current_user.id,
        RatingMotorista.frete_id == request.frete_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Você já avaliou este motorista para este frete")

    # Criar avaliação
    rating = RatingMotorista(
        motorista_id=request.rated_user_id,
        shipper_id=current_user.id,
        frete_id=request.frete_id,
        match_id=request.match_id,
        stars=request.stars,
        review_text=request.review_text,
        categoria=request.categoria
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    # Atualizar reputação do motorista (async seria melhor, mas por agora sync)
    _update_motorista_reputation(request.rated_user_id, db)

    return RatingResponse.from_orm(rating)


@router.post("/shipper", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def rate_shipper(
    request: RatingCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Motorista avalia um shipper
    Só pode avaliar após frete ser completado
    """

    # Validar que só motorista avalia shipper
    if current_user.tipo != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas motoristas podem avaliar shippers"
        )

    # Validar que shipper existe
    shipper = db.query(User).filter(
        User.id == request.rated_user_id,
        User.tipo == "shipper"
    ).first()

    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper não encontrado")

    # Validar que frete foi completado
    if request.frete_id:
        frete = db.query(Frete).filter(Frete.id == request.frete_id).first()
        if not frete or frete.status != "concluído":
            raise HTTPException(status_code=400, detail="Frete não foi completado")

    # Validar que não foi avaliado já
    existing = db.query(RatingShipper).filter(
        RatingShipper.shipper_id == request.rated_user_id,
        RatingShipper.motorista_id == current_user.id,
        RatingShipper.frete_id == request.frete_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Você já avaliou este shipper para este frete")

    # Criar avaliação
    rating = RatingShipper(
        shipper_id=request.rated_user_id,
        motorista_id=current_user.id,
        frete_id=request.frete_id,
        match_id=request.match_id,
        stars=request.stars,
        review_text=request.review_text,
        categoria=request.categoria
    )

    db.add(rating)
    db.commit()
    db.refresh(rating)

    # Atualizar reputação do shipper
    _update_shipper_reputation(request.rated_user_id, db)

    return RatingResponse.from_orm(rating)


# ===== CONSULTAR AVALIAÇÕES =====

@router.get("/motorista/{motorista_id}/ratings", response_model=RatingStatistics)
def get_motorista_ratings(
    motorista_id: int,
    db: Session = Depends(get_db)
):
    """
    Obter estatísticas de avaliações de um motorista
    """

    motorista = db.query(User).filter(User.id == motorista_id).first()
    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    # Buscar avaliações
    ratings = db.query(RatingMotorista).filter(
        RatingMotorista.motorista_id == motorista_id
    ).all()

    if not ratings:
        return RatingStatistics(
            average_rating=Decimal("5.00"),
            total_ratings=0,
            percentage_5_stars=0,
            percentage_4_stars=0,
            percentage_3_stars=0,
            percentage_2_stars=0,
            percentage_1_star=0
        )

    # Calcular estatísticas
    total = len(ratings)
    avg = sum(r.stars for r in ratings) / total
    stars_count = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for rating in ratings:
        stars_int = int(rating.stars)
        stars_count[stars_int] += 1

    return RatingStatistics(
        average_rating=Decimal(str(round(avg, 2))),
        total_ratings=total,
        percentage_5_stars=round(stars_count[5] / total * 100, 1) if total > 0 else 0,
        percentage_4_stars=round(stars_count[4] / total * 100, 1) if total > 0 else 0,
        percentage_3_stars=round(stars_count[3] / total * 100, 1) if total > 0 else 0,
        percentage_2_stars=round(stars_count[2] / total * 100, 1) if total > 0 else 0,
        percentage_1_star=round(stars_count[1] / total * 100, 1) if total > 0 else 0
    )


@router.get("/motorista/{motorista_id}/reviews", response_model=list[RatingListItem])
def get_motorista_reviews(
    motorista_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Obter avaliações detalhadas de um motorista (com comentários)
    """

    ratings = db.query(RatingMotorista).filter(
        RatingMotorista.motorista_id == motorista_id
    ).order_by(
        RatingMotorista.created_at.desc()
    ).offset(offset).limit(limit).all()

    result = []
    for rating in ratings:
        shipper = db.query(User).filter(User.id == rating.shipper_id).first()
        result.append(RatingListItem(
            id=rating.id,
            from_user_name=shipper.nome if shipper else "Usuário deletado",
            from_user_foto=shipper.foto if shipper else None,
            stars=rating.stars,
            review_text=rating.review_text,
            created_at=rating.created_at
        ))

    return result


@router.get("/shipper/{shipper_id}/ratings", response_model=RatingStatistics)
def get_shipper_ratings(
    shipper_id: int,
    db: Session = Depends(get_db)
):
    """Obter estatísticas de avaliações de um shipper"""

    shipper = db.query(User).filter(User.id == shipper_id).first()
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper não encontrado")

    ratings = db.query(RatingShipper).filter(
        RatingShipper.shipper_id == shipper_id
    ).all()

    if not ratings:
        return RatingStatistics(
            average_rating=Decimal("5.00"),
            total_ratings=0,
            percentage_5_stars=0,
            percentage_4_stars=0,
            percentage_3_stars=0,
            percentage_2_stars=0,
            percentage_1_star=0
        )

    total = len(ratings)
    avg = sum(r.stars for r in ratings) / total
    stars_count = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for rating in ratings:
        stars_int = int(rating.stars)
        stars_count[stars_int] += 1

    return RatingStatistics(
        average_rating=Decimal(str(round(avg, 2))),
        total_ratings=total,
        percentage_5_stars=round(stars_count[5] / total * 100, 1) if total > 0 else 0,
        percentage_4_stars=round(stars_count[4] / total * 100, 1) if total > 0 else 0,
        percentage_3_stars=round(stars_count[3] / total * 100, 1) if total > 0 else 0,
        percentage_2_stars=round(stars_count[2] / total * 100, 1) if total > 0 else 0,
        percentage_1_star=round(stars_count[1] / total * 100, 1) if total > 0 else 0
    )


@router.get("/shipper/{shipper_id}/reviews", response_model=list[RatingListItem])
def get_shipper_reviews(
    shipper_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obter avaliações detalhadas de um shipper"""

    ratings = db.query(RatingShipper).filter(
        RatingShipper.shipper_id == shipper_id
    ).order_by(
        RatingShipper.created_at.desc()
    ).offset(offset).limit(limit).all()

    result = []
    for rating in ratings:
        motorista = db.query(User).filter(User.id == rating.motorista_id).first()
        result.append(RatingListItem(
            id=rating.id,
            from_user_name=motorista.nome if motorista else "Usuário deletado",
            from_user_foto=motorista.foto if motorista else None,
            stars=rating.stars,
            review_text=rating.review_text,
            created_at=rating.created_at
        ))

    return result


@router.get("/user/{user_id}/profile", response_model=UserProfileWithReputation)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Perfil completo do usuário com reputação"""

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Obter reputação
    reputation = db.query(UserReputation).filter(
        UserReputation.user_id == user_id
    ).first()

    # Obter últimas avaliações
    recent_ratings = []
    if user.tipo == "motorista":
        ratings = db.query(RatingMotorista).filter(
            RatingMotorista.motorista_id == user_id
        ).order_by(RatingMotorista.created_at.desc()).limit(5).all()

        for rating in ratings:
            shipper = db.query(User).filter(User.id == rating.shipper_id).first()
            recent_ratings.append(RatingListItem(
                id=rating.id,
                from_user_name=shipper.nome if shipper else "Deletado",
                from_user_foto=shipper.foto if shipper else None,
                stars=rating.stars,
                review_text=rating.review_text,
                created_at=rating.created_at
            ))

    elif user.tipo == "shipper":
        ratings = db.query(RatingShipper).filter(
            RatingShipper.shipper_id == user_id
        ).order_by(RatingShipper.created_at.desc()).limit(5).all()

        for rating in ratings:
            motorista = db.query(User).filter(User.id == rating.motorista_id).first()
            recent_ratings.append(RatingListItem(
                id=rating.id,
                from_user_name=motorista.nome if motorista else "Deletado",
                from_user_foto=motorista.foto if motorista else None,
                stars=rating.stars,
                review_text=rating.review_text,
                created_at=rating.created_at
            ))

    return UserProfileWithReputation(
        id=user.id,
        email=user.email,
        nome=user.nome,
        tipo=user.tipo,
        telefone=user.telefone,
        foto=user.foto,
        reputation=UserReputationResponse.from_orm(reputation) if reputation else None,
        recent_ratings=recent_ratings
    )


# ===== FUNÇÕES AUXILIARES =====

def _update_motorista_reputation(motorista_id: int, db: Session):
    """Recalcula reputação do motorista"""

    ratings = db.query(RatingMotorista).filter(
        RatingMotorista.motorista_id == motorista_id
    ).all()

    if not ratings:
        return

    total = len(ratings)
    avg = sum(r.stars for r in ratings) / total
    stars_count = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for rating in ratings:
        stars_int = int(rating.stars)
        stars_count[stars_int] += 1

    # Atualizar ou criar reputação
    reputation = db.query(UserReputation).filter(
        UserReputation.user_id == motorista_id
    ).first()

    if not reputation:
        reputation = UserReputation(
            user_id=motorista_id,
            average_rating=Decimal(str(round(avg, 2))),
            total_ratings=total,
            five_stars=stars_count[5],
            four_stars=stars_count[4],
            three_stars=stars_count[3],
            two_stars=stars_count[2],
            one_star=stars_count[1]
        )
        db.add(reputation)
    else:
        reputation.average_rating = Decimal(str(round(avg, 2)))
        reputation.total_ratings = total
        reputation.five_stars = stars_count[5]
        reputation.four_stars = stars_count[4]
        reputation.three_stars = stars_count[3]
        reputation.two_stars = stars_count[2]
        reputation.one_star = stars_count[1]

    db.commit()


def _update_shipper_reputation(shipper_id: int, db: Session):
    """Recalcula reputação do shipper"""

    ratings = db.query(RatingShipper).filter(
        RatingShipper.shipper_id == shipper_id
    ).all()

    if not ratings:
        return

    total = len(ratings)
    avg = sum(r.stars for r in ratings) / total
    stars_count = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

    for rating in ratings:
        stars_int = int(rating.stars)
        stars_count[stars_int] += 1

    reputation = db.query(UserReputation).filter(
        UserReputation.user_id == shipper_id
    ).first()

    if not reputation:
        reputation = UserReputation(
            user_id=shipper_id,
            average_rating=Decimal(str(round(avg, 2))),
            total_ratings=total,
            five_stars=stars_count[5],
            four_stars=stars_count[4],
            three_stars=stars_count[3],
            two_stars=stars_count[2],
            one_star=stars_count[1]
        )
        db.add(reputation)
    else:
        reputation.average_rating = Decimal(str(round(avg, 2)))
        reputation.total_ratings = total
        reputation.five_stars = stars_count[5]
        reputation.four_stars = stars_count[4]
        reputation.three_stars = stars_count[3]
        reputation.two_stars = stars_count[2]
        reputation.one_star = stars_count[1]

    db.commit()
