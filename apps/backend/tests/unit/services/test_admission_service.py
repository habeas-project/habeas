import pytest

from app.exceptions import (
    AdmissionNotFoundError,
    AttorneyNotFoundError,
    CourtNotFoundError,
)
from app.models.attorney import Attorney
from app.models.court import Court
from app.services import admission_service


@pytest.mark.unit
class TestAddAdmission:
    """Tests for the add_admission function."""

    def test_add_admission_success(self, db_session):
        """Test that adding a valid admission works correctly."""
        # Create test attorney and court
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add_all([attorney, court])
        db_session.commit()

        # Add the admission
        result = admission_service.add_admission(db=db_session, attorney_id=attorney.id, court_id=court.id)

        # Verify the result and the relationship
        assert result is True
        assert court in attorney.admitted_courts
        assert attorney in court.admitted_attorneys

    def test_add_admission_duplicate(self, db_session):
        """Test that adding a duplicate admission returns False."""
        # Create test attorney and court
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add_all([attorney, court])
        db_session.commit()

        # Add the admission for the first time
        admission_service.add_admission(db=db_session, attorney_id=attorney.id, court_id=court.id)

        # Try to add the same admission again
        result = admission_service.add_admission(db=db_session, attorney_id=attorney.id, court_id=court.id)

        # Verify the result
        assert result is False

    def test_add_admission_attorney_not_found(self, db_session):
        """Test that attempting to add an admission for a non-existent attorney raises AttorneyNotFoundError."""
        # Create only a court
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add(court)
        db_session.commit()

        # Try to add an admission for a non-existent attorney
        with pytest.raises(AttorneyNotFoundError) as excinfo:
            admission_service.add_admission(db=db_session, attorney_id=9999, court_id=court.id)

        # Verify the error message
        assert "9999" in str(excinfo.value)

    def test_add_admission_court_not_found(self, db_session):
        """Test that attempting to add an admission for a non-existent court raises CourtNotFoundError."""
        # Create only an attorney
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        db_session.add(attorney)
        db_session.commit()

        # Try to add an admission for a non-existent court
        with pytest.raises(CourtNotFoundError) as excinfo:
            admission_service.add_admission(db=db_session, attorney_id=attorney.id, court_id=9999)

        # Verify the error message
        assert "9999" in str(excinfo.value)


@pytest.mark.unit
class TestRemoveAdmission:
    """Tests for the remove_admission function."""

    def test_remove_admission_success(self, db_session):
        """Test that removing a valid admission works correctly."""
        # Create test attorney and court
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add_all([attorney, court])
        db_session.commit()

        # Add the admission
        attorney.admitted_courts.append(court)
        db_session.commit()

        # Remove the admission
        result = admission_service.remove_admission(db=db_session, attorney_id=attorney.id, court_id=court.id)

        # Verify the result and the relationship
        assert result is True
        assert court not in attorney.admitted_courts
        assert attorney not in court.admitted_attorneys

    def test_remove_admission_attorney_not_found(self, db_session):
        """Test that attempting to remove an admission for a non-existent attorney raises AttorneyNotFoundError."""
        # Create only a court
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add(court)
        db_session.commit()

        # Try to remove an admission for a non-existent attorney
        with pytest.raises(AttorneyNotFoundError) as excinfo:
            admission_service.remove_admission(db=db_session, attorney_id=9999, court_id=court.id)

        # Verify the error message
        assert "9999" in str(excinfo.value)

    def test_remove_admission_court_not_found(self, db_session):
        """Test that attempting to remove an admission for a non-existent court raises CourtNotFoundError."""
        # Create only an attorney
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        db_session.add(attorney)
        db_session.commit()

        # Try to remove an admission for a non-existent court
        with pytest.raises(CourtNotFoundError) as excinfo:
            admission_service.remove_admission(db=db_session, attorney_id=attorney.id, court_id=9999)

        # Verify the error message
        assert "9999" in str(excinfo.value)

    def test_remove_admission_not_found(self, db_session):
        """Test that attempting to remove a non-existent admission raises AdmissionNotFoundError."""
        # Create test attorney and court (but no admission between them)
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add_all([attorney, court])
        db_session.commit()

        # Try to remove a non-existent admission
        with pytest.raises(AdmissionNotFoundError) as excinfo:
            admission_service.remove_admission(db=db_session, attorney_id=attorney.id, court_id=court.id)

        # Verify the error message
        assert str(attorney.id) in str(excinfo.value) and str(court.id) in str(excinfo.value)
