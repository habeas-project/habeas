import pytest

from sqlalchemy.exc import IntegrityError

from app.models.attorney import Attorney
from app.models.court import Court


@pytest.mark.unit
def test_attorney_required_fields(db_session):
    """Test that attorney model enforces required fields."""
    # Missing name
    attorney_missing_name = Attorney(
        phone_number="+15551234567", email="test.attorney@example.com", zip_code="12345", state="CA"
    )
    db_session.add(attorney_missing_name)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing phone_number
    attorney_missing_phone = Attorney(
        name="Test Attorney", email="test.attorney@example.com", zip_code="12345", state="CA"
    )
    db_session.add(attorney_missing_phone)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing email
    attorney_missing_email = Attorney(name="Test Attorney", phone_number="+15551234567", zip_code="12345", state="CA")
    db_session.add(attorney_missing_email)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing zip_code
    attorney_missing_zip = Attorney(
        name="Test Attorney", phone_number="+15551234567", email="test.attorney@example.com", state="CA"
    )
    db_session.add(attorney_missing_zip)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing state
    attorney_missing_state = Attorney(
        name="Test Attorney", phone_number="+15551234567", email="test.attorney@example.com", zip_code="12345"
    )
    db_session.add(attorney_missing_state)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


@pytest.mark.unit
def test_attorney_unique_email(db_session):
    """Test that attorney model enforces unique email constraint."""
    # Create first attorney
    attorney1 = Attorney(
        name="First Attorney", phone_number="+15551234567", email="duplicate@example.com", zip_code="12345", state="CA"
    )
    db_session.add(attorney1)
    db_session.commit()

    # Try to create second attorney with same email
    attorney2 = Attorney(
        name="Second Attorney",
        phone_number="+15559876543",
        email="duplicate@example.com",  # Same email as attorney1
        zip_code="67890",
        state="NY",
    )
    db_session.add(attorney2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


@pytest.mark.unit
def test_court_required_fields(db_session):
    """Test that court model enforces required fields."""
    # Missing name
    court_missing_name = Court(abbreviation="TDC", url="https://testcourt.gov")
    db_session.add(court_missing_name)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing abbreviation
    court_missing_abbr = Court(name="Test District Court", url="https://testcourt.gov")
    db_session.add(court_missing_abbr)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

    # Missing url
    court_missing_url = Court(name="Test District Court", abbreviation="TDC")
    db_session.add(court_missing_url)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


@pytest.mark.unit
def test_court_unique_abbreviation(db_session):
    """Test that court model enforces unique abbreviation constraint."""
    # Create first court
    court1 = Court(
        name="First Court",
        abbreviation="DUPC",  # Duplicate abbreviation
        url="https://firstcourt.gov",
    )
    db_session.add(court1)
    db_session.commit()

    # Try to create second court with same abbreviation
    court2 = Court(
        name="Second Court",
        abbreviation="DUPC",  # Same abbreviation as court1
        url="https://secondcourt.gov",
    )
    db_session.add(court2)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
