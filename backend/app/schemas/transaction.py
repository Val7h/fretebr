from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    """Schema for creating a new transaction"""
    match_id: int
    amount: float


class TransactionUpdate(BaseModel):
    """Schema for updating transaction status"""
    status: str


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: int
    match_id: int
    motorista_id: int
    shipper_id: int
    amount: float
    status: str
    mp_payment_id: Optional[str] = None
    qr_code_data: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentCreateRequest(BaseModel):
    """Schema for creating a payment request"""
    match_id: int
    amount: float


class PaymentResponse(BaseModel):
    """Schema for payment response with QR code"""
    transaction_id: int
    qr_code_data: str
    payment_id: Optional[str] = None
    expires_in_seconds: Optional[int] = None
    expires_at: Optional[datetime] = None


class PaymentStatusResponse(BaseModel):
    """Schema for payment status"""
    transaction_id: int
    status: str
    amount: float
    qr_code_data: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ReceiptResponse(BaseModel):
    """Schema for receipt after payment"""
    transaction_id: int
    match_id: int
    amount: float
    status: str
    payment_date: datetime
    motorista_id: int
    shipper_id: int
