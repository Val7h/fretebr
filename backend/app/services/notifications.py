import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def send_whatsapp_notification(phone_number: str, message: str) -> bool:
    """
    Send a WhatsApp notification via Twilio.

    Args:
        phone_number: Recipient phone number (with country code, e.g. +55XXXXXXXXXXXX)
        message: Message content to send

    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        # Import Twilio client
        from twilio.rest import Client

        # Get credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_whatsapp_number = os.getenv("TWILIO_PHONE_NUMBER")

        # Validate credentials are configured
        if not account_sid or not auth_token or not twilio_whatsapp_number:
            logger.warning(
                "Twilio credentials not configured. "
                "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER in .env"
            )
            return False

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Send message via WhatsApp
        # Format: whatsapp:+XXXXXXXXXXX
        response = client.messages.create(
            from_=f"whatsapp:{twilio_whatsapp_number}",
            to=f"whatsapp:{phone_number}",
            body=message
        )

        logger.info(
            f"WhatsApp notification sent successfully. "
            f"Message SID: {response.sid}, To: {phone_number}"
        )
        return True

    except ImportError:
        logger.error(
            "Twilio package not installed. "
            "Run: pip install twilio==9.2.1"
        )
        return False

    except Exception as e:
        logger.error(
            f"Failed to send WhatsApp notification: {type(e).__name__}: {str(e)}"
        )
        return False

def send_sms_notification(phone_number: str, message: str) -> bool:
    """
    Send an SMS notification via Twilio (fallback if WhatsApp fails).

    Args:
        phone_number: Recipient phone number (with country code, e.g. +55XXXXXXXXXXXX)
        message: Message content to send

    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        from twilio.rest import Client

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not account_sid or not auth_token or twilio_phone_number:
            logger.warning("Twilio credentials not configured")
            return False

        client = Client(account_sid, auth_token)

        response = client.messages.create(
            from_=twilio_phone_number,
            to=phone_number,
            body=message
        )

        logger.info(
            f"SMS notification sent successfully. "
            f"Message SID: {response.sid}, To: {phone_number}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to send SMS notification: {str(e)}")
        return False
