import logging

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.models.attorney import Attorney
from app.models.client_profile import ClientProfile
from app.models.user import User
from app.schemas.unified_signup import (
    MultiProfileSignupRequest,
    MultiProfileSignupResponse,
    RoleSpecificData,
    UnifiedSignupRequest,
    UnifiedSignupResponse,
)
from app.schemas.user import UserResponse

# Add logger
logger = logging.getLogger(__name__)

# OAuth 2.0 token type constant (not a password, ignore bandit B105)
OAUTH_TOKEN_TYPE = "bearer"  # nosec B105

router = APIRouter(
    prefix="/signup",
    tags=["unified-signup"],
    responses={400: {"description": "Bad Request"}, 422: {"description": "Validation Error"}},
)


@router.post(
    "/unified",
    response_model=UnifiedSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Unified User Signup",
    description="Universal signup endpoint that handles all user types with role-based routing",
    responses={
        201: {
            "description": "User registration successful",
            "content": {
                "application/json": {
                    "examples": {
                        "attorney": {
                            "summary": "Attorney Signup",
                            "value": {
                                "user": {
                                    "id": 1,
                                    "cognito_id": "mock_jane.doe@example.com",
                                    "user_type": "attorney",
                                    "primary_role": "attorney",
                                    "is_active": True,
                                    "created_at": "2023-01-01T00:00:00",
                                    "updated_at": "2023-01-01T00:00:00",
                                },
                                "attorney": {
                                    "id": 1,
                                    "name": "Jane Doe",
                                    "phone_number": "+15551234567",
                                    "email": "jane.doe@example.com",
                                    "zip_code": "12345",
                                    "state": "CA",
                                },
                                "access_token": "mock_token_1",
                                "token_type": "bearer",
                            },
                        },
                        "client_helper": {
                            "summary": "Client Helper Signup",
                            "value": {
                                "user": {
                                    "id": 2,
                                    "cognito_id": "mock_john.helper@example.com",
                                    "user_type": "client_helper",
                                    "primary_role": "client_helper",
                                    "is_active": True,
                                },
                                "client_profile": {
                                    "id": 1,
                                    "profile_name": "John Doe",
                                    "is_self": True,
                                    "first_name": "John",
                                    "last_name": "Doe",
                                },
                                "access_token": "mock_token_2",
                                "token_type": "bearer",
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "User with this email already exists or invalid role data",
            "content": {"application/json": {"example": {"detail": "A user with this email already exists"}}},
        },
        422: {"description": "Validation Error"},
    },
)
def unified_signup(
    signup_data: UnifiedSignupRequest,
    role_data: RoleSpecificData,
    db: Session = Depends(get_db),
):
    """
    Universal signup endpoint that handles all user types with role-based routing.

    This endpoint:
    1. Validates role and corresponding data
    2. Creates a User record with enhanced primary_role field
    3. Creates role-specific records (Attorney, ClientProfile, or Admin)
    4. Returns unified response with user and role-specific information
    5. Handles transaction rollback on errors to prevent orphaned records

    **Supported Roles:**
    - **attorney**: Requires attorney_data with professional information
    - **client_helper**: Requires client_profile_data with personal information
    - **admin**: Requires admin_data with administrative information

    **Returns:**
    - User account information with primary_role
    - Role-specific profile information
    - Mock authentication token (for testing environments)
    """
    try:
        # Validate role and corresponding data
        if signup_data.primary_role == "attorney" and not role_data.attorney_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Attorney data required for attorney role"
            )
        elif signup_data.primary_role == "client_helper" and not role_data.client_profile_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile data required for client_helper role"
            )
        elif signup_data.primary_role == "admin" and not role_data.admin_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin data required for admin role")

        # Check if user with this email already exists
        mock_cognito_id = f"mock_{signup_data.email}"
        existing_user = db.query(User).filter(User.cognito_id == mock_cognito_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        # Create User first
        db_user = User(
            cognito_id=mock_cognito_id,
            user_type=signup_data.primary_role,
            primary_role=signup_data.primary_role,
            is_active=True,
        )
        db.add(db_user)
        db.flush()

        # Role-specific record creation
        role_specific_response: Dict[str, Any] = {}

        if signup_data.primary_role == "attorney":
            attorney_data = role_data.attorney_data
            if not attorney_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attorney data is required")
            db_attorney = Attorney(
                name=attorney_data.name,
                phone_number=attorney_data.phone_number,
                email=attorney_data.email,
                zip_code=attorney_data.zip_code,
                state=attorney_data.state,
                user_id=db_user.id,
            )
            db.add(db_attorney)
            db.flush()
            role_specific_response["attorney"] = {
                "id": db_attorney.id,
                "name": db_attorney.name,
                "phone_number": db_attorney.phone_number,
                "email": db_attorney.email,
                "zip_code": db_attorney.zip_code,
                "state": db_attorney.state,
                "created_at": db_attorney.created_at,
                "updated_at": db_attorney.updated_at,
            }

        elif signup_data.primary_role == "client_helper":
            profile_data = role_data.client_profile_data
            if not profile_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client profile data is required")
            db_client_profile = ClientProfile(
                user_id=db_user.id,
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
            db.add(db_client_profile)
            db.flush()
            role_specific_response["client_profile"] = {
                "id": db_client_profile.id,
                "profile_name": db_client_profile.profile_name,
                "is_self": db_client_profile.is_self,
                "first_name": db_client_profile.first_name,
                "last_name": db_client_profile.last_name,
                "country_of_birth": db_client_profile.country_of_birth,
                "nationality": db_client_profile.nationality,
                "birth_date": db_client_profile.birth_date,
                "created_at": db_client_profile.created_at,
                "updated_at": db_client_profile.updated_at,
            }

        elif signup_data.primary_role == "admin":
            admin_data = role_data.admin_data
            if not admin_data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin data is required")
            db_admin = Admin(
                name=admin_data.name,
                email=admin_data.email,
                department=admin_data.department,
                role=admin_data.role,
                user_id=db_user.id,
            )
            db.add(db_admin)
            db.flush()
            role_specific_response["admin"] = {
                "id": db_admin.id,
                "name": db_admin.name,
                "email": db_admin.email,
                "department": db_admin.department,
                "role": db_admin.role,
                "created_at": db_admin.created_at,
                "updated_at": db_admin.updated_at,
            }

        # Commit transaction
        db.commit()
        db.refresh(db_user)

        # Create response
        user_response = UserResponse.model_validate(db_user)
        mock_token = f"mock_token_{db_user.id}"

        return UnifiedSignupResponse(
            user=user_response,
            **role_specific_response,
            access_token=mock_token,
            token_type=OAUTH_TOKEN_TYPE,
        )

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during unified signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during unified signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error.",
        )


@router.post(
    "/multi-profile",
    response_model=MultiProfileSignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Multi-Profile Client Signup",
    description="Create account with multiple client profiles for family helpers",
    responses={
        201: {
            "description": "Multi-profile registration successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": 3,
                            "cognito_id": "mock_family.helper@example.com",
                            "user_type": "client_helper",
                            "primary_role": "client_helper",
                            "is_active": True,
                        },
                        "client_profiles": [
                            {
                                "id": 2,
                                "profile_name": "Maria Rodriguez",
                                "is_self": True,
                                "first_name": "Maria",
                                "last_name": "Rodriguez",
                            },
                            {
                                "id": 3,
                                "profile_name": "My Son",
                                "is_self": False,
                                "first_name": "Carlos",
                                "last_name": "Rodriguez",
                            },
                        ],
                        "access_token": "mock_token_3",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {"description": "User with this email already exists"},
        422: {"description": "Validation Error"},
    },
)
def multi_profile_signup(
    signup_data: MultiProfileSignupRequest,
    db: Session = Depends(get_db),
):
    """
    Multi-profile signup endpoint for family helpers managing multiple client profiles.

    This endpoint:
    1. Creates a User record with client_helper role
    2. Creates multiple ClientProfile records linked to the user
    3. Optionally creates an Attorney record if attorney_data is provided
    4. Returns all created profiles in the response

    **Features:**
    - Support for multiple client profiles under one account
    - Each profile can be marked as "self" or "other person"
    - Profile names help identify each person (e.g., "My Son", "Maria Rodriguez")
    - Optional attorney capability for lawyers who also need legal help

    **Returns:**
    - User account information
    - Array of created client profiles
    - Optional attorney information
    - Mock authentication token
    """
    try:
        if len(signup_data.client_profiles) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="At least one client profile is required"
            )

        # Check if user with this email already exists
        mock_cognito_id = f"mock_{signup_data.email}"
        existing_user = db.query(User).filter(User.cognito_id == mock_cognito_id).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A user with this email already exists")

        # Create User record
        db_user = User(
            cognito_id=mock_cognito_id,
            user_type=signup_data.primary_role,
            primary_role=signup_data.primary_role,
            is_active=True,
        )
        db.add(db_user)
        db.flush()

        # Create multiple client profiles
        created_profiles = []
        for profile_data in signup_data.client_profiles:
            db_client_profile = ClientProfile(
                user_id=db_user.id,
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
            db.add(db_client_profile)
            db.flush()

            created_profiles.append(
                {
                    "id": db_client_profile.id,
                    "profile_name": db_client_profile.profile_name,
                    "is_self": db_client_profile.is_self,
                    "first_name": db_client_profile.first_name,
                    "last_name": db_client_profile.last_name,
                    "country_of_birth": db_client_profile.country_of_birth,
                    "birth_date": db_client_profile.birth_date,
                    "created_at": db_client_profile.created_at,
                    "updated_at": db_client_profile.updated_at,
                }
            )

        # Optional attorney record
        attorney_response = None
        if signup_data.attorney_data:
            attorney_data = signup_data.attorney_data
            db_attorney = Attorney(
                name=attorney_data.name,
                phone_number=attorney_data.phone_number,
                email=attorney_data.email,
                zip_code=attorney_data.zip_code,
                state=attorney_data.state,
                user_id=db_user.id,
            )
            db.add(db_attorney)
            db.flush()
            attorney_response = {
                "id": db_attorney.id,
                "name": db_attorney.name,
                "email": db_attorney.email,
                "created_at": db_attorney.created_at,
            }

        # Commit transaction
        db.commit()
        db.refresh(db_user)

        # Create response
        user_response = UserResponse.model_validate(db_user)
        mock_token = f"mock_token_{db_user.id}"

        return MultiProfileSignupResponse(
            user=user_response,
            client_profiles=created_profiles,
            attorney=attorney_response,
            access_token=mock_token,
            token_type=OAUTH_TOKEN_TYPE,
        )

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during multi-profile signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to data conflict.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during multi-profile signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error.",
        )
