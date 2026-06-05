import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Frete, Match, Message, UserType, FreteStatus, MatchStatus
from app.crud.user import hash_password
from app.api.auth import create_access_token
from unittest.mock import patch, MagicMock

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def db():
    """Get database session for tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def motorista_user(db):
    """Create a motorista user"""
    user = User(
        email="motorista@test.com",
        password_hash=hash_password("password123"),
        tipo=UserType.motorista,
        nome="João Motorista",
        telefone="+5511987654321",
        cpf="12345678901"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def shipper_user(db):
    """Create a shipper user"""
    user = User(
        email="shipper@test.com",
        password_hash=hash_password("password123"),
        tipo=UserType.shipper,
        nome="Maria Shipper",
        telefone="+5511912345678",
        cpf="98765432109"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def frete(db, motorista_user):
    """Create a frete"""
    frete = Frete(
        motorista_id=motorista_user.id,
        origem="São Paulo",
        destino="Rio de Janeiro",
        peso_kg=100.0,
        valor_r=500.0,
        status=FreteStatus.disponivel,
        descricao="Teste frete"
    )
    db.add(frete)
    db.commit()
    db.refresh(frete)
    return frete

def get_auth_headers(user: User) -> dict:
    """Generate authorization headers for a user"""
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {access_token}"}

# ============ TESTS ============

def test_shipper_accepts_frete(db, motorista_user, shipper_user, frete):
    """Test that shipper can accept a frete and create a match"""
    headers = get_auth_headers(shipper_user)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["frete_id"] == frete.id
    assert data["shipper_id"] == shipper_user.id
    assert data["status"] == "pendente"
    assert data["valor_final"] == 500.0

def test_motorista_cannot_accept_own_frete(db, motorista_user, frete):
    """Test that motorista cannot accept their own frete"""
    headers = get_auth_headers(motorista_user)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    assert response.status_code == 403
    assert "Cannot accept your own frete" in response.json()["detail"]

def test_non_shipper_cannot_accept_frete(db, motorista_user, shipper_user):
    """Test that only shippers can accept fretes"""
    # Create another motorista
    another_motorista = User(
        email="motorista2@test.com",
        password_hash=hash_password("password123"),
        tipo=UserType.motorista,
        nome="Pedro Motorista",
        telefone="+5511912345678",
        cpf="11111111111"
    )
    db.add(another_motorista)
    db.commit()

    frete = Frete(
        motorista_id=motorista_user.id,
        origem="São Paulo",
        destino="Rio de Janeiro",
        peso_kg=100.0,
        valor_r=500.0,
        status=FreteStatus.disponivel,
        descricao="Teste frete"
    )
    db.add(frete)
    db.commit()

    headers = get_auth_headers(another_motorista)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    assert response.status_code == 403
    assert "Only shippers can accept fretes" in response.json()["detail"]

def test_cannot_accept_unavailable_frete(db, motorista_user, shipper_user):
    """Test that shipper cannot accept unavailable frete"""
    # Create unavailable frete
    frete = Frete(
        motorista_id=motorista_user.id,
        origem="São Paulo",
        destino="Rio de Janeiro",
        peso_kg=100.0,
        valor_r=500.0,
        status=FreteStatus.aceito,  # Already accepted
        descricao="Teste frete"
    )
    db.add(frete)
    db.commit()

    headers = get_auth_headers(shipper_user)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    assert response.status_code == 400
    assert "not available" in response.json()["detail"]

def test_cannot_accept_same_frete_twice(db, motorista_user, shipper_user, frete):
    """Test that shipper cannot accept the same frete twice"""
    headers = get_auth_headers(shipper_user)

    # First acceptance should succeed
    response1 = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )
    assert response1.status_code == 201

    # Second acceptance should fail
    response2 = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )
    assert response2.status_code == 400
    assert "already accepted" in response2.json()["detail"]

def test_list_motorista_matches(db, motorista_user, shipper_user, frete):
    """Test that motorista sees their match"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(motorista_user)

    response = client.get(
        "/api/matches",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == match.id
    assert data[0]["frete_id"] == frete.id

def test_list_shipper_matches(db, motorista_user, shipper_user, frete):
    """Test that shipper sees their matches"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(shipper_user)

    response = client.get(
        "/api/matches",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["shipper_id"] == shipper_user.id

def test_get_match_detail(db, motorista_user, shipper_user, frete):
    """Test getting match detail"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(motorista_user)

    response = client.get(
        f"/api/matches/{match.id}",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == match.id
    assert data["status"] == "pendente"
    assert "messages" in data
    assert isinstance(data["messages"], list)

def test_unauthorized_cannot_view_match(db, motorista_user, shipper_user, frete):
    """Test that unauthorized user cannot view match"""
    # Create another user
    other_user = User(
        email="other@test.com",
        password_hash=hash_password("password123"),
        tipo=UserType.shipper,
        nome="Other User",
        telefone="+5511912345678",
        cpf="22222222222"
    )
    db.add(other_user)
    db.commit()

    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(other_user)

    response = client.get(
        f"/api/matches/{match.id}",
        headers=headers
    )

    assert response.status_code == 403

def test_update_match_status(db, motorista_user, shipper_user, frete):
    """Test updating match status"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(motorista_user)

    response = client.put(
        f"/api/matches/{match.id}/status",
        json={"status": "aceito"},
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "aceito"

def test_shipper_cannot_update_status(db, motorista_user, shipper_user, frete):
    """Test that shipper cannot update match status"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(shipper_user)

    response = client.put(
        f"/api/matches/{match.id}/status",
        json={"status": "aceito"},
        headers=headers
    )

    assert response.status_code == 403

def test_send_message(db, motorista_user, shipper_user, frete):
    """Test sending a message in match chat"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    headers = get_auth_headers(motorista_user)

    response = client.post(
        f"/api/matches/{match.id}/messages",
        json={"conteudo": "Oi, tudo bem com o frete?"},
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["conteudo"] == "Oi, tudo bem com o frete?"
    assert data["sender_id"] == motorista_user.id
    assert data["match_id"] == match.id

def test_get_messages(db, motorista_user, shipper_user, frete):
    """Test getting messages from match chat"""
    # Create match
    match = Match(
        frete_id=frete.id,
        shipper_id=shipper_user.id,
        status=MatchStatus.pendente,
        valor_final=500.0
    )
    db.add(match)
    db.commit()

    # Add messages
    msg1 = Message(
        match_id=match.id,
        sender_id=motorista_user.id,
        conteudo="Primeira mensagem"
    )
    msg2 = Message(
        match_id=match.id,
        sender_id=shipper_user.id,
        conteudo="Segunda mensagem"
    )
    db.add_all([msg1, msg2])
    db.commit()

    headers = get_auth_headers(motorista_user)

    response = client.get(
        f"/api/matches/{match.id}/messages",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["conteudo"] == "Primeira mensagem"
    assert data[1]["conteudo"] == "Segunda mensagem"

@patch('app.api.matches.send_whatsapp_notification')
def test_whatsapp_notification_called_on_accept(mock_whatsapp, db, motorista_user, shipper_user, frete):
    """Test that WhatsApp notification is sent when match is created"""
    mock_whatsapp.return_value = True

    headers = get_auth_headers(shipper_user)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    assert response.status_code == 201
    # Verify send_whatsapp_notification was called
    assert mock_whatsapp.called
    call_args = mock_whatsapp.call_args
    assert motorista_user.telefone in str(call_args)

@patch('app.api.matches.send_whatsapp_notification')
def test_whatsapp_failure_doesnt_crash(mock_whatsapp, db, motorista_user, shipper_user, frete):
    """Test that WhatsApp failure doesn't crash the API"""
    mock_whatsapp.side_effect = Exception("Twilio error")

    headers = get_auth_headers(shipper_user)

    response = client.post(
        "/api/matches",
        json={"frete_id": frete.id},
        headers=headers
    )

    # Should still return 201 even if WhatsApp fails
    assert response.status_code == 201
    assert response.json()["id"] is not None

def test_unauthorized_access_denied(db, motorista_user):
    """Test that unauthorized access is denied"""
    response = client.get("/api/matches")

    assert response.status_code == 403 or response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
