"""Service layer for managing Attorney Court Admissions."""

from sqlalchemy.orm import Session, joinedload

from app.exceptions import (
    AdmissionNotFoundError,
    AttorneyNotFoundError,
    CourtNotFoundError,
)
from app.models.attorney import Attorney
from app.models.court import Court


def add_admission(db: Session, *, attorney_id: int, court_id: int) -> bool:
    """Add a court admission link for an attorney.

    This directly manipulates the association through the Attorney object's relationship.

    Args:
        db: The database session.
        attorney_id: The ID of the attorney.
        court_id: The ID of the court.

    Returns:
        True if the admission link was newly created, False if it already existed.

    Raises:
        AttorneyNotFoundError: If the attorney is not found.
        CourtNotFoundError: If the court is not found.
    """
    # Fetch attorney, ensuring admitted_courts relationship is loaded
    attorney = (
        db.query(Attorney).options(joinedload(Attorney.admitted_courts)).filter(Attorney.id == attorney_id).first()
    )
    if not attorney:
        raise AttorneyNotFoundError(attorney_id=attorney_id)

    # Fetch court
    court = db.query(Court).filter(Court.id == court_id).first()
    if not court:
        raise CourtNotFoundError(court_id=court_id)

    # Check if the relationship already exists
    if court in attorney.admitted_courts:
        return False  # Already exists, no action needed

    # Add the relationship
    attorney.admitted_courts.append(court)

    # Flush to ensure the change is pending before returning, but don't commit
    # Commit/rollback should be handled by the calling scope (e.g., FastAPI dependency)
    db.flush()

    return True  # Link was newly created


def remove_admission(db: Session, *, attorney_id: int, court_id: int) -> bool:
    """Remove a court admission link for an attorney.

    This directly manipulates the association through the Attorney object's relationship.

    Args:
        db: The database session.
        attorney_id: The ID of the attorney.
        court_id: The ID of the court.

    Returns:
        True if the admission link was successfully removed.

    Raises:
        AttorneyNotFoundError: If the attorney is not found.
        CourtNotFoundError: If the court is not found.
        AdmissionNotFoundError: If the admission link does not exist between them.
    """
    # Fetch attorney, ensuring admitted_courts relationship is loaded
    attorney = (
        db.query(Attorney).options(joinedload(Attorney.admitted_courts)).filter(Attorney.id == attorney_id).first()
    )
    if not attorney:
        raise AttorneyNotFoundError(attorney_id=attorney_id)

    # Fetch court
    court = db.query(Court).filter(Court.id == court_id).first()
    if not court:
        raise CourtNotFoundError(court_id=court_id)

    # Check if the relationship exists before attempting removal
    if court not in attorney.admitted_courts:
        raise AdmissionNotFoundError(attorney_id=attorney_id, court_id=court_id)

    # Remove the relationship
    attorney.admitted_courts.remove(court)

    # Flush to ensure the change is pending before returning, but don't commit
    db.flush()

    return True  # Link was successfully removed
