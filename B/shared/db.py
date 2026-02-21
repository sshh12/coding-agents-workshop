# shared/db.py
# Database engine, session factory, and dependency injection.
# Why: Single source of truth for DB connections; all routes use get_db().
# Relevant files: shared/config.py, shared/base.py, experiments/models.py, runs/models.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
