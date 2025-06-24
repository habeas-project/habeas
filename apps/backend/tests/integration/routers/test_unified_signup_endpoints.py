import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.admin import Admin
from app.models.attorney import Attorney
from app.models.client_profile import ClientProfile
from app.models.user import User


class TestUnifiedSignupEndpoints:
    """Test suite for unified signup endpoints with hybrid architecture"""

    @pytest.fixture
    def client(self):
        """FastAPI test client"""
        return TestClient(app)

    def test_unified_signup_attorney_success(self, client: TestClient, session: Session):
        """Test successful attorney signup via unified endpoint"""
        signup_data = {"email": "attorney@example.com", "password": "SecurePassword123!", "primary_role": "attorney"}

        role_data = {
            "attorney_data": {
                "name": "Jane Attorney",
                "phone_number": "+15551234567",
                "email": "attorney@example.com",
                "zip_code": "12345",
                "state": "CA",
            }
        }

        response = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "attorney" in data
        assert "access_token" in data
        assert "token_type" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "attorney"
        assert user_data["primary_role"] == "attorney"
        assert user_data["is_active"] is True

        # Verify attorney data
        attorney_data = data["attorney"]
        assert attorney_data["name"] == "Jane Attorney"
        assert attorney_data["email"] == "attorney@example.com"

        # Verify database records
        user = session.query(User).filter(User.cognito_id == "mock_attorney@example.com").first()
        assert user is not None
        assert user.primary_role == "attorney"

        attorney = session.query(Attorney).filter(Attorney.user_id == user.id).first()
        assert attorney is not None
        assert attorney.name == "Jane Attorney"

    def test_unified_signup_client_helper_success(self, client: TestClient, session: Session):
        """Test successful client helper signup via unified endpoint"""
        signup_data = {"email": "helper@example.com", "password": "SecurePassword123!", "primary_role": "client_helper"}

        role_data = {
            "client_profile_data": {
                "profile_name": "John Doe",
                "is_self": True,
                "first_name": "John",
                "last_name": "Doe",
                "country_of_birth": "United States",
                "birth_date": "1990-01-01",
            }
        }

        response = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "client_profile" in data
        assert "access_token" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "client_helper"
        assert user_data["primary_role"] == "client_helper"

        # Verify client profile data
        profile_data = data["client_profile"]
        assert profile_data["profile_name"] == "John Doe"
        assert profile_data["is_self"] is True
        assert profile_data["first_name"] == "John"

        # Verify database records
        user = session.query(User).filter(User.cognito_id == "mock_helper@example.com").first()
        assert user is not None
        assert user.primary_role == "client_helper"

        profile = session.query(ClientProfile).filter(ClientProfile.user_id == user.id).first()
        assert profile is not None
        assert profile.profile_name == "John Doe"

    def test_unified_signup_admin_success(self, client: TestClient, session: Session):
        """Test successful admin signup via unified endpoint"""
        signup_data = {"email": "admin@example.com", "password": "SecurePassword123!", "primary_role": "admin"}

        role_data = {
            "admin_data": {
                "name": "Admin User",
                "email": "admin@example.com",
                "department": "IT",
                "role": "System Administrator",
            }
        }

        response = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "admin" in data
        assert "access_token" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "admin"
        assert user_data["primary_role"] == "admin"

        # Verify admin data
        admin_data = data["admin"]
        assert admin_data["name"] == "Admin User"
        assert admin_data["department"] == "IT"

        # Verify database records
        user = session.query(User).filter(User.cognito_id == "mock_admin@example.com").first()
        assert user is not None
        assert user.primary_role == "admin"

        admin = session.query(Admin).filter(Admin.user_id == user.id).first()
        assert admin is not None
        assert admin.name == "Admin User"

    def test_unified_signup_duplicate_email(self, client: TestClient, session: Session):
        """Test unified signup with duplicate email"""
        # Create initial user
        signup_data = {"email": "duplicate@example.com", "password": "SecurePassword123!", "primary_role": "attorney"}

        role_data = {
            "attorney_data": {
                "name": "First Attorney",
                "phone_number": "+15551234567",
                "email": "duplicate@example.com",
                "zip_code": "12345",
                "state": "CA",
            }
        }

        response = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})
        assert response.status_code == 201

        # Try to create another user with same email
        signup_data2 = {
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
            "primary_role": "client_helper",
        }

        role_data2 = {
            "client_profile_data": {
                "profile_name": "John Doe",
                "is_self": True,
                "first_name": "John",
                "last_name": "Doe",
                "country_of_birth": "United States",
                "birth_date": "1990-01-01",
            }
        }

        response2 = client.post("/signup/unified", json={"signup_data": signup_data2, "role_data": role_data2})

        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]

    def test_unified_signup_missing_role_data(self, client: TestClient):
        """Test unified signup with missing role-specific data"""
        signup_data = {"email": "test@example.com", "password": "SecurePassword123!", "primary_role": "attorney"}

        role_data = {
            "client_profile_data": {  # Wrong data type for attorney role
                "profile_name": "John Doe",
                "is_self": True,
                "first_name": "John",
                "last_name": "Doe",
                "country_of_birth": "United States",
                "birth_date": "1990-01-01",
            }
        }

        response = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})

        assert response.status_code == 400
        assert "Attorney data required" in response.json()["detail"]

    def test_multi_profile_signup_success(self, client: TestClient, session: Session):
        """Test successful multi-profile signup"""
        signup_data = {
            "email": "family@example.com",
            "password": "SecurePassword123!",
            "primary_role": "client_helper",
            "client_profiles": [
                {
                    "profile_name": "Maria Rodriguez",
                    "is_self": True,
                    "first_name": "Maria",
                    "last_name": "Rodriguez",
                    "country_of_birth": "Mexico",
                    "birth_date": "1985-05-15",
                },
                {
                    "profile_name": "My Son",
                    "is_self": False,
                    "first_name": "Carlos",
                    "last_name": "Rodriguez",
                    "country_of_birth": "United States",
                    "birth_date": "2010-08-20",
                },
            ],
        }

        response = client.post("/signup/multi-profile", json=signup_data)

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "client_profiles" in data
        assert "access_token" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "client_helper"
        assert user_data["primary_role"] == "client_helper"

        # Verify client profiles
        profiles = data["client_profiles"]
        assert len(profiles) == 2

        maria_profile = next(p for p in profiles if p["profile_name"] == "Maria Rodriguez")
        assert maria_profile["is_self"] is True
        assert maria_profile["first_name"] == "Maria"

        son_profile = next(p for p in profiles if p["profile_name"] == "My Son")
        assert son_profile["is_self"] is False
        assert son_profile["first_name"] == "Carlos"

        # Verify database records
        user = session.query(User).filter(User.cognito_id == "mock_family@example.com").first()
        assert user is not None

        profiles_db = session.query(ClientProfile).filter(ClientProfile.user_id == user.id).all()
        assert len(profiles_db) == 2

    def test_multi_profile_signup_with_attorney(self, client: TestClient, session: Session):
        """Test multi-profile signup with optional attorney data"""
        signup_data = {
            "email": "lawyer.family@example.com",
            "password": "SecurePassword123!",
            "primary_role": "client_helper",
            "client_profiles": [
                {
                    "profile_name": "Self",
                    "is_self": True,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "country_of_birth": "United States",
                    "birth_date": "1980-01-01",
                }
            ],
            "attorney_data": {
                "name": "Jane Smith, Esq.",
                "phone_number": "+15551234567",
                "email": "lawyer.family@example.com",
                "zip_code": "12345",
                "state": "NY",
            },
        }

        response = client.post("/signup/multi-profile", json=signup_data)

        assert response.status_code == 201
        data = response.json()

        # Verify response includes both profiles and attorney
        assert "user" in data
        assert "client_profiles" in data
        assert "attorney" in data
        assert len(data["client_profiles"]) == 1

        attorney_data = data["attorney"]
        assert attorney_data["name"] == "Jane Smith, Esq."

        # Verify database records
        user = session.query(User).filter(User.cognito_id == "mock_lawyer.family@example.com").first()
        assert user is not None

        attorney = session.query(Attorney).filter(Attorney.user_id == user.id).first()
        assert attorney is not None
        assert attorney.name == "Jane Smith, Esq."

    def test_multi_profile_signup_empty_profiles(self, client: TestClient):
        """Test multi-profile signup with no client profiles"""
        signup_data = {
            "email": "empty@example.com",
            "password": "SecurePassword123!",
            "primary_role": "client_helper",
            "client_profiles": [],
        }

        response = client.post("/signup/multi-profile", json=signup_data)

        assert response.status_code == 400
        assert "At least one client profile is required" in response.json()["detail"]

    def test_unified_signup_transaction_rollback(self, client: TestClient, session: Session):
        """Test that failed signups rollback properly"""
        # This test would need to simulate a database error during signup
        # For now, we'll test the duplicate email scenario which triggers rollback

        signup_data = {"email": "rollback@example.com", "password": "SecurePassword123!", "primary_role": "attorney"}

        role_data = {
            "attorney_data": {
                "name": "Test Attorney",
                "phone_number": "+15551234567",
                "email": "rollback@example.com",
                "zip_code": "12345",
                "state": "CA",
            }
        }

        # First signup should succeed
        response1 = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})
        assert response1.status_code == 201

        # Second signup should fail and not leave orphaned records
        response2 = client.post("/signup/unified", json={"signup_data": signup_data, "role_data": role_data})
        assert response2.status_code == 400

        # Verify only one user and attorney exist
        users = session.query(User).filter(User.cognito_id == "mock_rollback@example.com").all()
        assert len(users) == 1

        attorneys = session.query(Attorney).filter(Attorney.email == "rollback@example.com").all()
        assert len(attorneys) == 1
