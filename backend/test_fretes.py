"""
Test suite for FreteBR Frete API endpoints
"""
import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserType
from app.models.frete import Frete, FreteStatus

# Create a test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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

# Helper function to generate unique emails
def get_unique_email(prefix):
    return f"{prefix}_{int(time.time() * 1000)}@test.com"

def get_unique_cpf(base):
    return f"{base}{int(time.time() * 1000) % 100000:05d}"

# Fixtures
@pytest.fixture
def setup_users():
    """Create test users (motorista and shipper)"""
    # Create motorista
    motorista_response = client.post(
        "/api/auth/signup",
        json={
            "email": get_unique_email("motorista"),
            "password": "test123456",
            "tipo": "motorista",
            "nome": "Test Motorista",
            "telefone": "11999999999",
            "cpf": get_unique_cpf("123456789")
        }
    )
    assert motorista_response.status_code == 200, f"Failed to create motorista: {motorista_response.json()}"
    motorista_token = motorista_response.json()["access_token"]

    # Create shipper
    shipper_response = client.post(
        "/api/auth/signup",
        json={
            "email": get_unique_email("shipper"),
            "password": "test123456",
            "tipo": "shipper",
            "nome": "Test Shipper",
            "telefone": "11999999998",
            "cpf": get_unique_cpf("987654321")
        }
    )
    assert shipper_response.status_code == 200, f"Failed to create shipper: {shipper_response.json()}"
    shipper_token = shipper_response.json()["access_token"]

    return {
        "motorista_token": motorista_token,
        "shipper_token": shipper_token
    }

@pytest.fixture
def frete_data():
    """Sample frete data"""
    return {
        "origem": "São Paulo, SP",
        "destino": "Rio de Janeiro, RJ",
        "peso_kg": 1500.0,
        "valor_r": 5000.0,
        "descricao": "Frete de carga geral"
    }

# Tests
class TestFreteCreation:
    def test_create_frete_as_motorista(self, setup_users, frete_data):
        """Test creating a frete as motorista (should succeed with 201)"""
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        response = client.post("/api/fretes", json=frete_data, headers=headers)

        assert response.status_code == 201
        data = response.json()
        assert data["origem"] == frete_data["origem"]
        assert data["status"] == "disponível"
        assert data["motorista_id"] is not None

    def test_create_frete_as_shipper(self, setup_users, frete_data):
        """Test creating a frete as shipper (should fail with 403)"""
        headers = {"Authorization": f"Bearer {setup_users['shipper_token']}"}
        response = client.post("/api/fretes", json=frete_data, headers=headers)

        assert response.status_code == 403
        assert "motoristas" in response.json()["detail"].lower()

    def test_create_frete_without_auth(self, frete_data):
        """Test creating a frete without authentication (should fail with 403)"""
        response = client.post("/api/fretes", json=frete_data)

        assert response.status_code == 403

class TestFreteRetrieval:
    def test_list_available_fretes(self, setup_users, frete_data):
        """Test getting list of available fretes"""
        # Create a frete
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        client.post("/api/fretes", json=frete_data, headers=headers)

        # List fretes
        response = client.get("/api/fretes")

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["status"] == "disponível"

    def test_get_single_frete(self, setup_users, frete_data):
        """Test getting a single frete by ID"""
        # Create a frete
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        create_response = client.post("/api/fretes", json=frete_data, headers=headers)
        frete_id = create_response.json()["id"]

        # Get single frete
        response = client.get(f"/api/fretes/{frete_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == frete_id
        assert data["origem"] == frete_data["origem"]

    def test_get_nonexistent_frete(self):
        """Test getting a nonexistent frete (should fail with 404)"""
        response = client.get("/api/fretes/99999")

        assert response.status_code == 404

    def test_get_meus_fretes_motorista(self, setup_users, frete_data):
        """Test motorista getting their own fretes"""
        # Create multiple fretes
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        client.post("/api/fretes", json=frete_data, headers=headers)
        client.post("/api/fretes", json=frete_data, headers=headers)

        # Get meus-fretes
        response = client.get("/api/fretes/meus-fretes", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_get_meus_fretes_shipper(self, setup_users):
        """Test shipper cannot access meus-fretes (should fail with 403)"""
        headers = {"Authorization": f"Bearer {setup_users['shipper_token']}"}
        response = client.get("/api/fretes/meus-fretes", headers=headers)

        assert response.status_code == 403

class TestFreteUpdate:
    def test_update_own_frete(self, setup_users, frete_data):
        """Test motorista updating their own frete"""
        # Create frete
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        create_response = client.post("/api/fretes", json=frete_data, headers=headers)
        frete_id = create_response.json()["id"]

        # Update frete
        update_data = {"valor_r": 5500.0}
        response = client.put(f"/api/fretes/{frete_id}", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valor_r"] == 5500.0

    def test_update_other_frete(self, setup_users, frete_data):
        """Test motorista cannot update other motorista's frete"""
        # Create motorista 1 frete
        headers1 = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        create_response = client.post("/api/fretes", json=frete_data, headers=headers1)
        frete_id = create_response.json()["id"]

        # Create motorista 2
        motorista2_response = client.post(
            "/api/auth/signup",
            json={
                "email": get_unique_email("motorista2"),
                "password": "test123456",
                "tipo": "motorista",
                "nome": "Test Motorista 2",
                "telefone": "11999999997",
                "cpf": get_unique_cpf("111111111")
            }
        )
        motorista2_token = motorista2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {motorista2_token}"}

        # Try to update motorista1's frete
        update_data = {"valor_r": 5500.0}
        response = client.put(f"/api/fretes/{frete_id}", json=update_data, headers=headers2)

        assert response.status_code == 403

    def test_update_nonexistent_frete(self, setup_users):
        """Test updating a nonexistent frete (should fail with 404)"""
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        response = client.put(f"/api/fretes/99999", json={"valor_r": 5500}, headers=headers)

        assert response.status_code == 404

class TestFreteDeletion:
    def test_delete_own_frete(self, setup_users, frete_data):
        """Test motorista deleting their own frete"""
        # Create frete
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        create_response = client.post("/api/fretes", json=frete_data, headers=headers)
        frete_id = create_response.json()["id"]

        # Delete frete
        response = client.delete(f"/api/fretes/{frete_id}", headers=headers)

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/fretes/{frete_id}")
        assert get_response.status_code == 404

    def test_delete_other_frete(self, setup_users, frete_data):
        """Test motorista cannot delete other motorista's frete"""
        # Create motorista 1 frete
        headers1 = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        create_response = client.post("/api/fretes", json=frete_data, headers=headers1)
        frete_id = create_response.json()["id"]

        # Create motorista 2
        motorista2_response = client.post(
            "/api/auth/signup",
            json={
                "email": get_unique_email("motorista3"),
                "password": "test123456",
                "tipo": "motorista",
                "nome": "Test Motorista 3",
                "telefone": "11999999996",
                "cpf": get_unique_cpf("222222222")
            }
        )
        motorista2_token = motorista2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {motorista2_token}"}

        # Try to delete motorista1's frete
        response = client.delete(f"/api/fretes/{frete_id}", headers=headers2)

        assert response.status_code == 403

    def test_delete_nonexistent_frete(self, setup_users):
        """Test deleting a nonexistent frete (should fail with 404)"""
        headers = {"Authorization": f"Bearer {setup_users['motorista_token']}"}
        response = client.delete(f"/api/fretes/99999", headers=headers)

        assert response.status_code == 404
