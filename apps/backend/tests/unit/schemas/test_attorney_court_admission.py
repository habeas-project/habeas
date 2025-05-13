import pytest

from pydantic import ValidationError

from app.schemas import AttorneyCourtAdmissionCreate


@pytest.mark.unit
class TestAttorneyCourtAdmissionCreate:
    """Tests for the AttorneyCourtAdmissionCreate schema."""

    def test_valid_admission_schema(self):
        """Test that a valid court ID is accepted."""
        # Create a valid admission schema
        admission = AttorneyCourtAdmissionCreate(court_id=1)

        # Verify fields
        assert admission.court_id == 1

    def test_invalid_court_id_type(self):
        """Test that non-integer court_id is rejected."""
        # Try to create a schema with a string court_id
        with pytest.raises(ValidationError) as excinfo:
            AttorneyCourtAdmissionCreate(court_id="invalid")

        # Verify the error message
        errors = excinfo.value.errors()
        assert any("court_id" in error["loc"] for error in errors)

        # In Pydantic v2, the error type is 'int_parsing' instead of 'type_error'
        assert any("int_parsing" in error["type"] or "type_error" in error["type"] for error in errors)

    def test_non_positive_court_id(self):
        """Test that non-positive court_id values are rejected."""
        # Try with zero court_id
        with pytest.raises(ValidationError) as excinfo:
            AttorneyCourtAdmissionCreate(court_id=0)

        # Verify the error message
        errors = excinfo.value.errors()
        assert any("court_id" in error["loc"] for error in errors)
        assert any("greater than" in error["msg"].lower() for error in errors)

        # Try with negative court_id
        with pytest.raises(ValidationError) as excinfo:
            AttorneyCourtAdmissionCreate(court_id=-1)

        # Verify the error message
        errors = excinfo.value.errors()
        assert any("court_id" in error["loc"] for error in errors)
        assert any("greater than" in error["msg"].lower() for error in errors)

    def test_missing_court_id(self):
        """Test that missing court_id is rejected."""
        # Try to create a schema with a missing court_id
        with pytest.raises(ValidationError) as excinfo:
            AttorneyCourtAdmissionCreate()

        # Verify the error message
        errors = excinfo.value.errors()
        assert any("court_id" in error["loc"] for error in errors)
        assert any("field required" in error["msg"].lower() for error in errors)
