from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address

_limiter = Limiter(key_func=get_remote_address)


def _cookie_mode() -> bool:
    """Cookie httpOnly habilitado quando AUTH_COOKIE_MODE=true em env."""
    return os.getenv("AUTH_COOKIE_MODE", "false").lower() == "true"


def _set_auth_cookies(response: Response, access: str, refresh: str | None = None):
    """Define cookies httpOnly seguros."""
    secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    samesite = os.getenv("COOKIE_SAMESITE", "lax")
    response.set_cookie(
        key="fretebr_access",
        value=access,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    if refresh:
        response.set_cookie(
            key="fretebr_refresh",
            value=refresh,
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            path="/api/auth",  # so envia para endpoints de auth
        )


def _clear_auth_cookies(response: Response):
    response.delete_cookie("fretebr_access", path="/")
    response.delete_cookie("fretebr_refresh", path="/api/auth")
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, AuthResponse,
    PasswordResetRequest, PasswordResetConfirm,
)
from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_password, hash_password, create_user_from_google
# from app.routes.fuel_station import create_fuel_discount_for_motorista  # TODO: Fix circular import
# from app.models import FuelReferralCode
from app.auth.google import GoogleOAuthConfig, GoogleOAuthHandler
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    _env = os.getenv("ENVIRONMENT", "development").lower()
    if _env in ("production", "staging"):
        # Fail-hard em prod/staging: nao gerar runtime (multi-worker quebra JWT)
        raise RuntimeError(
            "[SECURITY] SECRET_KEY obrigatoria em production/staging. "
            "Gere com: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
        )
    # Apenas DEV: gera temporaria com WARN claro
    import secrets as _secrets
    SECRET_KEY = _secrets.token_urlsafe(64)
    logging.warning(
        "[SECURITY] SECRET_KEY nao definida (DEV) - gerada temporaria. "
        "Tokens JWT invalidam no restart. Em PROD/STAGING isso seria erro fatal."
    )
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token (curta duracao)
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token (longa duracao, rotacionado a cada uso).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_password_reset_token(user_id: int) -> str:
    """JWT de reset de senha, expira em 1h."""
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": str(user_id), "exp": expire, "type": "password_reset"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get current user from JWT token.
    Aceita tanto Authorization: Bearer <token> quanto cookie httpOnly 'fretebr_access'.
    """
    token = None
    # 1. Tenta header Authorization
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
    # 2. Fallback: cookie httpOnly
    if not token:
        token = request.cookies.get("fretebr_access")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user_id = int(user_id)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@router.post("/signup", response_model=AuthResponse)
@_limiter.limit("10/minute")
def signup(request: Request, response: Response, user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    Rate limited: 10/min por IP (anti spam de cadastros).
    Em AUTH_COOKIE_MODE=true, seta cookies httpOnly.
    """
    try:
        db_user = create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Se tem código de referência do posto, criar desconto
    # TODO: Reabilitar após corrigir circular import (fuel_station <-> auth)
    if user.fuel_referral_code:
        try:
            from app.models import FuelReferralCode
            from app.routes.fuel_station import create_fuel_discount_for_motorista
            code = db.query(FuelReferralCode).filter(
                FuelReferralCode.codigo == user.fuel_referral_code,
                FuelReferralCode.status == "ativo"
            ).first()
            if code:
                create_fuel_discount_for_motorista(db_user.id, code.id, db)
        except (ImportError, Exception) as e:
            logger.warning(f"Fuel referral indisponivel: {e}")

    # Create access token + refresh token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    if _cookie_mode():
        _set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": db_user
    }

