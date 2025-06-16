"""Integration tests for signup endpoints (attorney, client, admin)."""

import pytest

from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.models.attorney import Attorney
from app.models.client import Client
from app.models.user import User


@pytest.mark.integration
class TestSignupEndpoints:
    """Comprehensive integration tests for all signup endpoints."""

    # --- Attorney Signup Tests ---

    def test_attorney_signup_success(self, client, session: Session):
        """Test successful attorney registration."""
        # Arrange
        attorney_data = {
            "name": "Jane Doe",
            "phone_number": "+15551234567",
            "email": "jane.doe@example.com",
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/attorney", json=attorney_data)

        # Assert
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
        assert user_data["is_active"] is True
        assert user_data["cognito_id"] == "mock_jane.doe@example.com"

        # Verify attorney data
        attorney_data_response = data["attorney"]
        assert attorney_data_response["name"] == attorney_data["name"]
        assert attorney_data_response["email"] == attorney_data["email"]
        assert attorney_data_response["phone_number"] == attorney_data["phone_number"]

        # Verify database records
        db_user = session.query(User).filter(User.cognito_id == "mock_jane.doe@example.com").first()
        assert db_user is not None
        assert db_user.user_type == "attorney"

        db_attorney = session.query(Attorney).filter(Attorney.email == attorney_data["email"]).first()
        assert db_attorney is not None
        assert db_attorney.user_id == db_user.id

    def test_attorney_signup_duplicate_email(self, client, session: Session):
        """Test attorney signup with duplicate email."""
        # Arrange - Create first attorney
        attorney_data = {
            "name": "John Doe",
            "phone_number": "+15551234567",
            "email": "duplicate@example.com",
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }
        response1 = client.post("/signup/attorney", json=attorney_data)
        assert response1.status_code == 201

        # Act - Try to create another attorney with same email
        attorney_data2 = {
            "name": "Jane Smith",
            "phone_number": "+15559876543",
            "email": "duplicate@example.com",
            "zip_code": "67890",
            "state": "NY",
            "password": "AnotherPassword123!",
        }
        response2 = client.post("/signup/attorney", json=attorney_data2)

        # Assert
        assert response2.status_code == 400
        error_data = response2.json()
        assert "attorney with this email already exists" in error_data["detail"]

    # --- Client Signup Tests ---

    def test_client_signup_success(self, client, session: Session):
        """Test successful client registration."""
        # Arrange
        client_data = {
            "first_name": "Maria",
            "last_name": "Garcia",
            "country_of_birth": "Mexico",
            "nationality": "Mexican",
            "birth_date": "1990-05-15",
            "alien_registration_number": "A123456789",
            "passport_number": "MX1234567",
            "school_name": "University of California",
            "student_id_number": "STU123456",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/client", json=client_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "client" in data
        assert "access_token" in data
        assert "token_type" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "client"
        assert user_data["is_active"] is True

        # Verify client data
        client_data_response = data["client"]
        assert client_data_response["first_name"] == client_data["first_name"]
        assert client_data_response["last_name"] == client_data["last_name"]
        assert client_data_response["country_of_birth"] == client_data["country_of_birth"]

        # Verify database records
        db_client = (
            session.query(Client)
            .filter(
                Client.first_name == client_data["first_name"],
                Client.last_name == client_data["last_name"],
            )
            .first()
        )
        assert db_client is not None

        db_user = session.query(User).filter(User.id == db_client.user_id).first()
        assert db_user is not None
        assert db_user.user_type == "client"

    def test_client_signup_duplicate_name_and_birth_date(self, client, session: Session):
        """Test client signup with duplicate name and birth date."""
        # Arrange - Create first client
        client_data = {
            "first_name": "Carlos",
            "last_name": "Rodriguez",
            "country_of_birth": "Spain",
            "birth_date": "1985-10-20",
            "password": "SecurePassword123!",
        }
        response1 = client.post("/signup/client", json=client_data)
        assert response1.status_code == 201

        # Act - Try to create another client with same name and birth date
        client_data2 = {
            "first_name": "Carlos",
            "last_name": "Rodriguez",
            "country_of_birth": "Argentina",  # Different country
            "birth_date": "1985-10-20",  # Same birth date
            "password": "AnotherPassword123!",
        }
        response2 = client.post("/signup/client", json=client_data2)

        # Assert
        assert response2.status_code == 400
        error_data = response2.json()
        assert "client with this name and birth date already exists" in error_data["detail"]

    # --- Admin Signup Tests ---

    def test_admin_signup_success(self, client, session: Session):
        """Test successful admin registration."""
        # Arrange
        admin_data = {
            "name": "System Administrator",
            "email": "admin@example.com",
            "department": "IT",
            "role": "admin",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/admin", json=admin_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "user" in data
        assert "admin" in data
        assert "access_token" in data
        assert "token_type" in data

        # Verify user data
        user_data = data["user"]
        assert user_data["user_type"] == "admin"
        assert user_data["is_active"] is True
        assert user_data["cognito_id"] == "mock_admin@example.com"

        # Verify admin data
        admin_data_response = data["admin"]
        assert admin_data_response["name"] == admin_data["name"]
        assert admin_data_response["email"] == admin_data["email"]
        assert admin_data_response["department"] == admin_data["department"]
        assert admin_data_response["role"] == admin_data["role"]

        # Verify database records
        db_user = session.query(User).filter(User.cognito_id == "mock_admin@example.com").first()
        assert db_user is not None
        assert db_user.user_type == "admin"

        db_admin = session.query(Admin).filter(Admin.email == admin_data["email"]).first()
        assert db_admin is not None
        assert db_admin.user_id == db_user.id

    def test_admin_signup_duplicate_email(self, client, session: Session):
        """Test admin signup with duplicate email."""
        # Arrange - Create first admin
        admin_data = {
            "name": "First Admin",
            "email": "duplicate.admin@example.com",
            "department": "IT",
            "role": "admin",
            "password": "SecurePassword123!",
        }
        response1 = client.post("/signup/admin", json=admin_data)
        assert response1.status_code == 201

        # Act - Try to create another admin with same email
        admin_data2 = {
            "name": "Second Admin",
            "email": "duplicate.admin@example.com",
            "department": "Security",
            "role": "admin",
            "password": "AnotherPassword123!",
        }
        response2 = client.post("/signup/admin", json=admin_data2)

        # Assert
        assert response2.status_code == 400
        error_data = response2.json()
        assert "admin with this email already exists" in error_data["detail"]

    # --- Cross-Endpoint Integration Tests ---

    def test_cross_endpoint_email_uniqueness_attorney_admin(self, client, session: Session):
        """Test that attorney and admin cannot share the same email."""
        # Arrange - Create attorney first
        email = "shared@example.com"
        attorney_data = {
            "name": "Attorney User",
            "phone_number": "+15551234567",
            "email": email,
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }
        response1 = client.post("/signup/attorney", json=attorney_data)
        assert response1.status_code == 201

        # Act - Try to create admin with same email
        admin_data = {
            "name": "Admin User",
            "email": email,
            "department": "IT",
            "role": "admin",
            "password": "SecurePassword123!",
        }
        response2 = client.post("/signup/admin", json=admin_data)

        # Assert
        assert response2.status_code == 400
        error_data = response2.json()
        assert "user with this email already exists" in error_data["detail"]

    def test_cross_endpoint_email_uniqueness_admin_attorney(self, client, session: Session):
        """Test that admin and attorney cannot share the same email (reverse order)."""
        # Arrange - Create admin first
        email = "reverse.shared@example.com"
        admin_data = {
            "name": "Admin User",
            "email": email,
            "department": "IT",
            "role": "admin",
            "password": "SecurePassword123!",
        }
        response1 = client.post("/signup/admin", json=admin_data)
        assert response1.status_code == 201

        # Act - Try to create attorney with same email
        attorney_data = {
            "name": "Attorney User",
            "phone_number": "+15551234567",
            "email": email,
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }
        response2 = client.post("/signup/attorney", json=attorney_data)

        # Assert
        assert response2.status_code == 400
        error_data = response2.json()
        assert "user with this email already exists" in error_data["detail"]

    def test_multiple_user_types_different_emails(self, client, session: Session):
        """Test that different user types can be created with different emails."""
        # Arrange & Act - Create attorney
        attorney_response = client.post(
            "/signup/attorney",
            json={
                "name": "Attorney Smith",
                "phone_number": "+15551111111",
                "email": "attorney@example.com",
                "zip_code": "12345",
                "state": "CA",
                "password": "SecurePassword123!",
            },
        )

        # Create client (clients don't have email, so no conflict)
        client_response = client.post(
            "/signup/client",
            json={
                "first_name": "Client",
                "last_name": "Johnson",
                "country_of_birth": "USA",
                "birth_date": "1990-01-01",
                "password": "SecurePassword123!",
            },
        )

        # Create admin
        admin_response = client.post(
            "/signup/admin",
            json={
                "name": "Admin Wilson",
                "email": "admin@example.com",
                "department": "IT",
                "role": "admin",
                "password": "SecurePassword123!",
            },
        )

        # Assert all succeed
        assert attorney_response.status_code == 201
        assert client_response.status_code == 201
        assert admin_response.status_code == 201

        # Verify different user types in database
        users = session.query(User).all()
        user_types = {user.user_type for user in users}
        assert user_types == {"attorney", "client", "admin"}

    # --- Validation Tests ---

    def test_attorney_signup_invalid_phone_format(self, client):
        """Test attorney signup with invalid phone number format."""
        # Arrange
        attorney_data = {
            "name": "Jane Doe",
            "phone_number": "invalid-phone",  # Invalid format
            "email": "jane@example.com",
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/attorney", json=attorney_data)

        # Assert
        assert response.status_code == 422
        error_data = response.json()
        # Phone validation errors come as value_error, not validation_error
        assert "value_error" in error_data["detail"][0]["type"]

    def test_attorney_signup_invalid_state_code(self, client):
        """Test attorney signup with invalid state code."""
        # Arrange
        attorney_data = {
            "name": "Jane Doe",
            "phone_number": "+15551234567",
            "email": "jane@example.com",
            "zip_code": "12345",
            "state": "INVALID",  # Invalid state code
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/attorney", json=attorney_data)

        # Assert
        assert response.status_code == 422

    def test_client_signup_invalid_birth_date_format(self, client):
        """Test client signup with invalid birth date format."""
        # Arrange
        client_data = {
            "first_name": "Maria",
            "last_name": "Garcia",
            "country_of_birth": "Mexico",
            "birth_date": "invalid-date",  # Invalid date format
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/client", json=client_data)

        # Assert
        assert response.status_code == 422

    def test_admin_signup_missing_required_fields(self, client):
        """Test admin signup with missing required fields."""
        # Arrange
        admin_data = {
            "name": "Admin User",
            # Missing email and password
            "department": "IT",
            "role": "admin",
        }

        # Act
        response = client.post("/signup/admin", json=admin_data)

        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "email" in str(error_data)
        assert "password" in str(error_data)

    # --- Database Integrity Tests ---

    def test_signup_transaction_rollback_on_error(self, client, session: Session):
        """Test that signup transactions rollback properly on errors."""
        # This test simulates a scenario where the user is created but attorney creation fails
        # Due to our implementation, this should rollback the entire transaction

        # First, verify clean state
        initial_user_count = session.query(User).count()
        initial_attorney_count = session.query(Attorney).count()

        # Arrange - Use invalid data that passes schema validation but fails at DB level
        attorney_data = {
            "name": "Test Attorney",
            "phone_number": "+15551234567",
            "email": "valid@example.com",
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }

        # Act - First signup should succeed
        response1 = client.post("/signup/attorney", json=attorney_data)
        assert response1.status_code == 201

        # Act - Second signup with same email should fail and rollback
        response2 = client.post("/signup/attorney", json=attorney_data)
        assert response2.status_code == 400

        # Assert - Only one user and one attorney should exist (no orphaned records)
        final_user_count = session.query(User).count()
        final_attorney_count = session.query(Attorney).count()

        assert final_user_count == initial_user_count + 1
        assert final_attorney_count == initial_attorney_count + 1

    def test_user_attorney_relationship_integrity(self, client, session: Session):
        """Test that User and Attorney records are properly linked."""
        # Arrange
        attorney_data = {
            "name": "Linked Attorney",
            "phone_number": "+15551234567",
            "email": "linked@example.com",
            "zip_code": "12345",
            "state": "CA",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/attorney", json=attorney_data)
        assert response.status_code == 201

        # Assert - Verify proper linking
        db_attorney = session.query(Attorney).filter(Attorney.email == attorney_data["email"]).first()
        assert db_attorney is not None
        assert db_attorney.user_id is not None

        db_user = session.query(User).filter(User.id == db_attorney.user_id).first()
        assert db_user is not None
        assert db_user.user_type == "attorney"

        # Verify bidirectional relationship (if implemented)
        assert db_user.attorney == db_attorney

    def test_user_admin_relationship_integrity(self, client, session: Session):
        """Test that User and Admin records are properly linked."""
        # Arrange
        admin_data = {
            "name": "Linked Admin",
            "email": "linked.admin@example.com",
            "department": "IT",
            "role": "admin",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/admin", json=admin_data)
        assert response.status_code == 201

        # Assert - Verify proper linking
        db_admin = session.query(Admin).filter(Admin.email == admin_data["email"]).first()
        assert db_admin is not None
        assert db_admin.user_id is not None

        db_user = session.query(User).filter(User.id == db_admin.user_id).first()
        assert db_user is not None
        assert db_user.user_type == "admin"

        # Verify bidirectional relationship
        assert db_user.admin == db_admin

    def test_user_client_relationship_integrity(self, client, session: Session):
        """Test that User and Client records are properly linked."""
        # Arrange
        client_data = {
            "first_name": "Linked",
            "last_name": "Client",
            "country_of_birth": "USA",
            "birth_date": "1990-01-01",
            "password": "SecurePassword123!",
        }

        # Act
        response = client.post("/signup/client", json=client_data)
        assert response.status_code == 201

        # Assert - Verify proper linking
        db_client = session.query(Client).filter(Client.first_name == "Linked", Client.last_name == "Client").first()
        assert db_client is not None
        assert db_client.user_id is not None

        db_user = session.query(User).filter(User.id == db_client.user_id).first()
        assert db_user is not None
        assert db_user.user_type == "client"

        # Verify bidirectional relationship
        assert db_user.client == db_client

    # --- Edge Cases ---

    def test_signup_with_special_characters_in_names(self, client, session: Session):
        """Test signup with special characters in names."""
        # Test attorney with special characters
        attorney_response = client.post(
            "/signup/attorney",
            json={
                "name": "José María O'Connor-Smith",
                "phone_number": "+15551234567",
                "email": "jose.maria@example.com",
                "zip_code": "12345",
                "state": "CA",
                "password": "SecurePassword123!",
            },
        )
        assert attorney_response.status_code == 201

        # Test client with special characters
        client_response = client.post(
            "/signup/client",
            json={
                "first_name": "François",
                "last_name": "Müller-García",
                "country_of_birth": "France",
                "birth_date": "1990-01-01",
                "password": "SecurePassword123!",
            },
        )
        assert client_response.status_code == 201

        # Test admin with special characters
        admin_response = client.post(
            "/signup/admin",
            json={
                "name": "Åsa Ñoña-Übermensch",
                "email": "asa.admin@example.com",
                "department": "IT",
                "role": "admin",
                "password": "SecurePassword123!",
            },
        )
        assert admin_response.status_code == 201

        # Verify all were created successfully
        attorney_count = session.query(Attorney).count()
        client_count = session.query(Client).count()
        admin_count = session.query(Admin).count()

        assert attorney_count >= 1
        assert client_count >= 1
        assert admin_count >= 1
