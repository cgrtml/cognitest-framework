"""
User Service - Database Configuration
Author: Çağrı Temel
Description: Database session and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from demo_app.user_service.models import Base

# SQLite database for demo purposes
DATABASE_URL = "sqlite:///./user_service.db"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_db():
    """Reset database (for testing)"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)