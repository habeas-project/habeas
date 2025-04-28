import pytest

from app.models.attorney import Attorney
from app.models.court import Court


@pytest.mark.unit
def test_attorney_court_admission_relationship(db_session):
    """Test that the many-to-many relationship between Attorney and Court works correctly."""
    # Create test attorney
    attorney = Attorney(
        name="Test Attorney",
        phone_number="+15551234567",
        email="test.attorney@example.com",
        zip_code="12345",
        state="CA",
    )

    # Create test court
    court = Court(name="Test District Court", abbreviation="TDC", url="https://testcourt.gov")

    # Add both objects to the database
    db_session.add_all([attorney, court])
    db_session.commit()

    # Test adding court to attorney's admitted courts
    attorney.admitted_courts.append(court)
    db_session.commit()

    # Verify the relationship from both directions
    assert court in attorney.admitted_courts
    assert attorney in court.admitted_attorneys

    # Test removing the relationship
    attorney.admitted_courts.remove(court)
    db_session.commit()

    # Verify the relationship is removed
    assert court not in attorney.admitted_courts
    assert attorney not in court.admitted_attorneys


@pytest.mark.unit
def test_attorney_court_multiple_admissions(db_session):
    """Test that an attorney can be admitted to multiple courts."""
    # Create test attorney
    attorney = Attorney(
        name="Multiple Court Attorney",
        phone_number="+15551234500",
        email="multi.court@example.com",
        zip_code="12345",
        state="CA",
    )

    # Create multiple test courts with unique abbreviations
    court1 = Court(name="First District Court", abbreviation="FDC", url="https://firstcourt.gov")

    court2 = Court(name="Second District Court", abbreviation="SDC", url="https://secondcourt.gov")

    court3 = Court(name="Third District Court", abbreviation="THC", url="https://thirdcourt.gov")

    # Add all objects to the database
    db_session.add_all([attorney, court1, court2, court3])
    db_session.commit()

    # Add multiple courts to attorney
    attorney.admitted_courts.extend([court1, court2, court3])
    db_session.commit()

    # Verify all courts are in the relationship
    assert len(attorney.admitted_courts) == 3
    assert court1 in attorney.admitted_courts
    assert court2 in attorney.admitted_courts
    assert court3 in attorney.admitted_courts

    # Verify attorney is in all courts' admitted_attorneys
    assert attorney in court1.admitted_attorneys
    assert attorney in court2.admitted_attorneys
    assert attorney in court3.admitted_attorneys


@pytest.mark.unit
def test_court_multiple_attorneys(db_session):
    """Test that a court can have multiple admitted attorneys."""
    # Create multiple attorneys
    attorney1 = Attorney(
        name="First Attorney",
        phone_number="+15551111111",
        email="first.attorney@example.com",
        zip_code="12345",
        state="CA",
    )

    attorney2 = Attorney(
        name="Second Attorney",
        phone_number="+15552222222",
        email="second.attorney@example.com",
        zip_code="12345",
        state="NY",
    )

    attorney3 = Attorney(
        name="Third Attorney",
        phone_number="+15553333333",
        email="third.attorney@example.com",
        zip_code="12345",
        state="TX",
    )

    # Create test court
    court = Court(name="Popular District Court", abbreviation="PDC", url="https://popularcourt.gov")

    # Add all objects to the database
    db_session.add_all([attorney1, attorney2, attorney3, court])
    db_session.commit()

    # Add all attorneys to the court
    court.admitted_attorneys.extend([attorney1, attorney2, attorney3])
    db_session.commit()

    # Verify all attorneys are admitted to the court
    assert len(court.admitted_attorneys) == 3
    assert attorney1 in court.admitted_attorneys
    assert attorney2 in court.admitted_attorneys
    assert attorney3 in court.admitted_attorneys

    # Verify the court is in all attorneys' admitted_courts
    assert court in attorney1.admitted_courts
    assert court in attorney2.admitted_courts
    assert court in attorney3.admitted_courts
