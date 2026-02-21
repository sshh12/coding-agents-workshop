# tests/conftest.py
# Shared pytest fixtures for the test suite.
# Why: Provides a fresh in-memory database and test client for every test.
# Relevant files: tests/test_experiments.py, tests/test_runs.py, tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from shared.base import Base
from shared.db import get_db

# Import all models so Base.metadata knows about them before create_all()
import experiments.models  # noqa: F401
import runs.models  # noqa: F401


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(db_session):
    """Create a FastAPI test client with the test database injected."""
    from manage import create_app

    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
