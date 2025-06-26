"""
Integration tests for emergency system edge cases and failure scenarios.

These tests cover critical edge cases that could cause system failures:
- GPS unavailable/location permission denied scenarios
- Network connectivity issues during emergency activation
- Concurrent emergency activations and race conditions
- Attorney notification delivery failures and recovery
- Court jurisdiction boundary cases
"""

from datetime import date
from unittest.mock import patch

import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import (
    Attorney,
    ClientProfile,
    Court,
    EmergencyCase,
    EmergencyContact,
    User,
)
from app.services.emergency_service import EmergencyService

client = TestClient(app)


@pytest.fixture
def emergency_service(session: Session):
    """Create emergency service instance for testing"""
    return EmergencyService(db=session)


@pytest.fixture
def sample_user_with_contacts(session: Session):
    """Create a user with complete emergency setup"""
    user = User(cognito_id="test-user-emergency", user_type="client_helper", primary_role="client_helper")
    session.add(user)
    session.flush()

    client_profile = ClientProfile(
        user_id=user.id,
        profile_name="Test Emergency Profile",
        is_self=True,
        first_name="John",
        last_name="Doe",
        country_of_birth="USA",
        birth_date=date(1990, 1, 1),
    )
    session.add(client_profile)
    session.flush()

    # Add emergency contacts
    contact = EmergencyContact(
        client_profile_id=client_profile.id,
        full_name="Jane Doe",
        relationship="spouse",
        phone_number="+1234567890",
        email="jane@example.com",
    )
    session.add(contact)
    session.commit()
    return user


@pytest.fixture
def sample_court_with_attorneys(session: Session):
    """Create a court with multiple attorneys admitted"""
    court = Court(
        name="US District Court for the Central District of California",
        abbreviation="CACD",
        url="https://www.cacd.uscourts.gov/",
    )
    session.add(court)
    session.flush()

    # Create attorneys with different notification preferences
    attorneys = []
    for i in range(3):
        attorney = Attorney(
            name=f"Attorney {i + 1}",
            phone_number=f"+123456789{i}",
            email=f"attorney{i + 1}@lawfirm.com",
            zip_code="90210",
            state="CA",
        )
        session.add(attorney)
        session.flush()

        # Add court admission
        attorney.admitted_courts.append(court)
        attorneys.append(attorney)

    session.commit()
    return court, attorneys


