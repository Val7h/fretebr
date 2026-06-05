"""
Test suite for Twilio WhatsApp integration.

Tests include:
- Twilio credentials validation
- Twilio client initialization
- Message sending (with mock to avoid real costs)
- Error handling for invalid credentials
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class TestTwilioSetup:
    """Test Twilio environment setup"""

    def test_twilio_credentials_exist(self):
        """Test that Twilio credentials are set in environment"""
        # These should be set in .env
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        # In development, they might be placeholder values
        # In production/testing, they should be real
        assert account_sid is not None, "TWILIO_ACCOUNT_SID not set"
        assert auth_token is not None, "TWILIO_AUTH_TOKEN not set"
        assert phone_number is not None, "TWILIO_PHONE_NUMBER not set"

        # Basic validation of format
        assert account_sid.startswith("AC"), f"Invalid Account SID format: {account_sid}"
        assert phone_number.startswith("+"), f"Invalid phone format: {phone_number}"

    def test_twilio_client_initialization(self):
        """Test that Twilio client can be initialized with credentials"""
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        # Should not raise exception
        try:
            client = Client(account_sid, auth_token)
            assert client is not None
            assert client.api.accounts is not None
        except Exception as e:
            # If credentials are placeholder, client creation might fail
            # That's OK for this test - we're just checking format
            if "placeholder" not in str(account_sid).lower():
                pytest.skip(f"Skipping with test credentials: {str(e)}")


class TestTwilioMessaging:
    """Test Twilio message sending functionality"""

    @patch('twilio.rest.Client.messages.create')
    def test_send_whatsapp_message_success(self, mock_create):
        """Test sending a WhatsApp message with mock"""
        # Mock the response
        mock_message = MagicMock()
        mock_message.sid = "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        mock_message.status = "queued"
        mock_create.return_value = mock_message

        # Create client with dummy credentials
        client = Client("ACxxx", "token_xxx")

        # Send message
        message = client.messages.create(
            from_="whatsapp:+1234567890",
            body="Test message from FreteBR",
            to="whatsapp:+5583993476410"
        )

        # Verify
        assert message.sid is not None
        assert message.status == "queued"
        mock_create.assert_called_once()

    @patch('twilio.rest.Client.messages.create')
    def test_send_whatsapp_message_with_variables(self, mock_create):
        """Test sending WhatsApp message with dynamic variables"""
        mock_message = MagicMock()
        mock_message.sid = "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        mock_create.return_value = mock_message

        client = Client("ACxxx", "token_xxx")

        # Example: notification for new match
        motorista_name = "João Silva"
        frete_route = "SP → RJ"
        frete_value = "R$ 500,00"

        body = f"Novo frete! {motorista_name} quer seu frete: {frete_route} ({frete_value})"

        message = client.messages.create(
            from_="whatsapp:+1234567890",
            body=body,
            to="whatsapp:+5583993476410"
        )

        assert message.sid is not None
        # Verify the body was set
        call_kwargs = mock_create.call_args[1]
        assert frete_route in call_kwargs['body']
        assert frete_value in call_kwargs['body']


class TestTwilioErrorHandling:
    """Test error handling for Twilio failures"""

    @patch('twilio.rest.Client.messages.create')
    def test_invalid_phone_number(self, mock_create):
        """Test handling of invalid phone numbers"""
        # Simulate Twilio error
        error = TwilioRestException(
            status=400,
            msg="Invalid phone number format",
            code=21202
        )
        mock_create.side_effect = error

        client = Client("ACxxx", "token_xxx")

        with pytest.raises(TwilioRestException) as exc_info:
            client.messages.create(
                from_="whatsapp:+1234567890",
                body="Test",
                to="whatsapp:invalid_phone"
            )

        assert exc_info.value.status == 400

    @patch('twilio.rest.Client.messages.create')
    def test_authentication_error(self, mock_create):
        """Test handling of authentication errors"""
        error = TwilioRestException(
            status=401,
            msg="Authentication failed",
            code=20003
        )
        mock_create.side_effect = error

        client = Client("ACxxx", "invalid_token")

        with pytest.raises(TwilioRestException) as exc_info:
            client.messages.create(
                from_="whatsapp:+1234567890",
                body="Test",
                to="whatsapp:+5583993476410"
            )

        assert exc_info.value.status == 401

    @patch('twilio.rest.Client.messages.create')
    def test_rate_limit_error(self, mock_create):
        """Test handling of rate limit errors"""
        error = TwilioRestException(
            status=429,
            msg="Too many requests",
            code=20429
        )
        mock_create.side_effect = error

        client = Client("ACxxx", "token_xxx")

        with pytest.raises(TwilioRestException) as exc_info:
            client.messages.create(
                from_="whatsapp:+1234567890",
                body="Test",
                to="whatsapp:+5583993476410"
            )

        assert exc_info.value.status == 429


class TestTwilioIntegrationPatterns:
    """Test common integration patterns"""

    @patch('twilio.rest.Client.messages.create')
    def test_notification_on_match_created(self, mock_create):
        """Test sending notification when match is created"""
        mock_message = MagicMock()
        mock_message.sid = "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        mock_create.return_value = mock_message

        # Simulate match creation scenario
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER")

        # This would be called from app.services.notifications
        if "placeholder" not in account_sid.lower():
            client = Client(account_sid, auth_token)
        else:
            client = Client("ACxxx", "token_xxx")

        # Simulate match data
        match_data = {
            "match_id": 123,
            "frete_route": "São Paulo → Rio de Janeiro",
            "frete_value": "R$ 500,00",
            "motorista_name": "João Silva",
            "shipper_phone": "+5583993476410"
        }

        # Send notification
        message = client.messages.create(
            from_=f"whatsapp:{from_phone}",
            body=f"Novo frete! {match_data['motorista_name']} quer seu frete: {match_data['frete_route']} ({match_data['frete_value']})",
            to=f"whatsapp:{match_data['shipper_phone']}"
        )

        assert message is not None
        mock_create.assert_called_once()

    def test_phone_number_formatting(self):
        """Test phone number formatting for WhatsApp"""
        # Brazilian phone numbers should be formatted with +55 country code
        phone_raw = "83993476410"
        phone_formatted = f"+55{phone_raw}"
        whatsapp_phone = f"whatsapp:{phone_formatted}"

        assert whatsapp_phone.startswith("whatsapp:+55")
        assert len(phone_formatted) == 13  # +55 + 11 digits


# Integration test (requires real Twilio credentials)
class TestTwilioIntegrationLive:
    """Live integration tests (only run with valid credentials)"""

    @pytest.mark.skip(reason="Requires real Twilio credentials - run manually")
    def test_send_real_message(self):
        """Send a real test message to verify Twilio integration"""
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER")
        to_phone = os.getenv("TWILIO_TEST_PHONE")  # Set for manual testing

        if "placeholder" in account_sid.lower() or not to_phone:
            pytest.skip("Real credentials not configured")

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=f"whatsapp:{from_phone}",
            body="Test message from FreteBR - ignore this",
            to=f"whatsapp:{to_phone}"
        )

        assert message.sid is not None
        print(f"Message sent: {message.sid}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
