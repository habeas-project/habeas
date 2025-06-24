"""
Integration tests for geocoding with emergency case creation.
"""

from datetime import date
from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.models.client_profile import ClientProfile
from app.models.court import Court
from app.models.court_county import CourtCounty
from app.models.emergency_contact import EmergencyContact
from app.models.user import User
from app.schemas.emergency_case import EmergencyActivationRequest, LocationData
from app.services.emergency_service import EmergencyService


class TestGeocodingIntegration:
    """Integration tests for geocoding with emergency services"""

    @patch("app.services.geocoding_service.requests.get")
    def test_emergency_case_creation_with_geocoding(self, mock_get, session: Session):
        """Test that emergency case creation uses geocoding to determine court jurisdiction"""

        # Create test data
        user = User(cognito_id="test-user-1", user_type="client_helper", primary_role="client_helper")
        session.add(user)
        session.flush()

        client_profile = ClientProfile(
            user_id=user.id,
            profile_name="Test Profile",
            first_name="John",
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            country_of_birth="United States",
        )
        session.add(client_profile)
        session.flush()

        emergency_contact = EmergencyContact(
            client_profile_id=client_profile.id,
            full_name="Jane Doe",
            relationship="spouse",
            phone_number="555-0124",
            email="jane@example.com",
        )
        session.add(emergency_contact)

        # Create court and county mapping
        court = Court(
            name="U.S. District Court for the Southern District of New York",
            abbreviation="SDNY",
            url="https://www.nysd.uscourts.gov/",
        )
        session.add(court)
        session.flush()

        court_county = CourtCounty(court_id=court.id, county_name="New York", state="New York")
        session.add(court_county)
        session.commit()

        # Mock geocoding API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "display_name": "123 Broadway, New York, NY 10001, USA",
            "address": {
                "city": "New York",
                "county": "New York County",
                "state": "New York",
                "country": "United States",
                "postcode": "10001",
            },
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create emergency service
        service = EmergencyService(session)

        # Create emergency activation request with GPS coordinates
        request = EmergencyActivationRequest(
            client_profile_id=client_profile.id,
            case_type="self",
            location=LocationData(latitude=40.7128, longitude=-74.0060, address=None, description="Near Times Square"),
        )

        # Create emergency case
        emergency_case, attorneys_notified = service.create_emergency_case(user.id, request)

        # Verify case was created with geocoded information
        assert emergency_case is not None
        assert emergency_case.user_id == user.id
        assert emergency_case.client_profile_id == client_profile.id
        assert emergency_case.case_type == "self"
        assert emergency_case.detention_latitude == 40.7128
        assert emergency_case.detention_longitude == -74.0060

        # Verify geocoded address was used
        assert emergency_case.detention_address == "123 Broadway, New York, NY 10001, USA"

        # Verify court jurisdiction was determined
        assert emergency_case.assigned_court_id == court.id
        assert emergency_case.assigned_court.abbreviation == "SDNY"

        # Verify geocoding API was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "nominatim.openstreetmap.org" in call_args[0][0]
        assert call_args[1]["params"]["lat"] == 40.7128
        assert call_args[1]["params"]["lon"] == -74.0060

    def test_emergency_case_creation_geocoding_fallback(self, session: Session):
        """Test that emergency case creation falls back gracefully when geocoding fails"""

        # Create minimal test data
        user = User(cognito_id="test-user-2", user_type="client_helper", primary_role="client_helper")
        session.add(user)
        session.flush()

        client_profile = ClientProfile(
            user_id=user.id,
            profile_name="Test Profile 2",
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1985, 5, 15),
            country_of_birth="United States",
        )
        session.add(client_profile)
        session.flush()

        emergency_contact = EmergencyContact(
            client_profile_id=client_profile.id,
            full_name="John Smith",
            relationship="spouse",
            phone_number="555-0126",
            email="john@example.com",
        )
        session.add(emergency_contact)

        # Create a fallback court
        court = Court(
            name="U.S. District Court for the Eastern District of New York",
            abbreviation="EDNY",
            url="https://www.nyed.uscourts.gov/",
        )
        session.add(court)
        session.commit()

        # Create emergency service
        service = EmergencyService(session)

        # Create request with invalid coordinates (should trigger fallback)
        request = EmergencyActivationRequest(
            client_profile_id=client_profile.id,
            case_type="self",
            location=LocationData(
                latitude=200.0,  # Invalid latitude
                longitude=-74.0060,
                address="Brooklyn, NY",
                description="Somewhere in Brooklyn",
            ),
        )

        # Create emergency case
        emergency_case, attorneys_notified = service.create_emergency_case(user.id, request)

        # Verify case was created despite geocoding failure
        assert emergency_case is not None
        assert emergency_case.user_id == user.id
        assert emergency_case.detention_latitude == 200.0  # Original coordinates preserved
        assert emergency_case.detention_longitude == -74.0060

        # Verify fallback address was used
        assert emergency_case.detention_address == "Brooklyn, NY"

        # Verify a court was still assigned (fallback logic)
        assert emergency_case.assigned_court_id is not None

    def test_manual_location_without_gps(self, session: Session):
        """Test emergency case creation with manual location entry (no GPS)"""

        # Create test data
        user = User(cognito_id="test-user-3", user_type="client_helper", primary_role="client_helper")
        session.add(user)
        session.flush()

        client_profile = ClientProfile(
            user_id=user.id,
            profile_name="Test Profile 3",
            first_name="Mike",
            last_name="Johnson",
            birth_date=date(1992, 3, 10),
            country_of_birth="United States",
        )
        session.add(client_profile)
        session.flush()

        emergency_contact = EmergencyContact(
            client_profile_id=client_profile.id,
            full_name="Sarah Johnson",
            relationship="wife",
            phone_number="555-0128",
            email="sarah@example.com",
        )
        session.add(emergency_contact)
        session.commit()

        # Create emergency service
        service = EmergencyService(session)

        # Create request with manual location (no GPS coordinates)
        request = EmergencyActivationRequest(
            client_profile_id=client_profile.id,
            case_type="self",
            location=LocationData(
                latitude=None, longitude=None, address="Los Angeles, CA 90210", description="Beverly Hills area"
            ),
        )

        # Create emergency case
        emergency_case, attorneys_notified = service.create_emergency_case(user.id, request)

        # Verify case was created with manual location
        assert emergency_case is not None
        assert emergency_case.user_id == user.id
        assert emergency_case.detention_latitude is None
        assert emergency_case.detention_longitude is None
        assert emergency_case.detention_address == "Los Angeles, CA 90210"
        assert emergency_case.location_description == "Beverly Hills area"

        # Verify a court was assigned (fallback logic should work)
        assert emergency_case.assigned_court_id is not None
