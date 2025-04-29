from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.exceptions import (
    AdmissionNotFoundError,
    AttorneyNotFoundError,
    CourtNotFoundError,
)
from app.models.attorney import Attorney
from app.schemas import Attorney as AttorneySchema
from app.schemas import AttorneyCourtAdmissionCreate, AttorneyCreate, AttorneyUpdate

router = APIRouter(
    prefix="/attorneys",
    tags=["attorneys"],
    responses={404: {"description": "Not found"}, 500: {"description": "Internal server error"}},
)


@router.post(
    "/",
    response_model=AttorneySchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Attorney",
    description="Creates a new attorney record in the system",
    responses={
        201: {
            "description": "Attorney created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jane Doe",
                        "phone_number": "+15551234567",
                        "email": "jane.doe@example.com",
                        "zip_code": "12345",
                        "state": "CA",
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    }
                }
            },
        },
        422: {"description": "Validation Error"},
    },
)
def create_attorney(
    attorney: AttorneyCreate = Body(
        ...,
        description="Attorney information to create",
        example={
            "name": "Jane Doe",
            "phone_number": "+15551234567",
            "email": "jane.doe@example.com",
            "zip_code": "12345",
            "state": "CA",
        },
    ),
    db: Session = Depends(get_db),
):
    """
    Create a new attorney with the following information:

    - **name**: Full name of the attorney
    - **phone_number**: Contact phone number (E.164 format)
    - **email**: Email address
    - **zip_code**: US postal code (5 digits or 5+4 format)
    - **state**: Two-letter US state code (uppercase)
    """
    db_attorney = Attorney(
        name=attorney.name,
        phone_number=attorney.phone_number,
        email=attorney.email,
        zip_code=attorney.zip_code,
        state=attorney.state,
    )
    db.add(db_attorney)
    db.commit()
    db.refresh(db_attorney)
    return db_attorney


