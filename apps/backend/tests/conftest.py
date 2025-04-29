import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# Test database setup
@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLAlchemy engine for the test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client using the test database session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# --- Factory Fixtures ---


@pytest.fixture
def SessionScopedFactory(db_session):
    """Fixture to provide factories scoped to the test db session."""
    from .factories import BaseFactory  # type: ignore

    class SessionFactory(BaseFactory):
        class Meta:
            sqlalchemy_session = db_session
            sqlalchemy_session_persistence = "flush"

    return SessionFactory


@pytest.fixture
def AttorneyTestFactory(SessionScopedFactory):
    """Factory fixture for creating Attorney instances."""
    from .factories import AttorneyFactory

    class TestAttorneyFactory(AttorneyFactory, SessionScopedFactory):
        pass

    return TestAttorneyFactory


@pytest.fixture
def CourtTestFactory(SessionScopedFactory):
    """Factory fixture for creating Court instances."""
    from .factories import CourtFactory

    class TestCourtFactory(CourtFactory, SessionScopedFactory):
        pass

    return TestCourtFactory


# Test markers setup
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
