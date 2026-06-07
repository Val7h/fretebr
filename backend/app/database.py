from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
import os
import logging

logger = logging.getLogger(__name__)

# DATABASE_URL drives tudo: SQLite default (dev), Postgres em prod/staging
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fretebr.db")

# Configuracoes especificas para cada banco
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    logger.info(f"[DB] SQLite ativo: {DATABASE_URL}")
elif DATABASE_URL.startswith("postgresql"):
    # PostgreSQL com connection pool tunado
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,            # health-check antes de cada checkout
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),  # recicla a cada 30min
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
    )
    # Logger sem expor senha
    safe_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
    logger.info(f"[DB] Postgres ativo: ...@{safe_url}")
else:
    # Outros bancos suportados pelo SQLAlchemy (MySQL, MSSQL etc)
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    logger.info(f"[DB] Engine generico ativo")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