@router.post("/login", response_model=AuthResponse)
@_limiter.limit("5/minute")
def login(request: Request, response: Response, user: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    Rate limited: 5 tentativas por minuto por IP (anti brute-force).
    Em modo AUTH_COOKIE_MODE=true, tambem seta cookies httpOnly.
    """
    db_user = get_user_by_email(db, user.email)

    if not db_user or not verify_password(user.password, db_user.password_hash):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"[AUTH] Login falhou de {client_ip}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # Setar cookies httpOnly quando habilitado (defesa contra XSS)
    if _cookie_mode():
        _set_auth_cookies(response, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/logout")
def logout(response: Response):
    """Limpa cookies httpOnly de autenticacao."""
    if _cookie_mode():
        _clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.post("/refresh")
@_limiter.limit("10/minute")
def refresh_token(request: Request, response: Response, payload: dict = None, db: Session = Depends(get_db)):
    """
    Trocar refresh_token por novo access_token (rotacao).
    Aceita body {refresh_token} ou cookie httpOnly 'fretebr_refresh'.
    Rate limited: 10/min por IP.
    """
    rt = None
    if isinstance(payload, dict):
        rt = payload.get("refresh_token")
    # Fallback: cookie
    if not rt:
        rt = request.cookies.get("fretebr_refresh")
    if not rt:
        raise HTTPException(status_code=400, detail="refresh_token required")

    try:
        decoded = jwt.decode(rt, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")
        user_id = decoded.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid refresh token: {e}")

    user = get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # Gera novos tokens (rotacao do refresh)
    new_access = create_access_token(data={"sub": str(user.id)})
    new_refresh = create_refresh_token(data={"sub": str(user.id)})

    if _cookie_mode():
        _set_auth_cookies(response, new_access, new_refresh)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }


@router.post("/forgot-password")
@_limiter.limit("3/minute")
def forgot_password(request: Request, payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Solicita reset de senha.
    Sempre retorna 200 (anti-enumeracao - nao revela se email existe).
    Em prod com SMTP, envia email com link.
    Em staging/dev sem SMTP, loga o link e (so em staging) retorna no body.
    Rate limited: 3/min por IP.
    """
    user = get_user_by_email(db, payload.email)
    response_body = {"message": "Se o email existir, enviaremos instrucoes de reset."}

    if not user:
        # Anti-enumeracao: nao revela
        return response_body

    token = create_password_reset_token(user.id)

    # URL de reset (frontend tem que ter rota /reset-password?token=...)
    front_url = os.getenv("FRONTEND_URL", "https://fretebr-web.vercel.app")
    reset_link = f"{front_url}/reset-password?token={token}"

    # Tenta enviar email se SMTP configurado
    smtp_host = os.getenv("SMTP_HOST", "").strip()
    if smtp_host:
        try:
            import smtplib
            from email.mime.text import MIMEText
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASS", "")
            smtp_from = os.getenv("SMTP_FROM", "no-reply@fretebr.com.br")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            msg = MIMEText(
                f"Ola {user.nome},\n\nClique no link para redefinir sua senha "
                f"(valido por 1 hora):\n\n{reset_link}\n\nSe nao foi voce, ignore."
            )
            msg["Subject"] = "FreteBR - Redefinir senha"
            msg["From"] = smtp_from
            msg["To"] = user.email
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if smtp_user:
                    smtp.login(smtp_user, smtp_pass)
                smtp.sendmail(smtp_from, [user.email], msg.as_string())
            logger.info(f"[AUTH] reset email enviado para {user.email}")
        except Exception as e:
            logger.error(f"[AUTH] falha SMTP no reset de {user.email}: {e}")
    else:
        # Modo MOCK: loga o link (operador pode mandar manualmente pro user)
        logger.warning(
            f"[AUTH MOCK] SMTP nao configurado. Link reset para {user.email}: {reset_link}"
        )

    # Em staging/dev, devolve link no response pra facilitar teste manual
    if os.getenv("ENVIRONMENT", "development").lower() in ("development", "staging") \
            and not smtp_host:
        response_body["debug_reset_link"] = reset_link

    return response_body


@router.post("/reset-password")
@_limiter.limit("5/minute")
def reset_password(request: Request, payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirma reset: valida token + grava nova senha.
    Rate limited: 5/min por IP.
    """
    try:
        decoded = jwt.decode(payload.token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded.get("type") != "password_reset":
            raise HTTPException(status_code=401, detail="Token invalido")
        user_id = int(decoded.get("sub", 0))
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token invalido: {e}")

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")

    # Grava nova senha
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    logger.info(f"[AUTH] senha resetada para user_id={user.id}")
    return {"message": "Senha redefinida com sucesso"}


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
    response: Response,
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
        # TODO: Reabilitar após corrigir circular import
        if fuel_referral_code:
            try:
                from app.models import FuelReferralCode
                from app.routes.fuel_station import create_fuel_discount_for_motorista
                code_record = db.query(FuelReferralCode).filter(
                    FuelReferralCode.codigo == fuel_referral_code,
                    FuelReferralCode.status == "ativo"
                ).first()
                if code_record:
                    create_fuel_discount_for_motorista(db_user.id, code_record.id, db)
            except (ImportError, Exception) as e:
                logger.warning(f"Fuel referral indisponivel: {e}")

        # Criar access + refresh tokens
        access_token = create_access_token(data={"sub": str(db_user.id)})
        refresh_tk = create_refresh_token(data={"sub": str(db_user.id)})

        # Em COOKIE_MODE, setar cookies httpOnly (alinha com /login)
        if _cookie_mode():
            _set_auth_cookies(response, access_token, refresh_tk)

        return {
            "access_token": access_token,
            "refresh_token": refresh_tk,
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
    response: Response,
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
        # TODO: Reabilitar após corrigir circular import
        if fuel_referral_code:
            try:
                from app.models import FuelReferralCode
                from app.routes.fuel_station import create_fuel_discount_for_motorista
                code_record = db.query(FuelReferralCode).filter(
                    FuelReferralCode.codigo == fuel_referral_code,
                    FuelReferralCode.status == "ativo"
                ).first()
                if code_record:
                    create_fuel_discount_for_motorista(db_user.id, code_record.id, db)
            except (ImportError, Exception) as e:
                logger.warning(f"Fuel referral indisponivel: {e}")

        # Criar access + refresh tokens
        access_token = create_access_token(data={"sub": str(db_user.id)})
        refresh_tk = create_refresh_token(data={"sub": str(db_user.id)})

        # Em COOKIE_MODE, setar cookies httpOnly (alinha com /login)
        if _cookie_mode():
            _set_auth_cookies(response, access_token, refresh_tk)

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