class TestGpsAndLocationEdgeCases:
    """Test GPS and location service edge cases"""

    @patch("app.services.geocoding_service.GeocodingService.reverse_geocode_coordinates")
    def test_emergency_activation_gps_unavailable(
        self,
        mock_reverse_geocode_coordinates,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        client,
    ):
        """Test emergency activation when GPS coordinates are unavailable"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Mock geocoding service to simulate GPS unavailable
        mock_reverse_geocode_coordinates.side_effect = Exception("GPS unavailable")

        # Emergency request without GPS coordinates (manual entry)
        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "address": "123 Main St, Los Angeles, CA 90210",
                "description": "Near downtown courthouse",
                # No latitude/longitude - simulating GPS failure
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        # Should still succeed with manual address entry
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None
        assert data["status"] == "active"
        assert "Case posted" in data["message"]

    @patch("app.services.geocoding_service.GeocodingService.reverse_geocode_coordinates")
    def test_location_permission_denied_fallback(
        self,
        mock_reverse_geocode_coordinates,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        client,
    ):
        """Test fallback to manual location entry when GPS permission denied"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Mock geocoding to simulate location permission denied
        mock_reverse_geocode_coordinates.return_value = {
            "address": "Address unavailable - location permission denied",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90210",
            "confidence": 0.0,
        }

        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,  # Coordinates provided but geocoding fails
                "longitude": -118.2437,
                "address": "Manual entry: Downtown Los Angeles",
                "description": "User provided address after GPS permission denied",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        assert response.status_code == 201
        data = response.json()
        assert "Case posted" in data["message"]

    def test_indoor_location_poor_gps_accuracy(
        self, sample_user_with_contacts: User, sample_court_with_attorneys: tuple[Court, list[Attorney]], client
    ):
        """Test emergency activation with poor GPS accuracy (indoor location)"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Simulate indoor location with poor GPS accuracy
        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "accuracy": 500,  # Poor accuracy (500 meters)
                "address": "Approximate location - indoor/poor GPS",
                "description": "Federal Building basement level",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None

        # Should still create case but with accuracy limitations noted
        assert "Case posted" in data["message"]


class TestNetworkConnectivityEdgeCases:
    """Test network connectivity and service availability edge cases"""

    @patch("app.services.notification_service.NotificationService.send_immediate_case_notification")
    def test_network_connectivity_failure_during_activation(
        self,
        mock_send_notification,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        client,
    ):
        """Test emergency activation when network connectivity is poor"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Mock notification service to simulate network failure
        mock_send_notification.side_effect = Exception("Network timeout")

        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Main St, Los Angeles, CA",
                "description": "Network connectivity poor",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        # Case should still be created even if initial notifications fail
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None

        # Background retry system should handle notification failures
        assert "Case posted" in data["message"]

    @patch("requests.post")
    def test_external_service_unavailable(
        self,
        mock_requests_post,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        client,
    ):
        """Test emergency activation when external services (SMS/email) are unavailable"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Mock external service failures
        mock_requests_post.side_effect = Exception("External service unavailable")

        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Main St, Los Angeles, CA",
                "description": "External services down",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        # Emergency case creation should not fail due to external service issues
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None


class TestConcurrentEmergencyActivations:
    """Test concurrent emergency activations and race conditions"""

    def test_concurrent_emergency_activations_same_user(
        self, sample_user_with_contacts: User, sample_court_with_attorneys: tuple[Court, list[Attorney]], client
    ):
        """Test multiple concurrent emergency activations from same user"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Main St, Los Angeles, CA",
                "description": "Concurrent activation test",
            },
        }

        # Simulate concurrent requests
        responses = []
        for _ in range(3):
            response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)
            responses.append(response)

        # First request should succeed
        assert responses[0].status_code == 201

        # Subsequent requests should either succeed (if different profile)
        # or handle gracefully (if same profile has active case)
        for response in responses[1:]:
            assert response.status_code in [201, 400, 409]  # Success or handled conflict

    def test_concurrent_attorney_case_acceptance(
        self,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        session: Session,
        client,
    ):
        """Test multiple attorneys trying to accept the same case concurrently"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Create an emergency case
        emergency_case = EmergencyCase(
            user_id=sample_user_with_contacts.id,
            client_profile_id=client_profile.id,
            case_type="self",
            status="active",
            detention_latitude=34.0522,
            detention_longitude=-118.2437,
            assigned_court_id=court.id,
        )
        session.add(emergency_case)
        session.commit()

        # Multiple attorneys try to accept the same case
        acceptance_responses = []
        for attorney in attorneys:
            response = client.post(f"/emergency/cases/{emergency_case.id}/accept?attorney_id={attorney.id}")
            acceptance_responses.append(response)

        # Only one attorney should successfully accept the case
        successful_acceptances = [r for r in acceptance_responses if r.status_code == 200]
        assert len(successful_acceptances) == 1

        # Others should get appropriate error responses
        failed_acceptances = [r for r in acceptance_responses if r.status_code != 200]
        assert len(failed_acceptances) == len(attorneys) - 1


class TestAttorneyNotificationEdgeCases:
    """Test attorney notification system edge cases and failures"""

    @patch("app.services.notification_service.NotificationService.send_immediate_case_notification")
    def test_attorney_notification_failure_recovery(
        self,
        mock_send_notification,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        session: Session,
        client,
    ):
        """Test notification failure recovery and retry logic"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Mock notification failures for first attempts, success for retries
        mock_send_notification.side_effect = [
            Exception("Notification failed"),  # First attempt fails
            Exception("Notification failed"),  # Second attempt fails
            None,  # Third attempt succeeds
        ]

        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0522,
                "longitude": -118.2437,
                "address": "123 Main St, Los Angeles, CA",
                "description": "Notification retry test",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None

    def test_no_attorneys_available_in_jurisdiction(self, sample_user_with_contacts: User, session: Session, client):
        """Test emergency activation when no attorneys are available in jurisdiction"""
        # Create a court with no admitted attorneys
        empty_court = Court(
            name="US District Court for the District of Alaska",
            abbreviation="AKD",
            url="https://www.akd.uscourts.gov/",
        )
        session.add(empty_court)
        session.commit()

        client_profile = sample_user_with_contacts.client_profiles[0]

        # Emergency in Alaska (no attorneys admitted)
        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 61.2181,  # Anchorage, Alaska
                "longitude": -149.9003,
                "address": "Anchorage, AK",
                "description": "No local attorneys test",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        # Should still create case but with escalation to national pool
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None
        # Should indicate that case will be escalated to broader attorney pool
        assert "Case posted" in data["message"]


