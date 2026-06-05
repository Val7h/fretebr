from sqlalchemy.orm import Session
from app.models.user import User, UserType
from app.schemas.user import UserCreate
from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    # Hash password
    hashed_password = hash_password(user.password)
    
    # Create user object
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        tipo=user.tipo,
        nome=user.nome,
        telefone=user.telefone,
        cpf=user.cpf
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> User:
    """
    Get user by email
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Get user by ID
    """
    return db.query(User).filter(User.id == user_id).first()
