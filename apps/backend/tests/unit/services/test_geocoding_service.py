"""
Unit tests for the geocoding service.
"""

from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.models.court import Court
from app.models.court_county import CourtCounty
from app.services.geocoding_service import GeocodingService


class TestGeocodingService:
    """Test cases for GeocodingService"""

    def test_validate_coordinates_valid(self, session: Session):
        """Test coordinate validation with valid coordinates"""
        service = GeocodingService(session)

        # Valid US coordinates
        assert service.validate_coordinates(40.7128, -74.0060)  # NYC
        assert service.validate_coordinates(34.0522, -118.2437)  # LA
        assert service.validate_coordinates(25.7617, -80.1918)  # Miami

    def test_validate_coordinates_invalid(self, session: Session):
        """Test coordinate validation with invalid coordinates"""
        service = GeocodingService(session)

        # Invalid coordinates
        assert not service.validate_coordinates(91.0, -74.0060)  # Invalid latitude
        assert not service.validate_coordinates(40.7128, -181.0)  # Invalid longitude
        assert not service.validate_coordinates(-91.0, -74.0060)  # Invalid latitude
        assert not service.validate_coordinates(40.7128, 181.0)  # Invalid longitude

    @patch("requests.get")
    def test_reverse_geocode_coordinates_success(self, mock_get, session: Session):
        """Test successful reverse geocoding"""
        service = GeocodingService(session)

        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "display_name": "123 Main St, New York, NY 10001, USA",
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

        result = service.reverse_geocode_coordinates(40.7128, -74.0060)

        assert result is not None
        assert result["city"] == "New York"
        assert result["county"] == "New York County"
        assert result["state"] == "New York"
        assert result["formatted_address"] == "123 Main St, New York, NY 10001, USA"
        assert result["geocoding_source"] == "Nominatim/OpenStreetMap"

    @patch("requests.get")
    def test_reverse_geocode_coordinates_failure(self, mock_get, session: Session):
        """Test failed reverse geocoding"""
        service = GeocodingService(session)

        # Mock failed API response
        mock_get.side_effect = Exception("API Error")

        result = service.reverse_geocode_coordinates(40.7128, -74.0060)
        assert result is None

    def test_extract_city_various_formats(self, db_session: Session):
        """Test city extraction from various address formats"""
        service = GeocodingService(db_session)

        # Test different city-level keys
        assert service._extract_city({"city": "New York"}) == "New York"
        assert service._extract_city({"town": "Small Town"}) == "Small Town"
        assert service._extract_city({"village": "Village Name"}) == "Village Name"
        assert service._extract_city({"municipality": "Municipality"}) == "Municipality"
        assert service._extract_city({"hamlet": "Hamlet"}) == "Hamlet"
        assert service._extract_city({}) == ""

        # Test priority order (city should be preferred over town)
        assert service._extract_city({"city": "New York", "town": "Old Town"}) == "New York"

    def test_find_court_by_county_state(self, db_session: Session):
        """Test finding court by county and state"""
        service = GeocodingService(db_session)

        # Create test data
        court = Court(
            name="U.S. District Court for the Southern District of New York", abbreviation="SDNY", type="district"
        )
        db_session.add(court)
        db_session.flush()

        court_county = CourtCounty(court_id=court.id, county="New York", state="New York")
        db_session.add(court_county)
        db_session.commit()

        # Test finding court
        found_court = service._find_court_by_county_state("New York County", "New York")
        assert found_court is not None
        assert found_court.abbreviation == "SDNY"

        # Test with "County" suffix
        found_court = service._find_court_by_county_state("New York", "New York")
        assert found_court is not None
        assert found_court.abbreviation == "SDNY"

        # Test not found
        not_found = service._find_court_by_county_state("Nonexistent County", "Nonexistent State")
        assert not_found is None

    def test_find_court_by_state(self, db_session: Session):
        """Test finding court by state for single-district states"""
        service = GeocodingService(db_session)

        # Create test data
        court = Court(name="U.S. District Court for the District of Delaware", abbreviation="D. Del.", type="district")
        db_session.add(court)
        db_session.commit()

        # Test finding court by state
        found_court = service._find_court_by_state("Delaware")
        assert found_court is not None
        assert found_court.abbreviation == "D. Del."

        # Test not found
        not_found = service._find_court_by_state("Nonexistent State")
        assert not_found is None

    @patch("app.services.geocoding_service.GeocodingService.reverse_geocode_coordinates")
    @patch("app.services.geocoding_service.GeocodingService.determine_court_jurisdiction")
    def test_geocode_and_determine_jurisdiction_success(self, mock_determine, mock_geocode, db_session: Session):
        """Test complete geocoding and jurisdiction determination"""
        service = GeocodingService(db_session)

        # Mock geocoding result
        mock_address = {
            "city": "New York",
            "county": "New York County",
            "state": "New York",
            "formatted_address": "123 Main St, New York, NY 10001, USA",
        }
        mock_geocode.return_value = mock_address

        # Mock court result
        mock_court = Court(name="SDNY", abbreviation="SDNY", type="district")
        mock_determine.return_value = mock_court

        address_data, court = service.geocode_and_determine_jurisdiction(40.7128, -74.0060)

        assert address_data == mock_address
        assert court == mock_court

    @patch("app.services.geocoding_service.GeocodingService.reverse_geocode_coordinates")
    def test_geocode_and_determine_jurisdiction_failure(self, mock_geocode, db_session: Session):
        """Test failed geocoding and jurisdiction determination"""
        service = GeocodingService(db_session)

        # Mock failed geocoding
        mock_geocode.return_value = None

        address_data, court = service.geocode_and_determine_jurisdiction(40.7128, -74.0060)

        assert address_data is None
        assert court is None

    @patch("time.sleep")
    @patch("requests.get")
    def test_rate_limiting(self, mock_get, mock_sleep, db_session: Session):
        """Test that rate limiting is applied"""
        service = GeocodingService(db_session)

        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "display_name": "Test Address",
            "address": {"city": "Test City", "state": "Test State"},
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service.reverse_geocode_coordinates(40.7128, -74.0060)

        # Verify rate limiting sleep was called
        mock_sleep.assert_called_once_with(1)  # 1 second delay

    def test_user_agent_header(self, db_session: Session):
        """Test that proper User-Agent header is sent"""
        service = GeocodingService(db_session)

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"error": "test"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            service.reverse_geocode_coordinates(40.7128, -74.0060)

            # Check that User-Agent header was included
            call_args = mock_get.call_args
            headers = call_args[1]["headers"]
            assert "User-Agent" in headers
            assert "HabeasApp" in headers["User-Agent"]
