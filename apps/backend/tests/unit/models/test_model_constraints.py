import pytest

from sqlalchemy.exc import IntegrityError

from app.models.attorney import Attorney
from app.models.court import Court


@pytest.mark.unit
def test_attorney_required_fields(session):
    """Test that attorney model enforces required fields."""
    # Missing name
    attorney_missing_name = Attorney(
        phone_number="+15551234567", email="test.attorney@example.com", zip_code="12345", state="CA"
    )
    session.add(attorney_missing_name)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing phone_number
    attorney_missing_phone = Attorney(
        name="Test Attorney", email="test.attorney@example.com", zip_code="12345", state="CA"
    )
    session.add(attorney_missing_phone)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing email
    attorney_missing_email = Attorney(name="Test Attorney", phone_number="+15551234567", zip_code="12345", state="CA")
    session.add(attorney_missing_email)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing zip_code
    attorney_missing_zip = Attorney(
        name="Test Attorney", phone_number="+15551234567", email="test.attorney@example.com", state="CA"
    )
    session.add(attorney_missing_zip)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing state
    attorney_missing_state = Attorney(
        name="Test Attorney", phone_number="+15551234567", email="test.attorney@example.com", zip_code="12345"
    )
    session.add(attorney_missing_state)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


@pytest.mark.unit
def test_attorney_unique_email(session):
    """Test that attorney model enforces unique email constraint."""
    # Create first attorney with unique email to avoid conflicts with other tests
    attorney1 = Attorney(
        name="First Attorney",
        phone_number="+15551234567",
        email="unique_test_duplicate@example.com",
        zip_code="12345",
        state="CA",
    )
    session.add(attorney1)
    session.commit()

    # Try to create second attorney with same email
    attorney2 = Attorney(
        name="Second Attorney",
        phone_number="+15559876543",
        email="unique_test_duplicate@example.com",  # Same email as attorney1
        zip_code="67890",
        state="NY",
    )
    session.add(attorney2)

    # This should raise an IntegrityError due to unique constraint violation
    with pytest.raises(IntegrityError):
        session.commit()

    # Rollback is automatically called by pytest.raises, but let's be explicit
    session.rollback()


@pytest.mark.unit
def test_court_required_fields(session):
    """Test that court model enforces required fields."""
    # Missing name
    court_missing_name = Court(abbreviation="TDC", url="https://testcourt.gov")
    session.add(court_missing_name)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing abbreviation
    court_missing_abbr = Court(name="Test District Court", url="https://testcourt.gov")
    session.add(court_missing_abbr)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()

    # Missing url
    court_missing_url = Court(name="Test District Court", abbreviation="TDC")
    session.add(court_missing_url)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


@pytest.mark.unit
def test_court_unique_abbreviation(session):
    """Test that court model enforces unique abbreviation constraint."""
    # Create first court
    court1 = Court(
        name="First Court",
        abbreviation="DUPC",  # Duplicate abbreviation
        url="https://firstcourt.gov",
    )
    session.add(court1)
    session.commit()

    # Try to create second court with same abbreviation
    court2 = Court(
        name="Second Court",
        abbreviation="DUPC",  # Same abbreviation as court1
        url="https://secondcourt.gov",
    )
    session.add(court2)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()
