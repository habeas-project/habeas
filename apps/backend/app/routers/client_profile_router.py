import logging

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.client_profile import ClientProfile
from app.models.user import User
from app.schemas.client_profile import (
    ClientProfileCreate,
    ClientProfileList,
    ClientProfileResponse,
    ClientProfileUpdate,
)

# Add logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/client-profiles",
    tags=["client-profiles"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=ClientProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Client Profile",
    description="Create a new client profile for a user",
)
def create_client_profile(
    profile_data: ClientProfileCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new client profile linked to a user.

    This endpoint allows users (particularly client helpers) to create
    additional client profiles for family members or others they help.
    """
    try:
        # Verify user exists
        user = db.query(User).filter(User.id == profile_data.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Create new client profile
        db_profile = ClientProfile(
            user_id=profile_data.user_id,
            profile_name=profile_data.profile_name,
            is_self=profile_data.is_self,
            first_name=profile_data.first_name,
            last_name=profile_data.last_name,
            country_of_birth=profile_data.country_of_birth,
            nationality=profile_data.nationality,
            birth_date=profile_data.birth_date,
            alien_registration_number=profile_data.alien_registration_number,
            passport_number=profile_data.passport_number,
            school_name=profile_data.school_name,
            student_id_number=profile_data.student_id_number,
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)

        return ClientProfileResponse.model_validate(db_profile)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error creating client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create profile due to data conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create profile due to internal error"
        )


@router.get(
    "/user/{user_id}",
    response_model=List[ClientProfileList],
    summary="Get User's Client Profiles",
    description="Get all client profiles for a specific user",
)
def get_user_profiles(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve all client profiles associated with a user.

    This endpoint is useful for client helpers who manage multiple
    profiles for family members or others.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get all profiles for the user
    profiles = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).all()

    return [ClientProfileList.model_validate(profile) for profile in profiles]


@router.get(
    "/{profile_id}",
    response_model=ClientProfileResponse,
    summary="Get Client Profile",
    description="Get a specific client profile by ID",
)
def get_client_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific client profile by its ID.
    """
    profile = db.query(ClientProfile).filter(ClientProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")

    return ClientProfileResponse.model_validate(profile)


@router.put(
    "/{profile_id}",
    response_model=ClientProfileResponse,
    summary="Update Client Profile",
    description="Update an existing client profile",
)
def update_client_profile(
    profile_id: int,
    profile_data: ClientProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing client profile with new information.
    """
    try:
        # Get existing profile
        db_profile = db.query(ClientProfile).filter(ClientProfile.id == profile_id).first()
        if not db_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")

        # Update only provided fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)

        db.commit()
        db.refresh(db_profile)

        return ClientProfileResponse.model_validate(db_profile)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error updating client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update profile due to data conflict"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile due to internal error"
        )


@router.delete(
    "/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Client Profile",
    description="Delete a client profile",
)
def delete_client_profile(
    profile_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a client profile.

    Note: This will also delete any related emergency contacts
    due to cascading delete constraints.
    """
    profile = db.query(ClientProfile).filter(ClientProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found")

    try:
        db.delete(profile)
        db.commit()

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error deleting client profile: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete profile due to related data")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting client profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete profile due to internal error"
        )
