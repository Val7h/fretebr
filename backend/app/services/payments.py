"""
Mercado Pago Pix Payment Service
Handles all payment processing and QR code generation for FreteBR
"""

import os
import json
import hmac
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Mercado Pago Configuration
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN", "")
MERCADO_PAGO_WEBHOOK_SECRET = os.getenv("MERCADO_PAGO_WEBHOOK_SECRET", "")
MERCADO_PAGO_ENVIRONMENT = os.getenv("MERCADO_PAGO_ENVIRONMENT", "sandbox")

# API URLs
if MERCADO_PAGO_ENVIRONMENT == "production":
    MERCADO_PAGO_API_URL = "https://api.mercadopago.com/v1"
else:
    MERCADO_PAGO_API_URL = "https://api.mercadopago.com/v1"  # Same endpoint for both


class MercadoPagoError(Exception):
    """Custom exception for Mercado Pago errors"""
    pass


def send_payment_request(
    amount: float,
    match_id: int,
    shipper_email: str,
    shipper_name: str,
    shipper_phone: str,
    expiry_minutes: int = 30
) -> Dict:
    """
    Send a payment request to Mercado Pago and generate Pix QR code.

    Args:
        amount: Payment amount in BRL
        match_id: FreteBR match ID
        shipper_email: Shipper email
        shipper_name: Shipper name
        shipper_phone: Shipper phone
        expiry_minutes: QR code expiry time in minutes

    Returns:
        Dictionary with:
        - qr_code: QR code data (string)
        - payment_id: Mercado Pago payment ID
        - expires_at: Expiry datetime
        - expires_in_seconds: Seconds until expiry

    Raises:
        MercadoPagoError: If payment request fails
    """
    # MODO MOCK: se nao tem credencial MP valida, gera Pix simulado (dev/staging)
    # Considera placeholder/x's como ausente
    def _is_placeholder(tok: str) -> bool:
        if not tok:
            return True
        t = tok.strip().lower()
        if not t:
            return True
        # Detectar placeholders comuns
        if "xxx" in t or "your" in t or "change" in t or "placeholder" in t:
            return True
        if len(t) < 20:
            return True
        return False

    if _is_placeholder(MERCADO_PAGO_ACCESS_TOKEN):
        logger.warning("[MOCK] MERCADO_PAGO_ACCESS_TOKEN ausente/placeholder - gerando Pix MOCK")
        import uuid as _uuid
        mock_payment_id = f"MOCK_{_uuid.uuid4().hex[:16]}"
        mock_qr = generate_pix_qr_fallback(mock_payment_id, amount)
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        return {
            "qr_code": mock_qr,
            "payment_id": mock_payment_id,
            "expires_at": expires_at,
            "expires_in_seconds": int(expiry_minutes * 60),
            "status": "pending",
            "mock": True,
        }

    try:
        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        expires_in_seconds = int(expiry_minutes * 60)

        # Prepare payment request payload
        payload = {
            "transaction_amount": amount,
            "description": f"Frete FreteBR - Match {match_id}",
            "payment_method_id": "pix",
            "payer": {
                "email": shipper_email,
                "first_name": shipper_name.split()[0],
                "last_name": " ".join(shipper_name.split()[1:]) if len(shipper_name.split()) > 1 else ".",
                "phone": {
                    "area_code": shipper_phone[:2] if len(shipper_phone) >= 2 else "11",
                    "number": shipper_phone.replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
                }
            },
            "notification_url": os.getenv("WEBHOOK_URL", "http://localhost:8000/api/webhook/mercado-pago"),
            "external_reference": f"fretebr_match_{match_id}",
            "metadata": {
                "match_id": match_id,
                "service": "fretebr"
            }
        }

        # Make request to Mercado Pago API
        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{MERCADO_PAGO_API_URL}/payments",
            json=payload,
            headers=headers,
            timeout=10
        )

        # Check response status
        if response.status_code not in [200, 201]:
            logger.error(f"Mercado Pago API error: {response.status_code} - {response.text}")
            raise MercadoPagoError(f"Payment request failed: {response.text}")

        payment_data = response.json()

        # Extract QR code from response
        qr_code = None
        if "point_of_interaction" in payment_data:
            poi = payment_data["point_of_interaction"]
            if "transaction_data" in poi and "qr_code" in poi["transaction_data"]:
                qr_code = poi["transaction_data"]["qr_code"]

        if not qr_code:
            logger.warning(f"No QR code in Mercado Pago response: {payment_data}")
            # Generate a fallback QR code if Mercado Pago doesn't provide one
            qr_code = generate_pix_qr_fallback(payment_data.get("id", match_id), amount)

        return {
            "qr_code": qr_code,
            "payment_id": payment_data.get("id"),
            "expires_at": expires_at,
            "expires_in_seconds": expires_in_seconds,
            "status": payment_data.get("status", "pending")
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error calling Mercado Pago: {str(e)}")
        raise MercadoPagoError(f"Failed to connect to Mercado Pago: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in send_payment_request: {str(e)}")
        raise MercadoPagoError(f"Unexpected error: {str(e)}")


def verify_payment(mp_payment_id: str) -> Dict:
    """
    Verify payment status with Mercado Pago.

    Args:
        mp_payment_id: Mercado Pago payment ID

    Returns:
        Dictionary with payment status and details

    Raises:
        MercadoPagoError: If verification fails
    """
    # MODO MOCK
    def _is_placeholder(tok: str) -> bool:
        if not tok or not tok.strip(): return True
        t = tok.strip().lower()
        return "xxx" in t or "your" in t or len(t) < 20
    if _is_placeholder(MERCADO_PAGO_ACCESS_TOKEN) or str(mp_payment_id).startswith("MOCK_"):
        logger.info(f"[MOCK] verify_payment({mp_payment_id}) - retornando pending")
        return {
            "status": "pendente",
            "payment_id": mp_payment_id,
            "mock": True,
        }

    try:
        headers = {
            "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{MERCADO_PAGO_API_URL}/payments/{mp_payment_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            logger.error(f"Mercado Pago verification error: {response.status_code} - {response.text}")
            raise MercadoPagoError(f"Verification failed: {response.text}")

        payment_data = response.json()

        # Map Mercado Pago status to our status
        mp_status = payment_data.get("status", "pending")
        our_status = map_mp_status_to_our_status(mp_status)

        return {
            "status": our_status,
            "mp_status": mp_status,
            "payment_id": payment_data.get("id"),
            "amount": payment_data.get("transaction_amount"),
            "payer_email": payment_data.get("payer", {}).get("email"),
            "paid_at": payment_data.get("date_approved")
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error in verify_payment: {str(e)}")
        raise MercadoPagoError(f"Failed to verify payment: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in verify_payment: {str(e)}")
        raise MercadoPagoError(f"Unexpected error: {str(e)}")


def handle_webhook(payload: Dict, signature: Optional[str] = None) -> Dict:
    """
    Handle webhook from Mercado Pago.

    Args:
        payload: Webhook payload from Mercado Pago
        signature: Webhook signature for verification

    Returns:
        Dictionary with webhook processing result

    Raises:
        MercadoPagoError: If webhook is invalid
    """
    try:
        # Verify webhook signature if secret is configured
        if MERCADO_PAGO_WEBHOOK_SECRET and signature:
            if not verify_webhook_signature(payload, signature):
                raise MercadoPagoError("Invalid webhook signature")

        # Extract event data
        event_type = payload.get("type", "")
        payment_id = payload.get("data", {}).get("id")
        action = payload.get("action", "")

        if not payment_id:
            logger.warning(f"Webhook received without payment ID: {payload}")
            return {"status": "ignored", "reason": "no_payment_id"}

        # Handle payment notifications
        if event_type == "payment" or action == "payment.created":
            return {
                "status": "processed",
                "type": "payment",
                "payment_id": payment_id,
                "action_required": "fetch_payment_status"
            }

        logger.info(f"Webhook received: type={event_type}, action={action}, payment_id={payment_id}")
        return {"status": "received"}

    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise MercadoPagoError(f"Webhook processing failed: {str(e)}")


def verify_webhook_signature(payload: Dict, signature: str) -> bool:
    """
    Verify webhook signature from Mercado Pago.

    Args:
        payload: Webhook payload
        signature: Webhook signature

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        payload_string = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        expected_signature = hmac.new(
            MERCADO_PAGO_WEBHOOK_SECRET.encode(),
            payload_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {str(e)}")
        return False


def generate_pix_qr_fallback(reference_id: str, amount: float) -> str:
    """
    Generate a fallback QR code data for Pix.
    This is used if Mercado Pago doesn't provide one.

    Args:
        reference_id: Reference ID (payment ID or match ID)
        amount: Payment amount

    Returns:
        QR code data string
    """
    # Format: reference_id|amount|timestamp
    # In production, this should be a proper Pix QR code
    timestamp = datetime.utcnow().isoformat()
    qr_code = f"00020126360014br.gov.bcb.pix0136{reference_id}|{amount}|{timestamp}"
    return qr_code


def map_mp_status_to_our_status(mp_status: str) -> str:
    """
    Map Mercado Pago status to our transaction status.

    Args:
        mp_status: Mercado Pago status

    Returns:
        Our transaction status
    """
    status_map = {
        "pending": "pendente",
        "approved": "pago",
        "authorized": "pago",
        "in_process": "pendente",
        "in_mediation": "pendente",
        "rejected": "falhou",
        "cancelled": "cancelado",
        "refunded": "cancelado",
        "charged_back": "falhou",
    }
    return status_map.get(mp_status, "pendente")


def is_payment_expired(expires_at: datetime) -> bool:
    """
    Check if payment has expired.

    Args:
        expires_at: Payment expiry datetime

    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expires_at


def get_time_until_expiry(expires_at: datetime) -> int:
    """
    Get seconds until payment expires.

    Args:
        expires_at: Payment expiry datetime

    Returns:
        Seconds until expiry (0 if expired)
    """
    if is_payment_expired(expires_at):
        return 0
    delta = expires_at - datetime.utcnow()
    return max(0, int(delta.total_seconds()))
