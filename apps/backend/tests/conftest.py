import os

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Import our test utility functions
from tests.test_utils import create_all_tables


# Enable mock authentication for all tests
@pytest.fixture(scope="session", autouse=True)
def enable_mock_auth():
    """
    Enable mock authentication for all tests by setting the ENABLE_MOCK_AUTH
    environment variable. This is automatically applied to all tests.

    Using autouse=True ensures this runs for all tests without explicit inclusion.
    """
    # Store original value if it exists
    original_value = os.environ.get("ENABLE_MOCK_AUTH")

    # Set to true for tests
    os.environ["ENABLE_MOCK_AUTH"] = "true"

    yield

    # Restore original value or remove if it wasn't set
    if original_value is not None:
        os.environ["ENABLE_MOCK_AUTH"] = original_value
    else:
        os.environ.pop("ENABLE_MOCK_AUTH", None)


# Test database setup
@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLAlchemy engine for the test database."""
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},  # Allow SQLite to be used in multiple threads
    )

    # Create all tables using our utility function
    create_all_tables(engine)

    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    # Create a new session for each test
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

    # Override the dependency to use our test session
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


@pytest.fixture
def UserTestFactory(SessionScopedFactory):
    """Factory fixture for creating User instances."""
    from .factories import UserFactory

    class TestUserFactory(UserFactory, SessionScopedFactory):
        pass

    return TestUserFactory


# Test markers setup
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
