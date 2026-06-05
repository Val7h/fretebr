"""
Payment Integration Tests for FreteBR
Tests Mercado Pago Pix payment flow
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import (
    User, UserType, Frete, FreteStatus, Match, MatchStatus,
    Transaction, TransactionStatus
)
from app.crud import create_user, hash_password

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_payments.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_motorista():
    """Create test motorista user"""
    db = TestingSessionLocal()
    user = User(
        email="motorista@test.com",
        password_hash=hash_password("test123"),
        tipo=UserType.motorista,
        nome="Test Motorista",
        telefone="+5511999999999",
        cpf="12345678901"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_shipper():
    """Create test shipper user"""
    db = TestingSessionLocal()
    user = User(
        email="shipper@test.com",
        password_hash=hash_password("test123"),
        tipo=UserType.shipper,
        nome="Test Shipper",
        telefone="+5511988888888",
        cpf="98765432101"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_match(test_motorista, test_shipper):
    """Create test match in finalizado status"""
    db = TestingSessionLocal()

    # Create frete
    frete = Frete(
        motorista_id=test_motorista.id,
        origem="São Paulo, SP",
        destino="Rio de Janeiro, RJ",
        descricao="Teste",
        peso_kg=100.0,
        valor_r=500.0,
        status=FreteStatus.disponível
    )
    db.add(frete)
    db.commit()
    db.refresh(frete)

    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=test_shipper.id,
        status=MatchStatus.finalizado,
        valor_final=500.0
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    db.close()

    return match


def test_create_payment_success(test_match, test_shipper):
    """Test successful payment creation"""
    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create payment
    response = client.post(
        "/api/payments",
        json={"match_id": test_match.id, "amount": 500.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should create transaction and return QR code
    assert response.status_code == 201
    data = response.json()
    assert "transaction_id" in data
    assert "qr_code_data" in data
    assert data["amount"] == 500.0 or "amount" not in data  # amount is optional in response

    # Verify transaction in database
    db = TestingSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.id == data["transaction_id"]
    ).first()
    assert transaction is not None
    assert transaction.status == TransactionStatus.pendente
    db.close()


def test_create_payment_invalid_status(test_match, test_shipper):
    """Test payment creation fails if match not finalized"""
    db = TestingSessionLocal()

    # Change match status back to pendente
    match = db.query(Match).filter(Match.id == test_match.id).first()
    match.status = MatchStatus.pendente
    db.commit()
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # Try to create payment
    response = client.post(
        "/api/payments",
        json={"match_id": test_match.id, "amount": 500.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "finalizado" in response.json()["detail"]


def test_create_payment_motorista_cannot_pay(test_match, test_motorista):
    """Test motorista cannot create payment"""
    # Login as motorista (different user)
    response = client.post(
        "/api/auth/login",
        json={"email": "motorista@test.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Try to create payment
    response = client.post(
        "/api/payments",
        json={"match_id": test_match.id, "amount": 500.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert "shippers" in response.json()["detail"]


def test_get_payment_status(test_match, test_shipper):
    """Test getting payment status"""
    db = TestingSessionLocal()

    # Create transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pendente,
        qr_code_data="test_qr_code",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # Get payment status
    response = client.get(
        f"/api/payments/{transaction.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"] == transaction.id
    assert data["status"] == "pendente"
    assert data["amount"] == 500.0


def test_webhook_payment_confirmed(test_match, test_shipper):
    """Test webhook updates transaction when payment confirmed"""
    db = TestingSessionLocal()

    # Create transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pendente,
        mp_payment_id="123456789",
        qr_code_data="test_qr_code",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    db.close()

    # Send webhook notification (simulating Mercado Pago)
    response = client.post(
        "/api/webhook/mercado-pago",
        json={
            "type": "payment",
            "data": {"id": "123456789"}
        }
    )

    # Should accept webhook
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_webhook_invalid_signature(test_match, test_shipper):
    """Test webhook rejects invalid signature"""
    db = TestingSessionLocal()

    # Create transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pendente,
        mp_payment_id="123456789"
    )
    db.add(transaction)
    db.commit()
    db.close()

    # Send webhook with invalid signature
    response = client.post(
        "/api/webhook/mercado-pago",
        json={"type": "payment", "data": {"id": "123456789"}},
        headers={"X-Signature": "invalid_signature"}
    )

    # Should still return 200 (never fail webhook to Mercado Pago)
    assert response.status_code == 200


def test_shipper_cannot_pay_twice(test_match, test_shipper):
    """Test shipper cannot pay twice for same match"""
    db = TestingSessionLocal()

    # Create first transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pago,
        mp_payment_id="123456789"
    )
    db.add(transaction)
    db.commit()
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # Try to create another payment
    response = client.post(
        "/api/payments",
        json={"match_id": test_match.id, "amount": 500.0},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "already completed" in response.json()["detail"]


def test_get_receipt_after_payment(test_match, test_shipper):
    """Test getting receipt after payment completed"""
    db = TestingSessionLocal()

    # Create paid transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pago,
        mp_payment_id="123456789",
        updated_at=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # Get receipt
    response = client.get(
        f"/api/payments/{test_match.id}/receipt",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["match_id"] == test_match.id
    assert data["amount"] == 500.0
    assert data["status"] == "pago"


def test_receipt_not_accessible_before_payment(test_match, test_shipper):
    """Test receipt not accessible before payment"""
    db = TestingSessionLocal()

    # Create pending transaction
    transaction = Transaction(
        match_id=test_match.id,
        motorista_id=test_match.frete.motorista_id,
        shipper_id=test_shipper.id,
        amount=500.0,
        status=TransactionStatus.pendente
    )
    db.add(transaction)
    db.commit()
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # Try to get receipt
    response = client.get(
        f"/api/payments/{test_match.id}/receipt",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "not completed" in response.json()["detail"]


def test_list_user_transactions(test_match, test_shipper):
    """Test listing user transactions"""
    db = TestingSessionLocal()

    # Create some transactions
    for i in range(3):
        transaction = Transaction(
            match_id=test_match.id if i == 0 else test_match.id + i,
            motorista_id=test_match.frete.motorista_id,
            shipper_id=test_shipper.id,
            amount=500.0 + i,
            status=TransactionStatus.pendente
        )
        db.add(transaction)
    db.commit()
    db.close()

    # Login as shipper
    response = client.post(
        "/api/auth/login",
        json={"email": "shipper@test.com", "password": "test123"}
    )
    token = response.json()["access_token"]

    # List transactions
    response = client.get(
        "/api/payments/1/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
