import os

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
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


# =============================================================================
# MODERN FIXTURES (RECOMMENDED)
# =============================================================================
# These fixtures follow SQLModel best practices with in-memory databases
# and proper session isolation. Use these for all new tests.


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session using SQLModel best practices.

    This uses an in-memory SQLite database with StaticPool to ensure
    the same database is used across all connections within a test.

    RECOMMENDED: Use this fixture for all new tests.
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

    RECOMMENDED: Use this fixture for all new tests.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# =============================================================================
# LEGACY FIXTURES (REMOVED)
# =============================================================================
# Legacy fixtures have been removed to eliminate deprecation warnings.
# All tests have been migrated to use the modern 'session' and 'client' fixtures.


# =============================================================================
# FACTORY FIXTURES (UPDATED TO SUPPORT BOTH LEGACY AND MODERN)
# =============================================================================
# These factories now support both legacy and modern fixtures during transition.


@pytest.fixture
def SessionScopedFactory(session):
    """
    Factory fixture that provides factories scoped to the modern test session.

    UPDATED: Now uses modern 'session' fixture instead of legacy 'db_session'.
    This provides better test isolation and follows SQLModel best practices.
    """
    from .factories import BaseFactory  # type: ignore

    class SessionFactory(BaseFactory):
        class Meta:
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "flush"

    return SessionFactory


# Legacy LegacySessionScopedFactory fixture has been removed.
# All tests now use SessionScopedFactory with the modern 'session' fixture.


@pytest.fixture
def AttorneyTestFactory(SessionScopedFactory):
    """Factory fixture for creating Attorney instances using modern session."""
    from .factories import AttorneyFactory

    class TestAttorneyFactory(AttorneyFactory, SessionScopedFactory):
        pass

    return TestAttorneyFactory


@pytest.fixture
def CourtTestFactory(SessionScopedFactory):
    """Factory fixture for creating Court instances using modern session."""
    from .factories import CourtFactory

    class TestCourtFactory(CourtFactory, SessionScopedFactory):
        pass

    return TestCourtFactory


@pytest.fixture
def UserTestFactory(SessionScopedFactory):
    """Factory fixture for creating User instances using modern session."""
    from .factories import UserFactory

    class TestUserFactory(UserFactory, SessionScopedFactory):
        pass

    return TestUserFactory


# Legacy factory fixtures for backward compatibility
# Legacy factory fixtures have been removed.
# All tests now use the modern factory fixtures with the 'session' fixture.


# Test markers setup
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
