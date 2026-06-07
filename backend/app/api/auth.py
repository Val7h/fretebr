from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, AuthResponse
from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_password, hash_password, create_user_from_google
from app.routes.fuel_station import create_fuel_discount_for_motorista
from app.models import FuelReferralCode
from app.auth.google import GoogleOAuthConfig, GoogleOAuthHandler
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> UserResponse:
    """
    Get current user from JWT token
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.post("/signup", response_model=AuthResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        db_user = create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Se tem código de referência do posto, criar desconto
    if user.fuel_referral_code:
        code = db.query(FuelReferralCode).filter(
            FuelReferralCode.codigo == user.fuel_referral_code,
            FuelReferralCode.status == "ativo"
        ).first()

        if code:
            create_fuel_discount_for_motorista(db_user.id, code.id, db)

    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/login", response_model=AuthResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    db_user = get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.get("/me", response_model=UserResponse)
def get_me(user: UserResponse = Depends(get_current_user)):
    """
    Get current user data
    """
    return user


# ===== GOOGLE OAUTH ENDPOINTS =====

@router.get("/google/login-url")
def get_google_login_url():
    """
    Retorna URL para o usuário fazer login via Google

    Frontend: redireciona usuário para esta URL
    """
    auth_url = GoogleOAuthConfig.get_auth_url()
    if not auth_url:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth não está configurado. Configure GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET."
        )

    return {
        "auth_url": auth_url,
        "client_id": GoogleOAuthConfig.GOOGLE_CLIENT_ID
    }


@router.post("/google/callback", response_model=AuthResponse)
def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    fuel_referral_code: str = Query(None, description="Optional fuel referral code"),
    db: Session = Depends(get_db)
):
    """
    Callback do Google OAuth

    Frontend: após autorizar no Google, redireciona para:
    /api/auth/google/callback?code=...

    Args:
        code: Authorization code do Google
        fuel_referral_code: Código opcional do posto

    Returns:
        AuthResponse com access_token e user completo
    """
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code is required"
        )

    # Autenticar com Google
    user_data = GoogleOAuthHandler.authenticate_with_google(code)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Falha ao autenticar com Google. Tente novamente."
        )

    try:
        # Criar ou atualizar usuário
        db_user = create_user_from_google(
            db=db,
            google_id=user_data["google_id"],
            email=user_data["email"],
            nome=user_data["nome"],
            foto=user_data.get("foto")
        )

        # Se tem código de referência do posto, criar desconto
        if fuel_referral_code:
            code_record = db.query(FuelReferralCode).filter(
                FuelReferralCode.codigo == fuel_referral_code,
                FuelReferralCode.status == "ativo"
            ).first()

            if code_record:
                create_fuel_discount_for_motorista(db_user.id, code_record.id, db)

        # Criar access token
        access_token = create_access_token(data={"sub": str(db_user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": db_user
        }

    except Exception as e:
        logger.error(f"Erro ao processar callback do Google: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar autenticação. Tente novamente."
        )


@router.post("/google/token", response_model=Token)
def google_token(
    code: str,
    fuel_referral_code: str = None,
    db: Session = Depends(get_db)
):
    """
    Versão POST do Google callback (alternativa ao GET)

    Frontend pode enviar POST em vez de GET se preferir

    Args:
        code: Authorization code do Google
        fuel_referral_code: Código opcional do posto

    Returns:
        Token com access_token e user_id
    """
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code is required"
        )

    # Autenticar com Google
    user_data = GoogleOAuthHandler.authenticate_with_google(code)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Falha ao autenticar com Google. Tente novamente."
        )

    try:
        # Criar ou atualizar usuário
        db_user = create_user_from_google(
            db=db,
            google_id=user_data["google_id"],
            email=user_data["email"],
            nome=user_data["nome"],
            foto=user_data.get("foto")
        )

        # Se tem código de referência do posto, criar desconto
        if fuel_referral_code:
            code_record = db.query(FuelReferralCode).filter(
                FuelReferralCode.codigo == fuel_referral_code,
                FuelReferralCode.status == "ativo"
            ).first()

            if code_record:
                create_fuel_discount_for_motorista(db_user.id, code_record.id, db)

        # Criar access token
        access_token = create_access_token(data={"sub": str(db_user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user.id
        }

    except Exception as e:
        logger.error(f"Erro ao processar Google token: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar autenticação. Tente novamente."
        )
