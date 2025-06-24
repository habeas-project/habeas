"""Integration tests for emergency endpoints"""

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import Attorney, ClientProfile, Court, EmergencyCase, EmergencyContact, User

client = TestClient(app)


@pytest.fixture
def sample_user(db_session: Session):
    """Create a sample user with client profile and emergency contacts"""
    user = User(cognito_id="test-user-123", user_type="client_helper", primary_role="client_helper")
    db_session.add(user)
    db_session.flush()

    client_profile = ClientProfile(
        user_id=user.id,
        profile_name="Test Profile",
        is_self=True,
        first_name="John",
        last_name="Doe",
        country_of_birth="USA",
        birth_date="1990-01-01",
    )
    db_session.add(client_profile)
    db_session.flush()

    emergency_contact = EmergencyContact(
        client_profile_id=client_profile.id,
        full_name="Jane Doe",
        relationship="spouse",
        phone_number="+1234567890",
        email="jane@example.com",
    )
    db_session.add(emergency_contact)
    db_session.commit()

    return user


@pytest.fixture
def sample_court(db_session: Session):
    """Create a sample court"""
    court = Court(
        name="US District Court for the Central District of California",
        abbreviation="CACD",
        url="https://www.cacd.uscourts.gov/",
    )
    db_session.add(court)
    db_session.commit()
    return court


@pytest.fixture
def sample_attorney(db_session: Session, sample_court: Court):
    """Create a sample attorney admitted to the court"""
    attorney = Attorney(
        name="Legal Attorney", phone_number="+1987654321", email="attorney@lawfirm.com", zip_code="90210", state="CA"
    )
    db_session.add(attorney)
    db_session.flush()

    # Add court admission
    attorney.admitted_courts.append(sample_court)
    db_session.commit()
    return attorney


def test_get_emergency_status_no_prerequisites(db_session: Session):
    """Test emergency status when user has no prerequisites"""
    # Create user without client profiles or emergency contacts
    user = User(cognito_id="test-user-no-prereq", user_type="client_helper")
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/emergency/users/{user.id}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["has_emergency_contacts"] is False
    assert data["has_client_profiles"] is False
    assert data["can_activate_emergency"] is False
    assert data["active_emergency_case_id"] is None


def test_get_emergency_status_with_prerequisites(sample_user: User):
    """Test emergency status when user has all prerequisites"""
    response = client.get(f"/emergency/users/{sample_user.id}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["has_emergency_contacts"] is True
    assert data["has_client_profiles"] is True
    assert data["can_activate_emergency"] is True
    assert data["active_emergency_case_id"] is None


def test_create_emergency_case(sample_user: User, sample_court: Court):
    """Test creating an emergency case"""
    client_profile = sample_user.client_profiles[0]

    emergency_request = {
        "client_profile_id": client_profile.id,
        "case_type": "self",
        "location": {
            "latitude": 34.0522,
            "longitude": -118.2437,
            "address": "123 Main St, Los Angeles, CA",
            "description": "Downtown Los Angeles",
        },
    }

    response = client.post(f"/emergency/cases?user_id={sample_user.id}", json=emergency_request)
    assert response.status_code == 201

    data = response.json()
    assert data["case_id"] is not None
    assert data["status"] == "active"
    assert "Case posted" in data["message"]


def test_get_emergency_case_status(sample_user: User, sample_court: Court, db_session: Session):
    """Test getting emergency case status"""
    # Create an emergency case
    client_profile = sample_user.client_profiles[0]

    emergency_case = EmergencyCase(
        user_id=sample_user.id,
        client_profile_id=client_profile.id,
        case_type="self",
        status="active",
        detention_latitude=34.0522,
        detention_longitude=-118.2437,
        assigned_court_id=sample_court.id,
    )
    db_session.add(emergency_case)
    db_session.commit()

    response = client.get(f"/emergency/cases/{emergency_case.id}/status")
    assert response.status_code == 200

    data = response.json()
    assert data["case_id"] == emergency_case.id
    assert data["status"] == "active"
    assert data["message"] == "Case posted - attorneys notified"


def test_court_jurisdiction_lookup(sample_court: Court):
    """Test court jurisdiction lookup by coordinates"""
    response = client.get("/emergency/courts/jurisdiction?latitude=34.0522&longitude=-118.2437")
    assert response.status_code == 200

    data = response.json()
    assert data["court_id"] == sample_court.id
    assert data["court_name"] == sample_court.name
    assert data["confidence"] > 0


def test_attorney_notification_preferences(sample_attorney: Attorney):
    """Test attorney notification preferences endpoints"""
    # Get default preferences
    response = client.get(f"/emergency/attorneys/{sample_attorney.id}/preferences")
    assert response.status_code == 200

    data = response.json()
    assert data["attorney_id"] == sample_attorney.id
    assert data["email_enabled"] is True
    assert data["sms_enabled"] is True

    # Update preferences
    update_request = {
        "email_enabled": False,
        "sms_enabled": True,
        "push_enabled": False,
        "daily_digest_enabled": True,
        "escalated_notifications_enabled": True,
    }

    response = client.put(f"/emergency/attorneys/{sample_attorney.id}/preferences", json=update_request)
    assert response.status_code == 200

    data = response.json()
    assert data["email_enabled"] is False
    assert data["push_enabled"] is False


def test_get_unassigned_cases(sample_user: User, sample_court: Court, db_session: Session):
    """Test getting unassigned emergency cases"""
    # Create an unassigned emergency case
    client_profile = sample_user.client_profiles[0]

    emergency_case = EmergencyCase(
        user_id=sample_user.id,
        client_profile_id=client_profile.id,
        case_type="self",
        status="active",
        detention_address="123 Main St, Los Angeles, CA",
        assigned_court_id=sample_court.id,
    )
    db_session.add(emergency_case)
    db_session.commit()

    response = client.get("/emergency/cases/unassigned")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert any(case["case_id"] == emergency_case.id for case in data)


def test_daily_digest(sample_user: User, sample_court: Court, db_session: Session):
    """Test daily digest endpoint"""
    # Create an unassigned emergency case
    client_profile = sample_user.client_profiles[0]

    emergency_case = EmergencyCase(
        user_id=sample_user.id,
        client_profile_id=client_profile.id,
        case_type="loved_one",
        status="active",
        detention_address="456 Oak Ave, Los Angeles, CA",
        assigned_court_id=sample_court.id,
    )
    db_session.add(emergency_case)
    db_session.commit()

    response = client.get("/emergency/daily-digest")
    assert response.status_code == 200

    data = response.json()
    assert "unassigned_cases" in data
    assert "court_coverage_stats" in data
    assert "total_unassigned" in data
    assert data["total_unassigned"] >= 1
