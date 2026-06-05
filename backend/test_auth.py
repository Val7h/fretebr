import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
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

def setup_function():
    """Clean database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

class TestHealth:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

class TestAuth:
    def test_signup(self):
        """Test user signup"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.com",
                "password": "123456",
                "tipo": "motorista",
                "nome": "Test User"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"

    def test_signup_invalid_email(self):
        """Test signup with invalid email"""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "invalid-email",
                "password": "123456",
                "tipo": "motorista",
                "nome": "Test User"
            }
        )
        assert response.status_code == 422

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        # First signup
        client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.com",
                "password": "123456",
                "tipo": "motorista",
                "nome": "Test User"
            }
        )
        
        # Try duplicate
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.com",
                "password": "123456",
                "tipo": "shipper",
                "nome": "Another User"
            }
        )
        assert response.status_code == 400

    def test_login(self):
        """Test user login"""
        # First signup
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.com",
                "password": "123456",
                "tipo": "motorista",
                "nome": "Test User"
            }
        )
        assert signup_response.status_code == 200
        
        # Then login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@test.com",
                "password": "123456"
            }
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()
        assert login_response.json()["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@test.com",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401

    def test_me_authenticated(self):
        """Test getting current user with valid token"""
        # Signup
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@test.com",
                "password": "123456",
                "tipo": "motorista",
                "nome": "Test User"
            }
        )
        token = signup_response.json()["access_token"]
        
        # Get me
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "test@test.com"
        assert response.json()["tipo"] == "motorista"

    def test_me_without_token(self):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403

    def test_me_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 403
