from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re


def _validate_password_strength(v: Optional[str]) -> Optional[str]:
    """Politica minima: 8+ chars, pelo menos 1 letra e 1 numero."""
    if v is None:
        return v
    if len(v) < 8:
        raise ValueError("Senha precisa ter pelo menos 8 caracteres")
    if not re.search(r"[A-Za-z]", v):
        raise ValueError("Senha precisa ter pelo menos 1 letra")
    if not re.search(r"\d", v):
        raise ValueError("Senha precisa ter pelo menos 1 numero")
    return v


class UserBase(BaseModel):
    email: EmailStr
    tipo: str
    nome: str
    telefone: Optional[str] = None
    cpf: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Opcional (para OAuth)
    fuel_referral_code: Optional[str] = None  # Codigo opcional de referencia do posto

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        return _validate_password_strength(v)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    """Solicitar reset de senha (envia email)."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirmar reset com token + nova senha."""
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def _check_password(cls, v):
        return _validate_password_strength(v)

class UserResponse(BaseModel):
    id: int
    email: str
    tipo: str
    nome: str
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    google_id: Optional[str] = None
    foto: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    user: UserResponse