@router.get(
    "/",
    response_model=List[AttorneySchema],
    summary="List Attorneys",
    description="Retrieve a list of attorneys with optional filtering by state and zip code",
    responses={
        200: {
            "description": "List of attorneys",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Jane Doe",
                            "phone_number": "+15551234567",
                            "email": "jane.doe@example.com",
                            "zip_code": "12345",
                            "state": "CA",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00",
                        },
                        {
                            "id": 2,
                            "name": "John Smith",
                            "phone_number": "+15559876543",
                            "email": "john.smith@example.com",
                            "zip_code": "54321",
                            "state": "NY",
                            "created_at": "2023-01-02T00:00:00",
                            "updated_at": "2023-01-02T00:00:00",
                        },
                    ]
                }
            },
        }
    },
)
def read_attorneys(
    skip: int = Query(0, description="Number of records to skip for pagination", ge=0),
    limit: int = Query(100, description="Maximum number of records to return", ge=1, le=1000),
    state: Optional[str] = Query(None, description="Filter by state (two-letter code)", min_length=2, max_length=2),
    zip_code: Optional[str] = Query(None, description="Filter by zip code", min_length=5, max_length=10),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of attorneys with optional filtering capabilities.

    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **state**: Optional filter by US state (two-letter code)
    - **zip_code**: Optional filter by ZIP code

    Returns a paginated list of attorneys matching the criteria.
    """
    query = db.query(Attorney)

    # Apply filters if provided
    if state:
        query = query.filter(Attorney.state == state)
    if zip_code:
        query = query.filter(Attorney.zip_code == zip_code)

    attorneys = query.offset(skip).limit(limit).all()
    return attorneys


@router.get(
    "/{attorney_id}",
    response_model=AttorneySchema,
    summary="Get Attorney",
    description="Retrieve detailed information about a specific attorney by ID",
    responses={
        200: {
            "description": "Attorney details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jane Doe",
                        "phone_number": "+15551234567",
                        "email": "jane.doe@example.com",
                        "zip_code": "12345",
                        "state": "CA",
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00",
                    }
                }
            },
        },
        404: {
            "description": "Attorney not found",
            "content": {"application/json": {"example": {"detail": "Attorney not found"}}},
        },
    },
)
def read_attorney(
    attorney_id: int = Path(..., description="The ID of the attorney to retrieve", ge=1), db: Session = Depends(get_db)
):
    """
    Retrieve detailed information about a specific attorney by their unique ID.

    Parameters:
    - **attorney_id**: Unique identifier of the attorney

    Returns the complete attorney record if found, or a 404 error if not found.
    """
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")
    return db_attorney


@router.patch(
    "/{attorney_id}",
    response_model=AttorneySchema,
    summary="Update Attorney",
    description="Update an attorney's information (partial update)",
    responses={
        200: {
            "description": "Attorney updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Jane Smith",
                        "phone_number": "+15551234567",
                        "email": "jane.smith@example.com",
                        "zip_code": "12345",
                        "state": "CA",
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-02T00:00:00",
                    }
                }
            },
        },
        404: {
            "description": "Attorney not found",
            "content": {"application/json": {"example": {"detail": "Attorney not found"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def update_attorney(
    attorney_id: int = Path(..., description="The ID of the attorney to update", ge=1),
    attorney: AttorneyUpdate = Body(
        ...,
        description="Attorney information to update",
        example={"name": "Jane Smith", "email": "jane.smith@example.com"},
    ),
    db: Session = Depends(get_db),
):
    """
    Update an attorney's information (partial update).

    Parameters:
    - **attorney_id**: Unique identifier of the attorney to update
    - **attorney**: JSON object with fields to update. All fields are optional.

    Available fields to update:
    - **name**: Full name of the attorney
    - **phone_number**: Contact phone number (E.164 format)
    - **email**: Email address
    - **zip_code**: US postal code (5 digits or 5+4 format)
    - **state**: Two-letter US state code (uppercase)

    Returns the updated attorney record.
    """
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")

    # Update only provided fields
    update_data = attorney.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attorney, key, value)

    db.commit()
    db.refresh(db_attorney)
    return db_attorney


@router.delete(
    "/{attorney_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Attorney",
    description="Delete an attorney from the system",
    responses={
        204: {"description": "Attorney successfully deleted"},
        404: {
            "description": "Attorney not found",
            "content": {"application/json": {"example": {"detail": "Attorney not found"}}},
        },
    },
)
def delete_attorney(
    attorney_id: int = Path(..., description="The ID of the attorney to delete", ge=1), db: Session = Depends(get_db)
):
    """
    Delete an attorney from the system.

    Parameters:
    - **attorney_id**: Unique identifier of the attorney to delete

    Returns no content (204) on successful deletion.
    Raises a 404 error if the attorney is not found.
    """
    db_attorney = db.query(Attorney).filter(Attorney.id == attorney_id).first()
    if db_attorney is None:
        raise HTTPException(status_code=404, detail="Attorney not found")

    db.delete(db_attorney)
    db.commit()
    return None


@router.post(
    "/{attorney_id}/admissions",
    # response_model=AttorneyCourtAdmission, # Response model might need adjustment
    status_code=status.HTTP_201_CREATED,
    summary="Add Court Admission",
    description="Add a court admission for an attorney",
    responses={
        201: {
            "description": "Court admission added successfully",
            "content": {"application/json": {"example": {"attorney_id": 1, "court_id": 2}}},
        },
        404: {
            "description": "Attorney or Court not found",
            "content": {"application/json": {"example": {"detail": "Attorney or Court not found"}}},
        },
        409: {
            "description": "Court admission already exists",
            "content": {"application/json": {"example": {"detail": "Attorney is already admitted to this court"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def add_court_admission(
    attorney_id: int = Path(..., description="The ID of the attorney", ge=1),
    admission: AttorneyCourtAdmissionCreate = Body(..., description="Court admission to add", example={"court_id": 2}),
    db: Session = Depends(get_db),
):
    """Add a court admission link for an attorney by calling the service layer."""
    try:
        created = services.admission_service.add_admission(db=db, attorney_id=attorney_id, court_id=admission.court_id)
        if created:
            # Return a simple dict as AttorneyCourtAdmission model doesn't exist
            # Consider changing response_model if this is the final form
            return {"attorney_id": attorney_id, "court_id": admission.court_id}
        else:
            # Admission already exists
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attorney is already admitted to this court",
            )
    except AttorneyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CourtNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        # Catch unexpected errors
        # TODO: Add logging for the exception `e`
        # logger.error(f"Unexpected error adding admission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding the admission.",
        )


@router.delete(
    "/{attorney_id}/admissions/{court_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Court Admission",
    description="Remove a court admission for an attorney",
    responses={
        204: {"description": "Court admission successfully removed"},
        404: {
            "description": "Attorney, Court, or Admission not found",
            "content": {"application/json": {"example": {"detail": "Attorney court admission not found"}}},
        },
    },
)
def remove_court_admission(
    attorney_id: int = Path(..., description="The ID of the attorney", ge=1),
    court_id: int = Path(..., description="The ID of the court", ge=1),
    db: Session = Depends(get_db),
):
    """
    Remove a court admission for an attorney.

    Parameters:
    - **attorney_id**: ID of the attorney
    - **court_id**: ID of the court

    Returns no content on success.
    """
    try:
        services.admission_service.remove_admission(db=db, attorney_id=attorney_id, court_id=court_id)
        return None
    except (AttorneyNotFoundError, CourtNotFoundError, AdmissionNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        # Catch unexpected errors
        # TODO: Add logging for the exception
        # logger.error(f"Unexpected error removing admission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing the admission.",
        )
