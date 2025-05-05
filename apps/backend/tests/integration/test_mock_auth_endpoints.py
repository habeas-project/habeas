import os
import tempfile

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.models.user import User
from app.routers import mock_auth_router
from tests.test_utils import create_all_tables


@pytest.fixture(scope="module")
def test_db_file():
    """Create a temporary SQLite file for the tests."""
    # Create a temporary file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Create the database URL for SQLite
    db_url = f"sqlite:///{db_path}"
    print(f"Using SQLite test database at: {db_url}")

    # Yield the database path for the tests
    yield db_url

    # Close and remove the temporary file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope="module")
def mock_test_engine(test_db_file):
    """Create a SQLAlchemy engine for the mock auth tests."""
    # Create an engine connected to the test database file
    engine = create_engine(test_db_file)

    # Create all tables
    tables = create_all_tables(engine)
    print(f"Tables created for mock auth tests: {tables}")

    yield engine

    # Close engine connections
    engine.dispose()


@pytest.fixture(scope="function")
def mock_test_session(mock_test_engine):
    """Create a new database session for each test."""
    # Create a new session
    TestSessionLocal = sessionmaker(bind=mock_test_engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def mock_test_app(mock_test_engine, mock_test_session):
    """Create a test app with mock auth router included."""
    # Create a new FastAPI app
    app = FastAPI()
    app.include_router(mock_auth_router.router)

    # Override the database dependency
    def override_get_db():
        try:
            yield mock_test_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.fixture
def mock_client(mock_test_app):
    """Create a test client using the mock auth test app."""
    with TestClient(mock_test_app) as test_client:
        yield test_client


@pytest.mark.integration
class TestMockAuthEndpoints:
    """Integration tests for mock authentication endpoints."""

    def test_register_user(self, mock_client, mock_test_session):
        """Test user registration endpoint."""
        # Arrange
        test_user = {"email": "test@example.com", "password": "Password123!", "user_type": "attorney"}

        # Act
        response = mock_client.post("/mock/register", json=test_user)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_type"] == "attorney"

        # Verify user was created in database
        db_user = mock_test_session.query(User).filter(User.cognito_id == f"mock_{test_user['email']}").first()
        assert db_user is not None
        assert db_user.user_type == "attorney"

    def test_register_existing_user(self, mock_client, mock_test_session):
        """Test registering a user that already exists."""
        # Arrange
        test_user = {"email": "existing@example.com", "password": "Password123!", "user_type": "attorney"}

        # Create user first
        response = mock_client.post("/mock/register", json=test_user)
        assert response.status_code == 201

        # Act - Try to register again
        response = mock_client.post("/mock/register", json=test_user)

        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_login_user(self, mock_client, mock_test_session):
        """Test user login endpoint."""
        # Arrange - Register a user first
        test_user = {"email": "login@example.com", "password": "Password123!", "user_type": "attorney"}
        register_response = mock_client.post("/mock/register", json=test_user)
        assert register_response.status_code == 201

        # Act - Login with the user
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        login_response = mock_client.post("/mock/login", json=login_data)

        # Assert
        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_type"] == "attorney"

    def test_login_nonexistent_user(self, mock_client):
        """Test login with a user that doesn't exist."""
        # Arrange
        login_data = {"email": "nonexistent@example.com", "password": "Password123!"}

        # Act
        response = mock_client.post("/mock/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
