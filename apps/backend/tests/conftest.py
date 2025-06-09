import os
import tempfile

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Import all models explicitly to ensure they are registered with Base.metadata
# This must happen before create_all_tables is called
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


# SQLModel-style testing fixtures for proper session isolation
@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session using SQLModel best practices.

    This uses an in-memory SQLite database with StaticPool to ensure
    the same database is used across all connections within a test.
    """
    engine = create_engine(
        "sqlite://",  # In-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Keep the same database across all connections
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables using our utility function
    tables = create_all_tables(engine)
    print(f"Test database initialized with tables: {tables}")

    # Create session and ensure it's properly cleaned up
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """
    Create a test client that uses the same session as the test.

    This follows the SQLModel testing best practice of sharing the same
    session between the API and the test assertions.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Legacy fixtures for backward compatibility with existing tests
@pytest.fixture(scope="session")
def db_engine():
    """Create a SQLAlchemy engine for the test database (legacy fixture)."""
    # Use a temporary file-based SQLite database for tests
    # This ensures tables persist across different sessions
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    engine = create_engine(
        f"sqlite:///{temp_db.name}",
        connect_args={"check_same_thread": False},  # Allow SQLite to be used in multiple threads
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables using our utility function
    tables = create_all_tables(engine)
    print(f"Legacy test database initialized with tables: {tables}")

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    os.unlink(temp_db.name)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test (legacy fixture)."""
    # Create a new session for each test
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


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
