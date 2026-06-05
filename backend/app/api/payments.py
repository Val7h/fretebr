"""
Payment API endpoints for FreteBR
Handles Pix payments via Mercado Pago
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.schemas.transaction import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentStatusResponse,
    ReceiptResponse,
    TransactionResponse
)
from app.schemas.user import UserResponse
from app.api.auth import get_current_user
from app.crud import transaction as transaction_crud
from app.models import Match, MatchStatus, Frete, User, Transaction, TransactionStatus
from app.services.payments import (
    send_payment_request,
    verify_payment,
    handle_webhook,
    is_payment_expired,
    get_time_until_expiry,
    MercadoPagoError
)

router = APIRouter(prefix="/api/payments", tags=["payments"])
logger = logging.getLogger(__name__)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Pix payment request.

    Only shippers can create payments.
    Match must be in "finalizado" status.
    Shipper cannot have already paid.

    Args:
        payment_data: { match_id, amount }
        current_user: Current authenticated user (must be shipper)
        db: Database session

    Returns:
        PaymentResponse with QR code data
    """
    # Only shippers can pay
    if current_user.tipo != "shipper":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only shippers can create payments"
        )

    # Get match
    db_match = db.query(Match).filter(Match.id == payment_data.match_id).first()
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Verify user is part of the match
    if db_match.shipper_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this match"
        )

    # Check match status
    if db_match.status != MatchStatus.finalizado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match must be in 'finalizado' status. Current status: {db_match.status}"
        )

    # Check if payment already exists and is not expired
    existing_transaction = transaction_crud.get_transaction_by_match(db, payment_data.match_id)
    if existing_transaction:
        if existing_transaction.status == TransactionStatus.pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already completed for this match"
            )
        elif existing_transaction.status == TransactionStatus.pendente:
            if not is_payment_expired(existing_transaction.expires_at):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment request already exists. Complete or wait for expiry."
                )
            else:
                # Mark expired transaction
                transaction_crud.update_transaction_status(
                    db, existing_transaction.id, TransactionStatus.expirado
                )

    # Get motorista info for payment
    frete = db_match.frete
    motorista = db.query(User).filter(User.id == frete.motorista_id).first()

    # Send payment request to Mercado Pago
    try:
        payment_result = send_payment_request(
            amount=payment_data.amount,
            match_id=payment_data.match_id,
            shipper_email=current_user.email,
            shipper_name=current_user.nome,
            shipper_phone=current_user.telefone or "11999999999"
        )
    except MercadoPagoError as e:
        logger.error(f"Payment request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment service unavailable: {str(e)}"
        )

    # Create transaction in database
    db_transaction = transaction_crud.create_transaction(
        db=db,
        match_id=payment_data.match_id,
        motorista_id=motorista.id,
        shipper_id=current_user.id,
        amount=payment_data.amount,
        mp_payment_id=payment_result.get("payment_id"),
        qr_code_data=payment_result.get("qr_code"),
        expires_at=payment_result.get("expires_at")
    )

    return PaymentResponse(
        transaction_id=db_transaction.id,
        qr_code_data=payment_result.get("qr_code"),
        payment_id=payment_result.get("payment_id"),
        expires_in_seconds=payment_result.get("expires_in_seconds"),
        expires_at=payment_result.get("expires_at")
    )


