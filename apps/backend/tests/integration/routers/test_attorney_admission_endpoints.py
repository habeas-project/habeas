import pytest

from fastapi import status

from app.models.attorney import Attorney
from app.models.court import Court


@pytest.mark.integration
class TestAttorneyAdmissionEndpoints:
    """Integration tests for the attorney admission API endpoints."""

    def test_add_court_admission_success(self, client, db_session):
        """Test that adding a court admission works correctly."""
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

        # Make API request to add admission
        response = client.post(f"/attorneys/{attorney.id}/admissions", json={"court_id": court.id})

        # Verify the response and the relationship
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"attorney_id": attorney.id, "court_id": court.id}

        # Verify the relationship in the database
        db_attorney = db_session.query(Attorney).filter(Attorney.id == attorney.id).first()
        db_court = db_session.query(Court).filter(Court.id == court.id).first()
        assert db_court in db_attorney.admitted_courts
        assert db_attorney in db_court.admitted_attorneys

    def test_add_court_admission_duplicate(self, client, db_session):
        """Test that adding a duplicate court admission returns 409 Conflict."""
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

        # Make API request to add the same admission again
        response = client.post(f"/attorneys/{attorney.id}/admissions", json={"court_id": court.id})

        # Verify the response
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already admitted" in response.json()["detail"].lower()

    def test_add_court_admission_attorney_not_found(self, client, db_session):
        """Test that adding a court admission for a non-existent attorney returns 404."""
        # Create test court only
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add(court)
        db_session.commit()

        # Make API request with non-existent attorney ID
        response = client.post("/attorneys/9999/admissions", json={"court_id": court.id})

        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "attorney not found" in response.json()["detail"].lower()

    def test_add_court_admission_court_not_found(self, client, db_session):
        """Test that adding a non-existent court admission returns 404."""
        # Create test attorney only
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        db_session.add(attorney)
        db_session.commit()

        # Make API request with non-existent court ID
        response = client.post(f"/attorneys/{attorney.id}/admissions", json={"court_id": 9999})

        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "court not found" in response.json()["detail"].lower()

    def test_remove_court_admission_success(self, client, db_session):
        """Test that removing a court admission works correctly."""
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

        # Make API request to remove the admission
        response = client.delete(f"/attorneys/{attorney.id}/admissions/{court.id}")

        # Verify the response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""  # Empty response body for 204

        # Verify the relationship is removed in the database
        db_attorney = db_session.query(Attorney).filter(Attorney.id == attorney.id).first()
        db_court = db_session.query(Court).filter(Court.id == court.id).first()
        assert db_court not in db_attorney.admitted_courts
        assert db_attorney not in db_court.admitted_attorneys

    def test_remove_court_admission_attorney_not_found(self, client, db_session):
        """Test that removing a court admission for a non-existent attorney returns 404."""
        # Create test court only
        court = Court(name="Test District Court", jurisdiction="Federal", location="CA")
        db_session.add(court)
        db_session.commit()

        # Make API request with non-existent attorney ID
        response = client.delete(f"/attorneys/9999/admissions/{court.id}")

        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "attorney not found" in response.json()["detail"].lower()

    def test_remove_court_admission_court_not_found(self, client, db_session):
        """Test that removing a non-existent court admission returns 404."""
        # Create test attorney only
        attorney = Attorney(
            name="Test Attorney",
            phone_number="+15551234567",
            email="test.attorney@example.com",
            zip_code="12345",
            state="CA",
        )
        db_session.add(attorney)
        db_session.commit()

        # Make API request with non-existent court ID
        response = client.delete(f"/attorneys/{attorney.id}/admissions/9999")

        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "court not found" in response.json()["detail"].lower()

    def test_remove_court_admission_not_found(self, client, db_session):
        """Test that removing a non-existent admission returns 404."""
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

        # Make API request to remove a non-existent admission
        response = client.delete(f"/attorneys/{attorney.id}/admissions/{court.id}")

        # Verify the response
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "admission not found" in response.json()["detail"].lower()
