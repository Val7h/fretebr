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

    # Hash password (required for regular signup)
    hashed_password = hash_password(user.password) if user.password else None

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


def create_user_from_google(db: Session, google_id: str, email: str, nome: str, foto: str = None) -> User:
    """
    Create a new user from Google OAuth data.
    If user already exists with this email, update with google_id and foto.

    Args:
        db: Database session
        google_id: Google unique ID
        email: Email from Google
        nome: Name from Google
        foto: Profile picture URL from Google

    Returns:
        User object (new or updated)
    """
    # Check if user already exists by google_id
    existing_user = db.query(User).filter(User.google_id == google_id).first()
    if existing_user:
        return existing_user

    # Check if user exists by email (from previous signup)
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # Update with Google info
        existing_user.google_id = google_id
        existing_user.foto = foto
        db.commit()
        db.refresh(existing_user)
        return existing_user

    # Create new user
    # Tipo padrão é "motorista", pode ser alterado depois
    db_user = User(
        email=email,
        password_hash=None,  # No password for OAuth users
        tipo="motorista",  # Default type
        nome=nome,
        google_id=google_id,
        foto=foto
    )

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