@router.get("/{transaction_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    transaction_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment status.

    User must be the shipper or motorista involved.

    Args:
        transaction_id: Transaction ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PaymentStatusResponse with current status
    """
    # Get transaction
    db_transaction = transaction_crud.get_transaction(db, transaction_id)
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Check authorization
    if current_user.id not in [db_transaction.shipper_id, db_transaction.motorista_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this transaction"
        )

    # If pending, check with Mercado Pago for updates
    if db_transaction.status == TransactionStatus.pendente and db_transaction.mp_payment_id:
        try:
            payment_info = verify_payment(db_transaction.mp_payment_id)
            if payment_info["status"] != TransactionStatus.pendente:
                # Update status if changed
                transaction_crud.update_transaction_status(
                    db, db_transaction.id, payment_info["status"]
                )
                db_transaction.status = payment_info["status"]
        except MercadoPagoError as e:
            logger.error(f"Error verifying payment: {str(e)}")
            # Continue with current status if verification fails

    # Check expiry
    if (db_transaction.status == TransactionStatus.pendente and
            db_transaction.expires_at and
            is_payment_expired(db_transaction.expires_at)):
        transaction_crud.update_transaction_status(
            db, db_transaction.id, TransactionStatus.expirado
        )
        db_transaction.status = TransactionStatus.expirado

    expires_in = (
        get_time_until_expiry(db_transaction.expires_at)
        if db_transaction.expires_at
        else None
    )

    return PaymentStatusResponse(
        transaction_id=db_transaction.id,
        status=db_transaction.status,
        amount=db_transaction.amount,
        qr_code_data=db_transaction.qr_code_data,
        expires_at=db_transaction.expires_at,
        created_at=db_transaction.created_at,
        updated_at=db_transaction.updated_at
    )


@router.post("/webhook/mercado-pago", status_code=status.HTTP_200_OK)
async def webhook_mercado_pago(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Mercado Pago notifications.

    Called when payment status changes (paid, failed, expired, etc.)

    Args:
        request: HTTP request with webhook payload
        db: Database session

    Returns:
        Success response for Mercado Pago
    """
    try:
        # Get payload
        payload = await request.json()
        signature = request.headers.get("X-Signature")

        # Handle webhook
        webhook_result = handle_webhook(payload, signature)

        if webhook_result.get("type") == "payment":
            payment_id = webhook_result.get("payment_id")

            # Get transaction by payment ID
            db_transaction = transaction_crud.get_transaction_by_mp_id(db, str(payment_id))
            if db_transaction:
                try:
                    # Verify payment status
                    payment_info = verify_payment(str(payment_id))

                    # Update transaction status
                    new_status = payment_info.get("status", TransactionStatus.pendente)
                    if new_status != db_transaction.status:
                        transaction_crud.update_transaction_status(db, db_transaction.id, new_status)
                        logger.info(f"Transaction {db_transaction.id} status updated to {new_status}")

                except MercadoPagoError as e:
                    logger.error(f"Error verifying payment {payment_id}: {str(e)}")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        # Always return 200 to Mercado Pago to prevent retries
        return {"status": "error", "message": str(e)}


@router.get("/{match_id}/receipt", response_model=ReceiptResponse)
def get_receipt(
    match_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get receipt after payment completed.

    Only accessible if transaction status is "pago".
    User must be shipper or motorista of the match.

    Args:
        match_id: Match ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        ReceiptResponse with payment details
    """
    # Get match
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Check authorization
    frete = db_match.frete
    is_motorista = frete.motorista_id == current_user.id
    is_shipper = db_match.shipper_id == current_user.id

    if not is_motorista and not is_shipper:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this receipt"
        )

    # Get transaction
    db_transaction = transaction_crud.get_transaction_by_match(db, match_id)
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transaction found for this match"
        )

    # Check if paid
    if db_transaction.status != TransactionStatus.pago:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment not completed. Current status: {db_transaction.status}"
        )

    return ReceiptResponse(
        transaction_id=db_transaction.id,
        match_id=match_id,
        amount=db_transaction.amount,
        status=db_transaction.status,
        payment_date=db_transaction.updated_at,
        motorista_id=db_transaction.motorista_id,
        shipper_id=db_transaction.shipper_id
    )


@router.get("/{transaction_id}/list", response_model=list[TransactionResponse])
def list_user_transactions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List transactions for the current user.

    If motorista: list transactions where they are the motorista
    If shipper: list transactions where they are the shipper

    Args:
        current_user: Current authenticated user
        db: Database session
        status_filter: Optional status filter
        limit: Max results
        offset: Pagination offset

    Returns:
        List of TransactionResponse
    """
    transactions = transaction_crud.list_transactions(
        db=db,
        user_id=current_user.id,
        user_type=current_user.tipo,
        status=status_filter,
        limit=limit,
        offset=offset
    )

    return transactions