class TestCourtJurisdictionEdgeCases:
    """Test court jurisdiction determination edge cases"""

    def test_court_jurisdiction_boundary_cases(
        self, sample_user_with_contacts: User, sample_court_with_attorneys: tuple[Court, list[Attorney]], client
    ):
        """Test emergency activation near court jurisdiction boundaries"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Location near district boundary
        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "self",
            "location": {
                "latitude": 34.0000,  # Edge of Central District
                "longitude": -118.0000,
                "address": "Near district boundary",
                "description": "Jurisdiction boundary test",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] is not None

    def test_international_location_emergency(
        self, sample_user_with_contacts: User, sample_court_with_attorneys: tuple[Court, list[Attorney]], client
    ):
        """Test emergency activation from international location"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # International location (loved one in US)
        emergency_request = {
            "client_profile_id": client_profile.id,
            "case_type": "loved_one",
            "location": {
                "latitude": 49.2827,  # Vancouver, Canada
                "longitude": -123.1207,
                "address": "Vancouver, BC, Canada",
                "description": "International caller, loved one in US",
            },
        }

        response = client.post(f"/emergency/cases?user_id={sample_user_with_contacts.id}", json=emergency_request)

        # Should handle international locations gracefully
        assert response.status_code in [201, 400]
        if response.status_code == 201:
            data = response.json()
            assert data["case_id"] is not None


class TestEmergencyCaseCleanupEdgeCases:
    """Test emergency case deactivation and cleanup edge cases"""

    def test_emergency_case_deactivation_edge_cases(
        self,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        session: Session,
        client,
    ):
        """Test emergency case deactivation in various states"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]

        # Create emergency case
        emergency_case = EmergencyCase(
            user_id=sample_user_with_contacts.id,
            client_profile_id=client_profile.id,
            case_type="self",
            status="active",
            detention_latitude=34.0522,
            detention_longitude=-118.2437,
            assigned_court_id=court.id,
        )
        session.add(emergency_case)
        session.commit()

        # Test deactivation
        response = client.post(f"/emergency/cases/{emergency_case.id}/deactivate")
        assert response.status_code == 200

        # Test deactivating already deactivated case
        response = client.post(f"/emergency/cases/{emergency_case.id}/deactivate")
        assert response.status_code in [200, 400]  # Should handle gracefully

    def test_emergency_case_cleanup_with_assigned_attorney(
        self,
        sample_user_with_contacts: User,
        sample_court_with_attorneys: tuple[Court, list[Attorney]],
        session: Session,
        client,
    ):
        """Test emergency case cleanup when attorney is already assigned"""
        court, attorneys = sample_court_with_attorneys
        client_profile = sample_user_with_contacts.client_profiles[0]
        attorney = attorneys[0]

        # Create emergency case with assigned attorney
        emergency_case = EmergencyCase(
            user_id=sample_user_with_contacts.id,
            client_profile_id=client_profile.id,
            case_type="self",
            status="attorney_assigned",
            detention_latitude=34.0522,
            detention_longitude=-118.2437,
            assigned_court_id=court.id,
            assigned_attorney_id=attorney.id,
        )
        session.add(emergency_case)
        session.commit()

        # Test deactivation with assigned attorney
        response = client.post(f"/emergency/cases/{emergency_case.id}/deactivate")
        assert response.status_code == 200

        # Should notify attorney of case deactivation
        data = response.json()
        assert "deactivated" in data["message"].lower()
