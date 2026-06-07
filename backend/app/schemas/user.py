from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    tipo: str
    nome: str
    telefone: Optional[str] = None
    cpf: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None  # Opcional (para OAuth)
    fuel_referral_code: Optional[str] = None  # Código opcional de referência do posto

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
    token_type: str
    user: UserResponse
